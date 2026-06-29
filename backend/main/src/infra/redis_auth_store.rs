use std::time::Duration;

use redis::AsyncCommands;
use uuid::Uuid;

use crate::{
    app::app_error::{AppError, AppResult},
    domain::entities::auth::{AttemptWindow, StoredLoginChallenge},
};

const CHALLENGE_TTL_SECONDS: u64 = 10 * 60;
const LOCK_TTL_SECONDS: u64 = 5 * 60;
const MAX_ATTEMPTS: u32 = 3;

#[derive(Clone)]
pub struct RedisAuthChallengeStore {
    client: redis::Client,
}

impl RedisAuthChallengeStore {
    pub fn new(client: redis::Client) -> Self {
        Self { client }
    }

    pub fn max_attempts(&self) -> u32 {
        MAX_ATTEMPTS
    }

    pub async fn ensure_login_available(&self, email: &str) -> AppResult<()> {
        let mut connection = self.client.get_multiplexed_async_connection().await?;
        let lock_key = lock_key(email);
        let is_locked: bool = connection.exists(&lock_key).await?;

        if !is_locked {
            return Ok(());
        }

        let retry_after_seconds = ttl_to_retry_after(connection.ttl(&lock_key).await?);
        Err(AppError::TooManyRequests {
            message: "Too many failed login attempts for this email. Try again later.".to_string(),
            retry_after_seconds,
        })
    }

    pub async fn replace_challenge(&self, challenge: &StoredLoginChallenge) -> AppResult<()> {
        let mut connection = self.client.get_multiplexed_async_connection().await?;
        let active_key = active_challenge_key(&challenge.email);
        let current_challenge_id: Option<String> = connection.get(&active_key).await?;
        if let Some(current_challenge_id) = current_challenge_id {
            let _: () = connection.del(challenge_key(&current_challenge_id)).await?;
        }

        let payload = serde_json::to_string(challenge).map_err(|error| {
            AppError::Internal(format!("Failed to serialize login challenge: {error}"))
        })?;
        let ttl = challenge_ttl(challenge);

        let _: () = connection
            .set_ex(challenge_key(challenge.challenge_id), payload, ttl)
            .await?;
        let _: () = connection
            .set_ex(active_key, challenge.challenge_id.to_string(), ttl)
            .await?;
        Ok(())
    }

    pub async fn get_challenge(
        &self,
        challenge_id: Uuid,
    ) -> AppResult<Option<StoredLoginChallenge>> {
        let mut connection = self.client.get_multiplexed_async_connection().await?;
        let payload: Option<String> = connection.get(challenge_key(challenge_id)).await?;
        payload
            .map(|value| {
                serde_json::from_str::<StoredLoginChallenge>(&value).map_err(|error| {
                    AppError::Internal(format!("Failed to deserialize login challenge: {error}"))
                })
            })
            .transpose()
    }

    pub async fn clear_challenge(&self, challenge_id: Uuid, email: &str) -> AppResult<()> {
        let mut connection = self.client.get_multiplexed_async_connection().await?;
        let _: () = connection.del(challenge_key(challenge_id)).await?;
        let _: () = connection.del(active_challenge_key(email)).await?;
        Ok(())
    }

    pub async fn record_failed_attempt(&self, email: &str) -> AppResult<AttemptWindow> {
        let mut connection = self.client.get_multiplexed_async_connection().await?;
        let attempts_key = attempts_key(email);
        let attempts: u32 = connection.incr(&attempts_key, 1).await?;
        if attempts == 1 {
            let _: bool = connection
                .expire(&attempts_key, LOCK_TTL_SECONDS as i64)
                .await?;
        }

        if attempts >= MAX_ATTEMPTS {
            let lock_key = lock_key(email);
            let _: () = connection.set_ex(&lock_key, "1", LOCK_TTL_SECONDS).await?;
            return Ok(AttemptWindow {
                remaining_attempts: 0,
                retry_after_seconds: Some(LOCK_TTL_SECONDS),
            });
        }

        Ok(AttemptWindow {
            remaining_attempts: MAX_ATTEMPTS - attempts,
            retry_after_seconds: None,
        })
    }

    pub async fn clear_failed_attempts(&self, email: &str) -> AppResult<()> {
        let mut connection = self.client.get_multiplexed_async_connection().await?;
        let _: () = connection.del(attempts_key(email)).await?;
        let _: () = connection.del(lock_key(email)).await?;
        Ok(())
    }
}

fn attempts_key(email: &str) -> String {
    format!("auth:login:attempts:{email}")
}

fn lock_key(email: &str) -> String {
    format!("auth:login:lock:{email}")
}

fn active_challenge_key(email: &str) -> String {
    format!("auth:login:active:{email}")
}

fn challenge_key(challenge_id: impl ToString) -> String {
    format!("auth:login:challenge:{}", challenge_id.to_string())
}

fn ttl_to_retry_after(ttl: i64) -> u64 {
    match ttl {
        positive if positive > 0 => positive as u64,
        _ => LOCK_TTL_SECONDS,
    }
}

fn challenge_ttl(challenge: &StoredLoginChallenge) -> u64 {
    let ttl = (challenge.expires_at - chrono::Utc::now())
        .to_std()
        .unwrap_or(Duration::from_secs(CHALLENGE_TTL_SECONDS))
        .as_secs();
    ttl.max(1)
}
