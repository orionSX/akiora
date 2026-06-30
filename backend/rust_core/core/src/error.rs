use mongodb::error::Error as MongoError;
use redis::RedisError;
use std::env::VarError;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum CoreError {
    #[error("MongoDB error: {0}")]
    Mongo(#[from] MongoError),

    #[error("Redis error: {0}")]
    Redis(#[from] RedisError),

    #[error("Environment variable error: {0}")]
    Env(#[from] VarError),
}

pub type CoreResult<T> = Result<T, CoreError>;
