use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

use crate::domain::entities::community::user::User;

#[derive(Debug, Clone, Serialize)]
pub struct LoginStartResult {
    pub challenge_id: Uuid,
    pub challenge: String,
    pub expires_at: DateTime<Utc>,
    pub attempts_left: u32,
}

#[derive(Debug, Clone, Serialize)]
pub struct AuthSession {
    pub user: User,
    pub authenticated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StoredLoginChallenge {
    pub challenge_id: Uuid,
    pub email: String,
    pub challenge: String,
    pub code_hash: String,
    pub expires_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Copy)]
pub struct AttemptWindow {
    pub remaining_attempts: u32,
    pub retry_after_seconds: Option<u64>,
}
