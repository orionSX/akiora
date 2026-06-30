use futures::TryStreamExt;
use mongodb::{
    Collection, Database,
    bson::{Document, doc},
};
use uuid::Uuid;

use crate::{domain::entities::host::Host, error::CoreResult};

#[derive(Clone)]
pub struct HostRepository {
    collection: Collection<Host>,
}

impl HostRepository {
    pub fn new(database: Database) -> Self {
        Self {
            collection: database.collection("hosts"),
        }
    }

    pub async fn create(&self, host: Host) -> CoreResult<Host> {
        self.collection.insert_one(&host).await?;
        Ok(host)
    }

    pub async fn get(&self, id: Uuid) -> CoreResult<Option<Host>> {
        self.collection.find_one(Self::id_filter(id)).await.map_err(Into::into)
    }

    pub async fn list(&self) -> CoreResult<Vec<Host>> {
        let cursor = self.collection.find(doc! {}).await?;
        cursor.try_collect().await.map_err(Into::into)
    }

    pub async fn update(&self, id: Uuid, host: Host) -> CoreResult<Option<Host>> {
        let result = self.collection.replace_one(Self::id_filter(id), &host).await?;

        if result.matched_count == 0 {
            return Ok(None);
        }

        Ok(Some(host))
    }

    pub async fn delete(&self, id: Uuid) -> CoreResult<bool> {
        let result = self.collection.delete_one(Self::id_filter(id)).await?;
        Ok(result.deleted_count > 0)
    }

    fn id_filter(id: Uuid) -> Document {
        doc! { "_id": id.to_string() }
    }
}
