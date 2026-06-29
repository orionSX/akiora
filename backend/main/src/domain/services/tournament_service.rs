use serde_json::to_value;
use uuid::Uuid;

use crate::{
    app::app_error::{AppError, AppResult},
    domain::entities::{enums::BracketType, tournament::tournament::PersistedBracket},
    infra::TournamentRepository,
};

use super::bracket_service::BracketService;

#[derive(Debug, Clone, Copy)]
pub struct GenerateBracketCommand {
    pub tournament_id: Uuid,
    pub bracket_type: BracketType,
}

#[derive(Clone)]
pub struct TournamentService {
    tournament_repo: TournamentRepository,
    bracket_service: BracketService,
}

impl TournamentService {
    pub fn new(tournament_repo: TournamentRepository, bracket_service: BracketService) -> Self {
        Self {
            tournament_repo,
            bracket_service,
        }
    }

    pub async fn get_bracket(&self, tournament_id: Uuid) -> AppResult<PersistedBracket> {
        self.tournament_repo
            .get_bracket(tournament_id)
            .await?
            .ok_or_else(|| {
                AppError::NotFound("Bracket was not generated for this tournament".to_string())
            })
    }

    pub async fn generate_bracket(
        &self,
        command: GenerateBracketCommand,
    ) -> AppResult<PersistedBracket> {
        let exists = self
            .tournament_repo
            .tournament_exists(command.tournament_id)
            .await?;
        if !exists {
            return Err(AppError::NotFound("Tournament was not found".to_string()));
        }

        let teams = self
            .tournament_repo
            .list_teams(command.tournament_id)
            .await?;
        let bracket =
            self.bracket_service
                .generate(command.tournament_id, command.bracket_type, teams)?;

        self.tournament_repo
            .upsert_bracket(
                command.tournament_id,
                command.bracket_type,
                to_value(bracket).map_err(|error| {
                    AppError::Internal(format!("Failed to serialize generated bracket: {error}"))
                })?,
            )
            .await
    }
}
