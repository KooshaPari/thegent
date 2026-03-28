//! Serialization support for errors

use crate::{Error, ErrorKind, ContextEntry, ContextValue};
use serde::{Serialize, Serializer};
use serde::ser::SerializeStruct;

impl Serialize for Error {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        let mut state = serializer.serialize_struct("Error", 5)?;
        state.serialize_field("kind", &self.kind.code())?;
        state.serialize_field("code", &self.code())?;
        state.serialize_field("message", &self.message)?;
        state.serialize_field("context", &self.context_entries)?;
        if let Some(source) = &self.source {
            state.serialize_field("source", &source.to_string())?;
        } else {
            state.serialize_field::<Option<&str>>("source", &None)?;
        }
        state.end()
    }
}

impl Serialize for ContextEntry {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        let mut state = serializer.serialize_struct("ContextEntry", 2)?;
        state.serialize_field("key", &self.key)?;
        state.serialize_field("value", &self.value)?;
        state.end()
    }
}

impl Serialize for ContextValue {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        match self {
            ContextValue::String(s) => serializer.serialize_str(s),
            ContextValue::Int(i) => serializer.serialize_i64(*i),
            ContextValue::UInt(u) => serializer.serialize_u64(*u),
            ContextValue::Float(f) => serializer.serialize_f64(*f),
            ContextValue::Bool(b) => serializer.serialize_bool(*b),
            ContextValue::Json(j) => serializer.serialize_str(j),
        }
    }
}

impl Serialize for ErrorKind {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        serializer.serialize_str(self.code())
    }
}
