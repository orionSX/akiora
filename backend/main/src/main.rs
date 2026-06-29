use actix_identity::IdentityMiddleware;
use actix_session::{SessionMiddleware, storage::CookieSessionStore};
use actix_web::cookie::Key;
use actix_web::{App, HttpResponse, HttpServer, Responder, get, web};

mod api;
mod app;
mod domain;
mod infra;

use crate::{
    app::AppState,
    domain::services::{AuthService, BracketService, TournamentService, UserService},
    infra::{
        MailSender, RedisAuthChallengeStore, TournamentRepository, UserRepository,
        get_connection_pool, get_redis_client, init_tracing,
    },
};
use dotenvy::dotenv;
use tracing_actix_web::TracingLogger;

#[get("/health")]
async fn health() -> impl Responder {
    HttpResponse::Ok().body("ok")
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    dotenv().ok();

    init_tracing().unwrap();

    let secret_key = std::env::var("SECRET_KEY").expect("SECRET_KEY must be set");
    let session_key = Key::derive_from(secret_key.as_bytes());
    let mail_sender = MailSender::new().unwrap();
    let pool = get_connection_pool().await.unwrap();
    let redis_client = get_redis_client().unwrap();

    let user_repo = UserRepository::new(pool.clone());
    let tournament_repo = TournamentRepository::new(pool);
    let auth_store = RedisAuthChallengeStore::new(redis_client);

    let app_state = AppState::new(
        AuthService::new(
            user_repo.clone(),
            auth_store,
            mail_sender.clone(),
            secret_key,
        ),
        UserService::new(user_repo),
        TournamentService::new(tournament_repo, BracketService),
    );

    HttpServer::new(move || {
        App::new()
            .app_data(web::Data::new(app_state.clone()))
            .wrap(IdentityMiddleware::default())
            .wrap(
                SessionMiddleware::builder(CookieSessionStore::default(), session_key.clone())
                    .cookie_secure(false)
                    .cookie_http_only(true)
                    .build(),
            )
            .wrap(TracingLogger::default())
            .service(health)
            .configure(api::configure)
    })
    .bind("0.0.0.0:3000")
    .unwrap()
    .run()
    .await
}
