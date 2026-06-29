use anyhow::{Context, Result};
use redis::Client as RedisClient;
use sqlx::{Postgres, postgres::PgPoolOptions};
use tracing::info;

pub async fn get_connection_pool() -> Result<sqlx::Pool<Postgres>> {
    let database_url = std::env::var("DATABASE_URL").expect("DATABASE_URL must be set");
    let pool = PgPoolOptions::new()
        .max_connections(5)
        .connect(&database_url)
        .await?;
    sqlx::migrate!("./migrations").run(&pool).await?;
    info!("Database connection pool established successfully");
    Ok(pool)
}

pub fn get_redis_client() -> Result<RedisClient> {
    let redis_url =
        std::env::var("REDIS_URL").unwrap_or_else(|_| "redis://127.0.0.1:6379/".to_string());
    let client = RedisClient::open(redis_url).context("Failed to create Redis client")?;
    Ok(client)
}
