use serde::Serializer;
use uuid::Uuid;

pub fn serialize_opt_uuid<S>(opt_uuid: &Option<Uuid>, serializer: S) -> Result<S::Ok, S::Error>
where
    S: Serializer,
{
    match opt_uuid {
        Some(uuid) => uuid::serde::hyphenated::serialize(uuid, serializer),
        None => serializer.serialize_none(),
    }
}
