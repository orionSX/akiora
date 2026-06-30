use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use serde_json::Value;

use uuid::Uuid;

use super::super::enums::GameStatus;
use crate::{domain::enums::GameDraftType, utils::serializers::serialize_opt_uuid};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LolGame {
    #[serde(serialize_with = "uuid::serde::hyphenated::serialize")]
    pub team_blue: Uuid,
    #[serde(serialize_with = "uuid::serde::hyphenated::serialize")]
    pub team_red: Uuid,
    pub status: GameStatus,
    #[serde(serialize_with = "serialize_opt_uuid")]
    pub winner: Option<Uuid>,
    pub draft: Option<Value>,
    #[serde(with = "chrono::serde::ts_milliseconds_option")]
    pub finished: Option<DateTime<Utc>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Match {
    #[serde(rename = "_id", serialize_with = "uuid::serde::hyphenated::serialize")]
    pub id: Uuid,
    #[serde(serialize_with = "uuid::serde::hyphenated::serialize")]
    pub tournament_id: Uuid,
    pub best_of: i32,
    pub status: GameStatus,
    pub draft_type: GameDraftType,
    #[serde(serialize_with = "uuid::serde::hyphenated::serialize")]
    pub team1: Uuid,
    #[serde(serialize_with = "uuid::serde::hyphenated::serialize")]
    pub team2: Uuid,
    #[serde(serialize_with = "serialize_opt_uuid")]
    pub winner: Option<Uuid>,
    pub forbidden_champions: Vec<i32>,
    pub games: Option<Vec<LolGame>>,
}
