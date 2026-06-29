use actix_web::{HttpResponse, web};
use uuid::Uuid;
use validator::Validate;

use crate::{
    app::{
        AppState,
        app_error::{AppError, AppResult},
    },
    domain::services::user_service::{CreateUserCommand, UpdateUserCommand},
};

#[derive(Debug, serde::Deserialize, Validate)]
pub(crate) struct CreateUserRequest {
    #[validate(length(min = 1, max = 32))]
    name: String,
    #[validate(email, length(max = 255))]
    email: String,
    #[validate(length(max = 2048))]
    avatar: Option<String>,
    #[validate(length(max = 4096))]
    about: Option<String>,
}

#[derive(Debug, serde::Deserialize, Validate)]
pub(crate) struct UpdateUserRequest {
    #[validate(length(min = 1, max = 32))]
    name: Option<String>,
    #[validate(email, length(max = 255))]
    email: Option<String>,
    #[validate(length(max = 2048))]
    avatar: Option<String>,
    #[validate(length(max = 4096))]
    about: Option<String>,
    clear_avatar: Option<bool>,
    clear_about: Option<bool>,
}

#[derive(Debug, serde::Deserialize)]
pub(crate) struct UserPath {
    user_id: Uuid,
}

pub async fn create_user(
    state: web::Data<AppState>,
    payload: web::Json<CreateUserRequest>,
) -> AppResult<HttpResponse> {
    payload.validate().map_err(validation_error)?;

    let user = state
        .user_service
        .create_user(CreateUserCommand {
            name: payload.name.clone(),
            email: payload.email.clone(),
            avatar: payload.avatar.clone(),
            about: payload.about.clone(),
        })
        .await?;

    Ok(HttpResponse::Created().json(user))
}

pub async fn list_users(state: web::Data<AppState>) -> AppResult<HttpResponse> {
    let users = state.user_service.list_users().await?;
    Ok(HttpResponse::Ok().json(users))
}

pub async fn get_user(
    state: web::Data<AppState>,
    path: web::Path<UserPath>,
) -> AppResult<HttpResponse> {
    let user = state.user_service.get_user(path.user_id).await?;
    Ok(HttpResponse::Ok().json(user))
}

pub async fn update_user(
    state: web::Data<AppState>,
    path: web::Path<UserPath>,
    payload: web::Json<UpdateUserRequest>,
) -> AppResult<HttpResponse> {
    payload.validate().map_err(validation_error)?;

    let avatar = match (
        payload.clear_avatar.unwrap_or(false),
        payload.avatar.clone(),
    ) {
        (true, _) => Some(None),
        (false, Some(value)) => Some(Some(value)),
        (false, None) => None,
    };

    let about = match (payload.clear_about.unwrap_or(false), payload.about.clone()) {
        (true, _) => Some(None),
        (false, Some(value)) => Some(Some(value)),
        (false, None) => None,
    };

    let user = state
        .user_service
        .update_user(
            path.user_id,
            UpdateUserCommand {
                name: payload.name.clone(),
                email: payload.email.clone(),
                avatar,
                about,
            },
        )
        .await?;

    Ok(HttpResponse::Ok().json(user))
}

pub async fn delete_user(
    state: web::Data<AppState>,
    path: web::Path<UserPath>,
) -> AppResult<HttpResponse> {
    state.user_service.delete_user(path.user_id).await?;
    Ok(HttpResponse::NoContent().finish())
}

fn validation_error(error: validator::ValidationErrors) -> AppError {
    AppError::Validation(error.to_string())
}
