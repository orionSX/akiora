use futures::TryStreamExt;
use mongodb::{
    Collection, Database,
    bson::{Document, doc},
};
use uuid::Uuid;

use crate::{domain::entities::r#match::Match, error::CoreResult};

#[derive(Clone)]
pub struct MatchRepository {
    collection: Collection<Match>,
}

impl MatchRepository {
    pub fn new(database: Database) -> Self {
        Self {
            collection: database.collection("matches"),
        }
    }

    pub async fn create(&self, r#match: Match) -> CoreResult<Match> {
        self.collection.insert_one(&r#match).await?;
        Ok(r#match)
    }

    pub async fn get(&self, id: Uuid) -> CoreResult<Option<Match>> {
        self.collection.find_one(Self::id_filter(id)).await.map_err(Into::into)
    }

    pub async fn list(&self) -> CoreResult<Vec<Match>> {
        let cursor = self.collection.find(doc! {}).await?;
        cursor.try_collect().await.map_err(Into::into)
    }

    pub async fn update(&self, id: Uuid, r#match: Match) -> CoreResult<Option<Match>> {
        let result = self.collection.replace_one(Self::id_filter(id), &r#match).await?;

        if result.matched_count == 0 {
            return Ok(None);
        }

        Ok(Some(r#match))
    }

    pub async fn delete(&self, id: Uuid) -> CoreResult<bool> {
        let result = self.collection.delete_one(Self::id_filter(id)).await?;
        Ok(result.deleted_count > 0)
    }

    fn id_filter(id: Uuid) -> Document {
        doc! { "_id": id.to_string() }
    }
}
