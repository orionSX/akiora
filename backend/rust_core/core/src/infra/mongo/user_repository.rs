use futures::TryStreamExt;
use mongodb::{
    Collection, Database,
    bson::{Document, doc},
};
use uuid::Uuid;

use crate::{domain::entities::user::User, error::CoreResult};

#[derive(Clone)]
pub struct UserRepository {
    collection: Collection<User>,
}

impl UserRepository {
    pub fn new(database: Database) -> Self {
        Self {
            collection: database.collection("users"),
        }
    }

    pub async fn create(&self, user: User) -> CoreResult<User> {
        self.collection.insert_one(&user).await?;
        Ok(user)
    }

    pub async fn get(&self, id: Uuid) -> CoreResult<Option<User>> {
        self.collection.find_one(Self::id_filter(id)).await.map_err(Into::into)
    }

    pub async fn list(&self) -> CoreResult<Vec<User>> {
        let cursor = self.collection.find(doc! {}).await?;
        cursor.try_collect().await.map_err(Into::into)
    }

    pub async fn update(&self, id: Uuid, user: User) -> CoreResult<Option<User>> {
        let result = self.collection.replace_one(Self::id_filter(id), &user).await?;

        if result.matched_count == 0 {
            return Ok(None);
        }

        Ok(Some(user))
    }

    pub async fn delete(&self, id: Uuid) -> CoreResult<bool> {
        let result = self.collection.delete_one(Self::id_filter(id)).await?;
        Ok(result.deleted_count > 0)
    }

    fn id_filter(id: Uuid) -> Document {
        doc! { "_id": id.to_string() }
    }
}
