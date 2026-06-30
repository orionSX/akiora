use futures::TryStreamExt;
use mongodb::{
    Collection, Database,
    bson::{Document, doc},
};
use uuid::Uuid;

use crate::{domain::entities::tournament::DraftTournament, error::CoreResult};

#[derive(Clone)]
pub struct TournamentRepository {
    collection: Collection<DraftTournament>,
}

impl TournamentRepository {
    pub fn new(database: Database) -> Self {
        Self {
            collection: database.collection("tournaments"),
        }
    }

    pub async fn create(&self, tournament: DraftTournament) -> CoreResult<DraftTournament> {
        self.collection.insert_one(&tournament).await?;
        Ok(tournament)
    }

    pub async fn get(&self, id: Uuid) -> CoreResult<Option<DraftTournament>> {
        self.collection.find_one(Self::id_filter(id)).await.map_err(Into::into)
    }

    pub async fn list(&self) -> CoreResult<Vec<DraftTournament>> {
        let cursor = self.collection.find(doc! {}).await?;
        cursor.try_collect().await.map_err(Into::into)
    }

    pub async fn update(
        &self,
        id: Uuid,
        tournament: DraftTournament,
    ) -> CoreResult<Option<DraftTournament>> {
        let result = self.collection.replace_one(Self::id_filter(id), &tournament).await?;

        if result.matched_count == 0 {
            return Ok(None);
        }

        Ok(Some(tournament))
    }

    pub async fn delete(&self, id: Uuid) -> CoreResult<bool> {
        let result = self.collection.delete_one(Self::id_filter(id)).await?;
        Ok(result.deleted_count > 0)
    }

    fn id_filter(id: Uuid) -> Document {
        doc! { "_id": id.to_string() }
    }
}
