use crate::domain::services::{AuthService, TournamentService, UserService};

#[derive(Clone)]
pub struct AppState {
    pub auth_service: AuthService,
    pub user_service: UserService,
    pub tournament_service: TournamentService,
}

impl AppState {
    pub fn new(
        auth_service: AuthService,
        user_service: UserService,
        tournament_service: TournamentService,
    ) -> Self {
        Self {
            auth_service,
            user_service,
            tournament_service,
        }
    }
}
