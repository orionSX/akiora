use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

use uuid::Uuid;

use crate::domain::enums::HostStatus;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Host {
    #[serde(rename = "_id", serialize_with = "uuid::serde::hyphenated::serialize")]
    pub id: Uuid,
    #[serde(serialize_with = "uuid::serde::hyphenated::serialize")]
    pub owner_id: Uuid,
    pub name: String,
    pub avatar: Option<String>,
    pub status:HostStatus,
    pub background: Option<String>,
    pub about: Option<String>,
    #[serde(with = "chrono::serde::ts_milliseconds")]
    pub created_at: DateTime<Utc>,
    #[serde(with = "chrono::serde::ts_milliseconds")]
    pub updated_at: DateTime<Utc>,
}

impl Host {
    fn create(owner_id:Uuid,name:&str) -> Self {
        let time_now = chrono::Utc::now();
        Self {
            id: uuid::Uuid::now_v7(),
            owner_id,
            name: name.into(),
            avatar: None,
            status: HostStatus::Pending,
            background: None,
            about: None,
            created_at: time_now,
            updated_at: time_now,
        }
    }
}
