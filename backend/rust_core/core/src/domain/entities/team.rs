use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use serde_with::{DisplayFromStr, serde_as};
use uuid::Uuid;

#[serde_as]
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Team {
    #[serde(rename = "_id", serialize_with = "uuid::serde::hyphenated::serialize")]
    pub id: Uuid,
    #[serde(serialize_with = "uuid::serde::hyphenated::serialize")]
    pub captain_id: Uuid,
    #[serde(serialize_with = "uuid::serde::hyphenated::serialize")]
    pub drafter_id: Uuid,
    #[serde_as(as = "Vec<DisplayFromStr>")]
    pub user_ids: Vec<Uuid>,
    pub avatar: Option<String>,
    #[serde(with = "chrono::serde::ts_milliseconds")]
    pub created_at: DateTime<Utc>,
    #[serde(with = "chrono::serde::ts_milliseconds")]
    pub updated_at: DateTime<Utc>,
}
