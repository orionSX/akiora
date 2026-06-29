use uuid::Uuid;

use crate::{
    app::app_error::{AppError, AppResult},
    domain::entities::community::user::{CreateUser, UpdateUser, User},
    infra::UserRepository,
};

#[derive(Debug, Clone)]
pub struct CreateUserCommand {
    pub name: String,
    pub email: String,
    pub avatar: Option<String>,
    pub about: Option<String>,
}

#[derive(Debug, Clone, Default)]
pub struct UpdateUserCommand {
    pub name: Option<String>,
    pub email: Option<String>,
    pub avatar: Option<Option<String>>,
    pub about: Option<Option<String>>,
}

#[derive(Clone)]
pub struct UserService {
    user_repo: UserRepository,
}

impl UserService {
    pub fn new(user_repo: UserRepository) -> Self {
        Self { user_repo }
    }

    pub async fn create_user(&self, command: CreateUserCommand) -> AppResult<User> {
        let user = CreateUser {
            name: normalize_name(command.name)?,
            email: normalize_email(command.email)?,
            avatar: sanitize_optional_text(command.avatar),
            about: sanitize_optional_text(command.about),
        };

        self.user_repo
            .create_user(user)
            .await
            .map_err(map_user_write_error)
    }

    pub async fn list_users(&self) -> AppResult<Vec<User>> {
        self.user_repo.list_users().await
    }

    pub async fn get_user(&self, user_id: Uuid) -> AppResult<User> {
        self.user_repo
            .get_user_by_id(user_id)
            .await?
            .ok_or_else(|| AppError::NotFound("User was not found".to_string()))
    }

    pub async fn update_user(&self, user_id: Uuid, command: UpdateUserCommand) -> AppResult<User> {
        if command.name.is_none()
            && command.email.is_none()
            && command.avatar.is_none()
            && command.about.is_none()
        {
            return Err(AppError::Validation(
                "At least one user field must be provided for update".to_string(),
            ));
        }

        let update = UpdateUser {
            name: command.name.map(normalize_name).transpose()?,
            email: command.email.map(normalize_email).transpose()?,
            avatar: command.avatar.map(|value| value.map(sanitize_text)),
            about: command.about.map(|value| value.map(sanitize_text)),
        };

        self.user_repo
            .update_user(user_id, update)
            .await
            .map_err(map_user_write_error)?
            .ok_or_else(|| AppError::NotFound("User was not found".to_string()))
    }

    pub async fn delete_user(&self, user_id: Uuid) -> AppResult<()> {
        let deleted = self.user_repo.delete_user(user_id).await?;
        if !deleted {
            return Err(AppError::NotFound("User was not found".to_string()));
        }

        Ok(())
    }
}

fn normalize_name(name: String) -> AppResult<String> {
    let trimmed = name.trim();
    if trimmed.is_empty() {
        return Err(AppError::Validation(
            "User name must not be empty".to_string(),
        ));
    }
    if trimmed.len() > 32 {
        return Err(AppError::Validation(
            "User name must not exceed 32 characters".to_string(),
        ));
    }

    Ok(trimmed.to_string())
}

fn normalize_email(email: String) -> AppResult<String> {
    let normalized = email.trim().to_lowercase();
    if normalized.is_empty() {
        return Err(AppError::Validation("Email must not be empty".to_string()));
    }
    Ok(normalized)
}

fn sanitize_optional_text(value: Option<String>) -> Option<String> {
    value.map(sanitize_text).filter(|text| !text.is_empty())
}

fn sanitize_text(value: String) -> String {
    value.trim().to_string()
}

fn map_user_write_error(error: AppError) -> AppError {
    match error {
        AppError::Database(sqlx_error) if is_unique_violation(&sqlx_error) => {
            AppError::Conflict("User with this email already exists".to_string())
        }
        other => other,
    }
}

fn is_unique_violation(error: &sqlx::Error) -> bool {
    error
        .as_database_error()
        .and_then(|database_error| database_error.code())
        .is_some_and(|code| code == "23505")
}
