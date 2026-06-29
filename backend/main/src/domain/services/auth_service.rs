use chrono::{Duration, Utc};
use rand::{Rng, rng};
use sha2::{Digest, Sha256};
use uuid::Uuid;

use crate::{
    app::app_error::{AppError, AppResult},
    domain::entities::{
        auth::{AttemptWindow, AuthSession, LoginStartResult, StoredLoginChallenge},
        community::user::User,
    },
    infra::{MailSender, RedisAuthChallengeStore, UserRepository},
};

#[derive(Debug, Clone)]
pub struct FinishLoginCommand {
    pub email: String,
    pub challenge_id: Uuid,
    pub challenge: String,
    pub code: String,
}

#[derive(Clone)]
pub struct AuthService {
    user_repo: UserRepository,
    challenge_store: RedisAuthChallengeStore,
    mail_sender: MailSender,
    challenge_secret: String,
}

impl AuthService {
    pub fn new(
        user_repo: UserRepository,
        challenge_store: RedisAuthChallengeStore,
        mail_sender: MailSender,
        challenge_secret: String,
    ) -> Self {
        Self {
            user_repo,
            challenge_store,
            mail_sender,
            challenge_secret,
        }
    }

    pub async fn start_login(&self, email: String) -> AppResult<LoginStartResult> {
        let email = normalize_email(email)?;
        self.challenge_store.ensure_login_available(&email).await?;

        let user = self
            .user_repo
            .get_user_by_email(&email)
            .await?
            .ok_or_else(|| AppError::NotFound("User with this email was not found".to_string()))?;

        let challenge_id = Uuid::now_v7();
        let public_challenge = format!("akiora-login-{}", Uuid::new_v4());
        let verification_code = format!("{:06}", rng().random_range(0..1_000_000));
        let expires_at = Utc::now() + Duration::minutes(10);

        let stored = StoredLoginChallenge {
            challenge_id,
            email: email.clone(),
            challenge: public_challenge.clone(),
            code_hash: hash_code(
                &self.challenge_secret,
                challenge_id,
                &email,
                &verification_code,
            ),
            expires_at,
        };

        self.challenge_store.replace_challenge(&stored).await?;
        self.send_login_email(&user, &verification_code, expires_at)
            .await?;

        Ok(LoginStartResult {
            challenge_id,
            challenge: public_challenge,
            expires_at,
            attempts_left: self.challenge_store.max_attempts(),
        })
    }

    pub async fn finish_login(&self, command: FinishLoginCommand) -> AppResult<AuthSession> {
        let email = normalize_email(command.email)?;
        self.challenge_store.ensure_login_available(&email).await?;

        let Some(stored) = self
            .challenge_store
            .get_challenge(command.challenge_id)
            .await?
        else {
            let attempt_window = self.challenge_store.record_failed_attempt(&email).await?;
            return Err(invalid_challenge_error(attempt_window));
        };

        if stored.email != email || stored.challenge != command.challenge {
            let attempt_window = self.challenge_store.record_failed_attempt(&email).await?;
            return Err(invalid_challenge_error(attempt_window));
        }

        if stored.expires_at < Utc::now() {
            self.challenge_store
                .clear_challenge(command.challenge_id, &email)
                .await?;
            let attempt_window = self.challenge_store.record_failed_attempt(&email).await?;
            return Err(invalid_challenge_error(attempt_window));
        }

        let provided_hash = hash_code(
            &self.challenge_secret,
            command.challenge_id,
            &email,
            command.code.trim(),
        );

        if provided_hash != stored.code_hash {
            let attempt_window = self.challenge_store.record_failed_attempt(&email).await?;
            return Err(invalid_code_error(attempt_window));
        }

        self.challenge_store
            .clear_challenge(command.challenge_id, &email)
            .await?;
        self.challenge_store.clear_failed_attempts(&email).await?;

        let user = self
            .user_repo
            .get_user_by_email(&email)
            .await?
            .ok_or_else(|| AppError::NotFound("User with this email was not found".to_string()))?;

        Ok(AuthSession {
            user,
            authenticated_at: Utc::now(),
        })
    }

    async fn send_login_email(
        &self,
        user: &User,
        verification_code: &str,
        expires_at: chrono::DateTime<Utc>,
    ) -> AppResult<()> {
        let body = format!(
            "Use this code to finish your Akiora login: {verification_code}\nThe code expires at {}.",
            expires_at.to_rfc3339()
        );

        self.mail_sender
            .send_email(&user.email, &user.name, "Akiora login code", &body)
            .await
            .map_err(|error| {
                AppError::Internal(format!(
                    "Failed to send login email to {}: {error}",
                    user.email
                ))
            })
    }
}

fn normalize_email(email: String) -> AppResult<String> {
    let normalized = email.trim().to_lowercase();
    if normalized.is_empty() {
        return Err(AppError::Validation("Email must not be empty".to_string()));
    }
    Ok(normalized)
}

fn hash_code(secret: &str, challenge_id: Uuid, email: &str, code: &str) -> String {
    let mut hasher = Sha256::new();
    hasher.update(secret.as_bytes());
    hasher.update(b":");
    hasher.update(challenge_id.as_bytes());
    hasher.update(b":");
    hasher.update(email.as_bytes());
    hasher.update(b":");
    hasher.update(code.as_bytes());
    format!("{:x}", hasher.finalize())
}

fn invalid_challenge_error(attempt_window: AttemptWindow) -> AppError {
    if let Some(retry_after_seconds) = attempt_window.retry_after_seconds {
        return AppError::TooManyRequests {
            message: "Too many failed login attempts for this email. Try again later.".to_string(),
            retry_after_seconds,
        };
    }

    AppError::Unauthorized(format!(
        "Login challenge is invalid or expired. Attempts left: {}",
        attempt_window.remaining_attempts
    ))
}

fn invalid_code_error(attempt_window: AttemptWindow) -> AppError {
    if let Some(retry_after_seconds) = attempt_window.retry_after_seconds {
        return AppError::TooManyRequests {
            message: "Too many failed login attempts for this email. Try again later.".to_string(),
            retry_after_seconds,
        };
    }

    AppError::Unauthorized(format!(
        "Verification code is invalid. Attempts left: {}",
        attempt_window.remaining_attempts
    ))
}
