use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use sqlx::FromRow;
use uuid::Uuid;

use super::super::enums::BracketType;

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct TournamentTeam {
    pub id: Uuid,
    pub tournament_id: Uuid,
    pub name: String,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct PersistedBracket {
    pub tournament_id: Uuid,
    pub body: Value,
    pub bracket_type: BracketType,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GeneratedBracket {
    pub tournament_id: Uuid,
    pub bracket_type: BracketType,
    pub generated_at: DateTime<Utc>,
    pub participants: Vec<BracketParticipant>,
    pub stages: Vec<BracketStage>,
    pub metadata: BracketMetadata,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BracketParticipant {
    pub team_id: Uuid,
    pub team_name: String,
    pub seed: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BracketMetadata {
    pub rounds: usize,
    pub bracket_size: Option<usize>,
    pub grand_final_reset: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub pairing_strategy: Option<String>,
    pub notes: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BracketStage {
    pub id: String,
    pub label: String,
    pub round: usize,
    pub kind: StageKind,
    pub matches: Vec<BracketMatch>,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum StageKind {
    Winners,
    Losers,
    GrandFinal,
    RoundRobin,
    Swiss,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BracketMatch {
    pub id: String,
    pub label: String,
    pub round: usize,
    pub best_of: u32,
    pub slots: Vec<MatchSlot>,
    pub advances_to: Vec<MatchAdvance>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MatchSlot {
    pub position: u8,
    pub seed: Option<usize>,
    pub team_id: Option<Uuid>,
    pub team_name: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub source_match_id: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub source_outcome: Option<String>,
    pub is_bye: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MatchAdvance {
    pub outcome: String,
    pub target_match_id: String,
    pub target_slot: u8,
}
