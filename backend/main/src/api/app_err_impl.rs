use actix_web::{
    HttpResponse, ResponseError,
    http::{StatusCode, header},
};
use serde::Serialize;

use crate::app::app_error::AppError;

#[derive(Debug, Serialize)]
struct ErrorEnvelope {
    error: ErrorPayload,
}

#[derive(Debug, Serialize)]
struct ErrorPayload {
    code: &'static str,
    message: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    retry_after_seconds: Option<u64>,
}

impl ResponseError for AppError {
    fn status_code(&self) -> StatusCode {
        match self {
            AppError::Validation(_) => StatusCode::BAD_REQUEST,
            AppError::Unauthorized(_) => StatusCode::UNAUTHORIZED,
            AppError::NotFound(_) => StatusCode::NOT_FOUND,
            AppError::Conflict(_) => StatusCode::CONFLICT,
            AppError::TooManyRequests { .. } => StatusCode::TOO_MANY_REQUESTS,
            AppError::Database(_) | AppError::Internal(_) | AppError::Redis(_) => {
                StatusCode::INTERNAL_SERVER_ERROR
            }
        }
    }

    fn error_response(&self) -> HttpResponse {
        let payload = match self {
            AppError::Validation(message) => ErrorPayload {
                code: "validation_error",
                message: message.clone(),
                retry_after_seconds: None,
            },
            AppError::Unauthorized(message) => ErrorPayload {
                code: "unauthorized",
                message: message.clone(),
                retry_after_seconds: None,
            },
            AppError::NotFound(message) => ErrorPayload {
                code: "not_found",
                message: message.clone(),
                retry_after_seconds: None,
            },
            AppError::Conflict(message) => ErrorPayload {
                code: "conflict",
                message: message.clone(),
                retry_after_seconds: None,
            },
            AppError::TooManyRequests {
                message,
                retry_after_seconds,
            } => ErrorPayload {
                code: "too_many_requests",
                message: message.clone(),
                retry_after_seconds: Some(*retry_after_seconds),
            },
            AppError::Database(_) => ErrorPayload {
                code: "database_error",
                message: "Database request failed".to_string(),
                retry_after_seconds: None,
            },
            AppError::Redis(_) => ErrorPayload {
                code: "cache_error",
                message: "Redis request failed".to_string(),
                retry_after_seconds: None,
            },
            AppError::Internal(message) => ErrorPayload {
                code: "internal_error",
                message: message.clone(),
                retry_after_seconds: None,
            },
        };

        let mut response = HttpResponse::build(self.status_code());
        if let AppError::TooManyRequests {
            retry_after_seconds,
            ..
        } = self
        {
            response.insert_header((header::RETRY_AFTER, retry_after_seconds.to_string()));
        }

        response.json(ErrorEnvelope { error: payload })
    }
}
