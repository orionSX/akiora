use mongodb::Database;
use uuid::Uuid;

use crate::{
    domain::entities::{r#match::Match, team::Team, tournament::DraftTournament},
    error::CoreResult,
    infra::mongo::{
        match_repository::MatchRepository, team_repository::TeamRepository,
        tournament_repository::TournamentRepository,
    },
};

#[derive(Clone)]
pub struct GameService {
    tournament_repository: TournamentRepository,
    match_repository: MatchRepository,
    team_repository: TeamRepository,
}

impl GameService {
    pub fn new(database: Database) -> Self {
        Self {
            tournament_repository: TournamentRepository::new(database.clone()),
            match_repository: MatchRepository::new(database.clone()),
            team_repository: TeamRepository::new(database),
        }
    }

    pub async fn create_tournament(&self, tournament: DraftTournament) -> CoreResult<DraftTournament> {
        self.tournament_repository.create(tournament).await
    }

    pub async fn get_tournament(&self, id: Uuid) -> CoreResult<Option<DraftTournament>> {
        self.tournament_repository.get(id).await
    }

    pub async fn list_tournaments(&self) -> CoreResult<Vec<DraftTournament>> {
        self.tournament_repository.list().await
    }

    pub async fn update_tournament(
        &self,
        id: Uuid,
        tournament: DraftTournament,
    ) -> CoreResult<Option<DraftTournament>> {
        self.tournament_repository.update(id, tournament).await
    }

    pub async fn delete_tournament(&self, id: Uuid) -> CoreResult<bool> {
        self.tournament_repository.delete(id).await
    }

    pub async fn create_match(&self, r#match: Match) -> CoreResult<Match> {
        self.match_repository.create(r#match).await
    }

    pub async fn get_match(&self, id: Uuid) -> CoreResult<Option<Match>> {
        self.match_repository.get(id).await
    }

    pub async fn list_matches(&self) -> CoreResult<Vec<Match>> {
        self.match_repository.list().await
    }

    pub async fn update_match(&self, id: Uuid, r#match: Match) -> CoreResult<Option<Match>> {
        self.match_repository.update(id, r#match).await
    }

    pub async fn delete_match(&self, id: Uuid) -> CoreResult<bool> {
        self.match_repository.delete(id).await
    }

    pub async fn create_team(&self, team: Team) -> CoreResult<Team> {
        self.team_repository.create(team).await
    }

    pub async fn get_team(&self, id: Uuid) -> CoreResult<Option<Team>> {
        self.team_repository.get(id).await
    }

    pub async fn list_teams(&self) -> CoreResult<Vec<Team>> {
        self.team_repository.list().await
    }

    pub async fn update_team(&self, id: Uuid, team: Team) -> CoreResult<Option<Team>> {
        self.team_repository.update(id, team).await
    }

    pub async fn delete_team(&self, id: Uuid) -> CoreResult<bool> {
        self.team_repository.delete(id).await
    }
}
