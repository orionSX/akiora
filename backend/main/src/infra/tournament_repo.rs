use serde_json::Value;
use sqlx::{Pool, Postgres, query_as, query_scalar};
use uuid::Uuid;

use crate::{
    app::app_error::AppResult,
    domain::entities::{
        enums::BracketType,
        tournament::tournament::{PersistedBracket, TournamentTeam},
    },
};

#[derive(Clone)]
pub struct TournamentRepository {
    pool: Pool<Postgres>,
}

impl TournamentRepository {
    pub fn new(pool: Pool<Postgres>) -> Self {
        Self { pool }
    }

    pub async fn tournament_exists(&self, tournament_id: Uuid) -> AppResult<bool> {
        Ok(
            query_scalar::<_, bool>("SELECT EXISTS(SELECT 1 FROM tournaments WHERE id = $1)")
                .bind(tournament_id)
                .fetch_one(&self.pool)
                .await?,
        )
    }

    pub async fn list_teams(&self, tournament_id: Uuid) -> AppResult<Vec<TournamentTeam>> {
        Ok(query_as::<_, TournamentTeam>(
            r#"
            SELECT id, tournament_id, name, created_at
            FROM teams
            WHERE tournament_id = $1
            ORDER BY created_at ASC, name ASC
            "#,
        )
        .bind(tournament_id)
        .fetch_all(&self.pool)
        .await?)
    }

    pub async fn get_bracket(&self, tournament_id: Uuid) -> AppResult<Option<PersistedBracket>> {
        Ok(query_as::<_, PersistedBracket>(
            r#"
            SELECT tournament_id, body, bracket_type, created_at, updated_at
            FROM brackets
            WHERE tournament_id = $1
            "#,
        )
        .bind(tournament_id)
        .fetch_optional(&self.pool)
        .await?)
    }

    pub async fn upsert_bracket(
        &self,
        tournament_id: Uuid,
        bracket_type: BracketType,
        body: Value,
    ) -> AppResult<PersistedBracket> {
        Ok(query_as::<_, PersistedBracket>(
            r#"
            INSERT INTO brackets (tournament_id, bracket_type, body)
            VALUES ($1, $2, $3)
            ON CONFLICT (tournament_id)
            DO UPDATE SET
                bracket_type = EXCLUDED.bracket_type,
                body = EXCLUDED.body,
                updated_at = NOW()
            RETURNING tournament_id, body, bracket_type, created_at, updated_at
            "#,
        )
        .bind(tournament_id)
        .bind(bracket_type)
        .bind(body)
        .fetch_one(&self.pool)
        .await?)
    }
}
