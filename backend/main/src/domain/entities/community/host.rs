#![allow(dead_code)]

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use sqlx::FromRow;
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct Host {
    pub id: Uuid,
    pub owner_id: Uuid,
    pub name: String,
    pub avatar: Option<String>,
    pub background: Option<String>,
    pub about: Option<String>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}
