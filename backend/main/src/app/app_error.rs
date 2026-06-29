use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("{0}")]
    Validation(String),
    #[error("{0}")]
    NotFound(String),
    #[error("{0}")]
    Conflict(String),
    #[error("{0}")]
    Unauthorized(String),
    #[error("{message}")]
    TooManyRequests {
        message: String,
        retry_after_seconds: u64,
    },
    #[error("Database error")]
    Database(#[from] sqlx::Error),
    #[error("Redis error")]
    Redis(#[from] redis::RedisError),
    #[error("{0}")]
    Internal(String),
}

pub type AppResult<T> = Result<T, AppError>;
