use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use serde_with::{DisplayFromStr, serde_as};
use uuid::Uuid;

use crate::domain::enums::{
    BracketType, CommunityStatus, GameDraftType, GameStatus, PlayerDraftType, Role, TournamentType,
};

#[serde_as]
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DraftPlayerRequest {
    #[serde(serialize_with = "uuid::serde::hyphenated::serialize")]
    pub user_id: Uuid,
    #[serde(serialize_with = "uuid::serde::hyphenated::serialize")]
    pub tournament_id: Uuid,
    pub main_role: Role,
    pub secondary_role: Option<Role>,
    pub status: CommunityStatus,
    #[serde(with = "chrono::serde::ts_milliseconds")]
    pub created_at: DateTime<Utc>,
}

#[serde_as]
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DraftPlayer {
    #[serde(serialize_with = "uuid::serde::hyphenated::serialize")]
    pub user_id: Uuid,
    #[serde(serialize_with = "uuid::serde::hyphenated::serialize")]
    pub tournament_id: Uuid,
    pub main_role: Role,
    pub secondary_role: Option<Role>,
    pub is_captain: bool,
    #[serde(with = "chrono::serde::ts_milliseconds")]
    pub created_at: DateTime<Utc>,
}

#[serde_as]
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DraftTournament {
    #[serde(rename = "_id", serialize_with = "uuid::serde::hyphenated::serialize")]
    pub id: Uuid,
    pub draft_pool: Vec<DraftPlayer>,
    pub avatar: Option<String>,
   
    pub status: GameStatus,
    pub about: Option<String>,
    pub prizepool: Option<String>,
    #[serde(with = "chrono::serde::ts_milliseconds")]
    pub created_at: DateTime<Utc>,
    #[serde(with = "chrono::serde::ts_milliseconds")]
    pub starts_at: DateTime<Utc>,
    #[serde(with = "chrono::serde::ts_milliseconds")]
    pub draft_starts_at: DateTime<Utc>,
}

#[serde_as]
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TournamentSettings {
    pub tournament_type: TournamentType,
    pub bracket_type: BracketType,
    pub game_draft_type: GameDraftType,
    pub player_draft_type: Option<PlayerDraftType>,
    pub team_size: i32,
}
