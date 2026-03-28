//! Timestamp value object
//! 
//! Immutable timestamp representation.

use chrono::{DateTime, Utc};
use serde::{Serialize, Deserialize};

#[derive(Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct Timestamp(DateTime<Utc>);

impl Timestamp {
    pub fn now() -> Self {
        Self(Utc::now())
    }
    
    pub fn from_datetime(dt: DateTime<Utc>) -> Self {
        Self(dt)
    }
    
    pub fn as_datetime(&self) -> DateTime<Utc> {
        self.0
    }
    
    pub fn as_secs(&self) -> i64 {
        self.0.timestamp()
    }
}

impl From<DateTime<Utc>> for Timestamp {
    fn from(dt: DateTime<Utc>) -> Self {
        Self(dt)
    }
}

impl From<Timestamp> for DateTime<Utc> {
    fn from(ts: Timestamp) -> Self {
        ts.0
    }
}

impl std::fmt::Debug for Timestamp {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "Timestamp({})", self.0.to_rfc3339())
    }
}

impl std::fmt::Display for Timestamp {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.0.to_rfc3339())
    }
}
