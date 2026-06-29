mod app_err_impl;
mod auth;
mod tournament;
mod user;

use actix_web::web;

pub fn configure(cfg: &mut web::ServiceConfig) {
    cfg.service(
        web::scope("/api")
            .service(
                web::scope("/auth")
                    .route("/me", web::get().to(auth::me))
                    .route("/login/start", web::post().to(auth::start_login))
                    .route("/login/finish", web::post().to(auth::finish_login)),
            )
            .service(
                web::scope("/users")
                    .route("", web::post().to(user::create_user))
                    .route("", web::get().to(user::list_users))
                    .route("/{user_id}", web::get().to(user::get_user))
                    .route("/{user_id}", web::patch().to(user::update_user))
                    .route("/{user_id}", web::delete().to(user::delete_user)),
            )
            .service(
                web::scope("/tournaments/{tournament_id}/bracket")
                    .route("", web::get().to(tournament::get_bracket))
                    .route("/generate", web::post().to(tournament::generate_bracket)),
            ),
    );
}
