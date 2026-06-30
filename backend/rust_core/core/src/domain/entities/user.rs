use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct User {
    #[serde(rename = "_id", serialize_with = "uuid::serde::hyphenated::serialize")]
    pub id: Uuid,
    pub name: String,
    pub email: String,
    pub avatar: Option<String>,
    pub about: Option<String>,
    #[serde(with = "chrono::serde::ts_milliseconds")]
    pub created_at: DateTime<Utc>,
    #[serde(with = "chrono::serde::ts_milliseconds")]
    pub updated_at: DateTime<Utc>,
}

impl User {
    fn create(email: &str) -> Self {
        let time_now = chrono::Utc::now();
        Self {
            id: uuid::Uuid::now_v7(),
            name: email.into(),
            email: email.into(),
            avatar: None,
            about: None,
            created_at: time_now,
            updated_at: time_now,
        }
    }
}
