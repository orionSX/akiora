#![allow(dead_code)]

use serde::{Deserialize, Serialize};

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize, sqlx::Type)]
#[sqlx(type_name = "TEXT", rename_all = "lowercase")]
#[serde(rename_all = "lowercase")]
pub enum Server {
    Ru,
    Euw,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize, sqlx::Type)]
#[sqlx(type_name = "TEXT", rename_all = "lowercase")]
#[serde(rename_all = "lowercase")]
pub enum Status {
    Scheduled,
    Active,
    Finished,
    Terminated,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize, sqlx::Type)]
#[sqlx(type_name = "TEXT", rename_all = "lowercase")]
#[serde(rename_all = "lowercase")]
pub enum TournamentType {
    Draft,
    Presigned,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize, sqlx::Type)]
#[sqlx(type_name = "TEXT", rename_all = "lowercase")]
#[serde(rename_all = "lowercase")]
pub enum BracketType {
    Se,
    De,
    Rr,
    Sw,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize, sqlx::Type)]
#[sqlx(type_name = "TEXT", rename_all = "lowercase")]
#[serde(rename_all = "lowercase")]
pub enum Role {
    Top,
    Jg,
    Mid,
    Adc,
    Sup,
}
