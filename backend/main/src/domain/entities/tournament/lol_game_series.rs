#![allow(dead_code)]

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use sqlx::types::Json;
use uuid::Uuid;

use super::super::enums::Status;

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize, sqlx::Type)]
#[sqlx(type_name = "TEXT", rename_all = "lowercase")]
#[serde(rename_all = "lowercase")]
pub enum DraftType {
    Classic,
    Ironman,
    Fearless,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LolGame {
    pub team_blue: Uuid,
    pub team_red: Uuid,
    pub status: Status,
    pub winner: Option<Uuid>,
    pub draft: Option<Json<Value>>,
    pub finished: Option<DateTime<Utc>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LolGameSeries {
    pub id: Uuid,
    pub tournament_id: Uuid,
    pub best_of: i32,
    pub status: Status,
    pub draft_type: DraftType,
    pub team1: Uuid,
    pub team2: Uuid,
    pub winner: Option<Uuid>,
    pub forbidden_champions: Vec<i32>,
    pub games: Option<Vec<LolGame>>,
}
