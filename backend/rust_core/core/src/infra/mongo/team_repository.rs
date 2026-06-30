use futures::TryStreamExt;
use mongodb::{
    Collection, Database,
    bson::{Document, doc},
};
use uuid::Uuid;

use crate::{domain::entities::team::Team, error::CoreResult};

#[derive(Clone)]
pub struct TeamRepository {
    collection: Collection<Team>,
}

impl TeamRepository {
    pub fn new(database: Database) -> Self {
        Self {
            collection: database.collection("teams"),
        }
    }

    pub async fn create(&self, team: Team) -> CoreResult<Team> {
        self.collection.insert_one(&team).await?;
        Ok(team)
    }

    pub async fn get(&self, id: Uuid) -> CoreResult<Option<Team>> {
        self.collection.find_one(Self::id_filter(id)).await.map_err(Into::into)
    }

    pub async fn list(&self) -> CoreResult<Vec<Team>> {
        let cursor = self.collection.find(doc! {}).await?;
        cursor.try_collect().await.map_err(Into::into)
    }

    pub async fn update(&self, id: Uuid, team: Team) -> CoreResult<Option<Team>> {
        let result = self.collection.replace_one(Self::id_filter(id), &team).await?;

        if result.matched_count == 0 {
            return Ok(None);
        }

        Ok(Some(team))
    }

    pub async fn delete(&self, id: Uuid) -> CoreResult<bool> {
        let result = self.collection.delete_one(Self::id_filter(id)).await?;
        Ok(result.deleted_count > 0)
    }

    fn id_filter(id: Uuid) -> Document {
        doc! { "_id": id.to_string() }
    }
}
