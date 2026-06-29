use actix_identity::Identity;
use actix_session::SessionExt;
use actix_web::{HttpMessage, HttpRequest, HttpResponse, web};
use uuid::Uuid;
use validator::Validate;

use crate::{
    app::{AppState, app_error::AppResult},
    domain::services::auth_service::FinishLoginCommand,
};

#[derive(Debug, serde::Deserialize, Validate)]
pub(crate) struct StartLoginRequest {
    #[validate(email, length(max = 255))]
    email: String,
}

#[derive(Debug, serde::Deserialize, Validate)]
pub(crate) struct FinishLoginRequest {
    #[validate(email, length(max = 255))]
    email: String,
    challenge_id: Uuid,
    #[validate(length(min = 8, max = 128))]
    challenge: String,
    #[validate(length(min = 6, max = 6))]
    code: String,
}

pub async fn start_login(
    state: web::Data<AppState>,
    payload: web::Json<StartLoginRequest>,
) -> AppResult<HttpResponse> {
    payload.validate().map_err(validation_error)?;

    let result = state
        .auth_service
        .start_login(payload.email.clone())
        .await?;

    Ok(HttpResponse::Ok().json(result))
}

pub async fn me(identity: Option<Identity>, state: web::Data<AppState>) -> AppResult<HttpResponse> {
    let identity = identity.ok_or_else(|| {
        crate::app::app_error::AppError::Unauthorized("Authentication required".to_string())
    })?;
    let user_id = identity.id().map_err(|error| {
        crate::app::app_error::AppError::Unauthorized(format!(
            "Invalid authenticated identity: {error}"
        ))
    })?;
    let user_id = Uuid::parse_str(&user_id).map_err(|error| {
        crate::app::app_error::AppError::Unauthorized(format!(
            "Invalid authenticated user id in session: {error}"
        ))
    })?;

    let user = state.user_service.get_user(user_id).await?;
    Ok(HttpResponse::Ok().json(user))
}

pub async fn finish_login(
    state: web::Data<AppState>,
    request: HttpRequest,
    payload: web::Json<FinishLoginRequest>,
) -> AppResult<HttpResponse> {
    payload.validate().map_err(validation_error)?;

    let auth_session = state
        .auth_service
        .finish_login(FinishLoginCommand {
            email: payload.email.clone(),
            challenge_id: payload.challenge_id,
            challenge: payload.challenge.clone(),
            code: payload.code.clone(),
        })
        .await?;

    request.get_session().renew();
    Identity::login(&request.extensions(), auth_session.user.id.to_string()).map_err(|error| {
        crate::app::app_error::AppError::Internal(format!(
            "Failed to persist authenticated identity: {error}"
        ))
    })?;

    Ok(HttpResponse::Ok().json(auth_session))
}

fn validation_error(error: validator::ValidationErrors) -> crate::app::app_error::AppError {
    crate::app::app_error::AppError::Validation(error.to_string())
}
