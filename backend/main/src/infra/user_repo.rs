use sqlx::{Pool, Postgres, QueryBuilder, query_as};
use uuid::Uuid;

use crate::{
    app::app_error::AppResult,
    domain::entities::community::user::{CreateUser, UpdateUser, User},
};

#[derive(Clone)]
pub struct UserRepository {
    pool: Pool<Postgres>,
}

impl UserRepository {
    pub fn new(pool: Pool<Postgres>) -> Self {
        Self { pool }
    }

    pub async fn create_user(&self, user: CreateUser) -> AppResult<User> {
        Ok(query_as::<_, User>(
            r#"
            INSERT INTO users (name, email, avatar, about)
            VALUES ($1, $2, $3, $4)
            RETURNING id, name, email, avatar, about, created_at, updated_at
            "#,
        )
        .bind(user.name)
        .bind(user.email)
        .bind(user.avatar)
        .bind(user.about)
        .fetch_one(&self.pool)
        .await?)
    }

    pub async fn list_users(&self) -> AppResult<Vec<User>> {
        Ok(query_as::<_, User>(
            r#"
            SELECT id, name, email, avatar, about, created_at, updated_at
            FROM users
            ORDER BY created_at DESC
            "#,
        )
        .fetch_all(&self.pool)
        .await?)
    }

    pub async fn get_user_by_id(&self, user_id: Uuid) -> AppResult<Option<User>> {
        Ok(query_as::<_, User>(
            r#"
            SELECT id, name, email, avatar, about, created_at, updated_at
            FROM users
            WHERE id = $1
            "#,
        )
        .bind(user_id)
        .fetch_optional(&self.pool)
        .await?)
    }

    pub async fn get_user_by_email(&self, email: &str) -> AppResult<Option<User>> {
        Ok(query_as::<_, User>(
            r#"
            SELECT id, name, email, avatar, about, created_at, updated_at
            FROM users
            WHERE email = $1
            "#,
        )
        .bind(email)
        .fetch_optional(&self.pool)
        .await?)
    }

    pub async fn update_user(&self, user_id: Uuid, user: UpdateUser) -> AppResult<Option<User>> {
        let mut builder = QueryBuilder::<Postgres>::new("UPDATE users SET updated_at = NOW()");

        if let Some(name) = user.name {
            builder.push(", name = ").push_bind(name);
        }
        if let Some(email) = user.email {
            builder.push(", email = ").push_bind(email);
        }
        if let Some(avatar) = user.avatar {
            builder.push(", avatar = ").push_bind(avatar);
        }
        if let Some(about) = user.about {
            builder.push(", about = ").push_bind(about);
        }

        builder
            .push(" WHERE id = ")
            .push_bind(user_id)
            .push(" RETURNING id, name, email, avatar, about, created_at, updated_at");

        Ok(builder
            .build_query_as::<User>()
            .fetch_optional(&self.pool)
            .await?)
    }

    pub async fn delete_user(&self, user_id: Uuid) -> AppResult<bool> {
        Ok(sqlx::query("DELETE FROM users WHERE id = $1")
            .bind(user_id)
            .execute(&self.pool)
            .await?
            .rows_affected()
            > 0)
    }
}
