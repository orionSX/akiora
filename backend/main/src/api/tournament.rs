use actix_web::{HttpResponse, web};
use uuid::Uuid;

use crate::{
    app::{AppState, app_error::AppResult},
    domain::{entities::enums::BracketType, services::tournament_service::GenerateBracketCommand},
};

#[derive(Debug, serde::Deserialize)]
pub(crate) struct TournamentPath {
    tournament_id: Uuid,
}

#[derive(Debug, serde::Deserialize)]
pub(crate) struct GenerateBracketRequest {
    bracket_type: BracketType,
}

pub async fn get_bracket(
    state: web::Data<AppState>,
    path: web::Path<TournamentPath>,
) -> AppResult<HttpResponse> {
    let bracket = state
        .tournament_service
        .get_bracket(path.tournament_id)
        .await?;

    Ok(HttpResponse::Ok().json(bracket))
}

pub async fn generate_bracket(
    state: web::Data<AppState>,
    path: web::Path<TournamentPath>,
    payload: web::Json<GenerateBracketRequest>,
) -> AppResult<HttpResponse> {
    let bracket = state
        .tournament_service
        .generate_bracket(GenerateBracketCommand {
            tournament_id: path.tournament_id,
            bracket_type: payload.bracket_type,
        })
        .await?;

    Ok(HttpResponse::Ok().json(bracket))
}
