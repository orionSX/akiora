
use mongodb::Database;
use uuid::Uuid;

use crate::{
    domain::entities::{host::Host, user::User},
    error::CoreResult,
    infra::mongo::{host_repository::HostRepository, user_repository::UserRepository},
};

#[derive(Clone)]
pub struct CommunityService {
    host_repository: HostRepository,
    user_repository: UserRepository,
}

impl CommunityService {
    pub fn new(database: Database) -> Self {
        Self {
            host_repository: HostRepository::new(database.clone()),
            user_repository: UserRepository::new(database),
        }
    }

    pub async fn create_host(&self, host: Host) -> CoreResult<Host> {
        self.host_repository.create(host).await
    }

    pub async fn get_host(&self, id: Uuid) -> CoreResult<Option<Host>> {
        self.host_repository.get(id).await
    }

    pub async fn list_hosts(&self) -> CoreResult<Vec<Host>> {
        self.host_repository.list().await
    }

    pub async fn update_host(&self, id: Uuid, host: Host) -> CoreResult<Option<Host>> {
        self.host_repository.update(id, host).await
    }

    pub async fn delete_host(&self, id: Uuid) -> CoreResult<bool> {
        self.host_repository.delete(id).await
    }

    pub async fn create_user(&self, user: User) -> CoreResult<User> {
        self.user_repository.create(user).await
    }

    pub async fn get_user(&self, id: Uuid) -> CoreResult<Option<User>> {
        self.user_repository.get(id).await
    }

    pub async fn list_users(&self) -> CoreResult<Vec<User>> {
        self.user_repository.list().await
    }

    pub async fn update_user(&self, id: Uuid, user: User) -> CoreResult<Option<User>> {
        self.user_repository.update(id, user).await
    }

    pub async fn delete_user(&self, id: Uuid) -> CoreResult<bool> {
        self.user_repository.delete(id).await
    }
}
