//! Configuration value types.
//!
//! This module contains pure domain types for representing configuration values.
//! No external dependencies allowed in this module.

use core::fmt;

/// Represents a configuration value.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ConfigValue {
    /// String value
    String(String),
    /// Integer value
    Integer(i64),
    /// Float value
    Float(f64),
    /// Boolean value
    Boolean(bool),
    /// List value
    List(Vec<ConfigValue>),
    /// Object value (nested config)
    Object(Vec<(String, ConfigValue)>),
    /// Null value
    Null,
}

impl ConfigValue {
    /// Create a string config value.
    pub fn string(s: impl Into<String>) -> Self {
        Self::String(s.into())
    }

    /// Create an integer config value.
    pub fn integer(i: i64) -> Self {
        Self::Integer(i)
    }

    /// Create a float config value.
    pub fn float(f: f64) -> Self {
        Self::Float(f)
    }

    /// Create a boolean config value.
    pub fn boolean(b: bool) -> Self {
        Self::Boolean(b)
    }

    /// Create a null config value.
    pub fn null() -> Self {
        Self::Null
    }

    /// Create a list config value.
    pub fn list(values: Vec<ConfigValue>) -> Self {
        Self::List(values)
    }

    /// Create an object config value.
    pub fn object(pairs: Vec<(impl Into<String>, ConfigValue)>) -> Self {
        Self::Object(pairs.into_iter().map(|(k, v)| (k.into(), v)).collect())
    }

    /// Check if the value is null.
    pub fn is_null(&self) -> bool {
        matches!(self, Self::Null)
    }

    /// Try to get as string.
    pub fn as_string(&self) -> Option<&str> {
        match self {
            Self::String(s) => Some(s),
            _ => None,
        }
    }

    /// Try to get as integer.
    pub fn as_integer(&self) -> Option<i64> {
        match self {
            Self::Integer(i) => Some(*i),
            Self::Float(f) if f.fract() == 0.0 => Some(*f as i64),
            _ => None,
        }
    }

    /// Try to get as float.
    pub fn as_float(&self) -> Option<f64> {
        match self {
            Self::Float(f) => Some(*f),
            Self::Integer(i) => Some(*i as f64),
            _ => None,
        }
    }

    /// Try to get as boolean.
    pub fn as_boolean(&self) -> Option<bool> {
        match self {
            Self::Boolean(b) => Some(*b),
            Self::String(s) => match s.to_lowercase().as_str() {
                "true" | "1" | "yes" | "on" => Some(true),
                "false" | "0" | "no" | "off" => Some(false),
                _ => None,
            },
            Self::Integer(i) => Some(*i != 0),
            _ => None,
        }
    }

    /// Try to get as list.
    pub fn as_list(&self) -> Option<&[ConfigValue]> {
        match self {
            Self::List(v) => Some(v),
            _ => None,
        }
    }

    /// Try to get as object.
    pub fn as_object(&self) -> Option<&[(String, ConfigValue)]> {
        match self {
            Self::Object(pairs) => Some(pairs),
            _ => None,
        }
    }

    /// Get a nested value by path (dot-separated).
    ///
    /// # Example
    ///
    /// ```
    /// let obj = ConfigValue::object(vec![
    ///     ("database", ConfigValue::object(vec![
    ///         ("host", ConfigValue::string("localhost")),
    ///     ])),
    /// ]);
    /// assert_eq!(obj.get_path("database.host").unwrap(), Some(&ConfigValue::String("localhost".to_string())));
    /// ```
    pub fn get_path(&self, path: &str) -> Option<&ConfigValue> {
        let parts: Vec<&str> = path.split('.').collect();
        let mut current = self;

        for part in parts {
            current = match current {
                Self::Object(pairs) => pairs.iter().find(|(k, _)| k == part)?.1,
                _ => return None,
            };
        }

        Some(current)
    }

    /// Get a nested value by path, returning a mutable reference.
    pub fn get_path_mut(&mut self, path: &str) -> Option<&mut ConfigValue> {
        let parts: Vec<&str> = path.split('.').collect();
        let mut current: &mut ConfigValue = self;

        for part in parts {
            current = match current {
                Self::Object(pairs) => {
                    let idx = pairs.iter().position(|(k, _)| k == part)?;
                    &mut pairs[idx].1
                }
                _ => return None,
            };
        }

        Some(current)
    }

    /// Convert to string representation.
    pub fn to_string_lossy(&self) -> String {
        match self {
            Self::String(s) => s.clone(),
            Self::Integer(i) => i.to_string(),
            Self::Float(f) => f.to_string(),
            Self::Boolean(b) => b.to_string(),
            Self::Null => "null".to_string(),
            Self::List(_) | Self::Object(_) => self.to_json().unwrap_or_default(),
        }
    }

    /// Convert to JSON string (requires serde feature).
    #[cfg(feature = "serde")]
    pub fn to_json(&self) -> Result<String, serde_json::Error> {
        serde_json::to_string(self)
    }

    /// Parse from JSON string (requires serde feature).
    #[cfg(feature = "serde")]
    pub fn from_json(s: &str) -> Result<Self, serde_json::Error> {
        serde_json::from_str(s)
    }
}

impl fmt::Display for ConfigValue {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::String(s) => write!(f, "{}", s),
            Self::Integer(i) => write!(f, "{}", i),
            Self::Float(fl) => write!(f, "{}", fl),
            Self::Boolean(true) => write!(f, "true"),
            Self::Boolean(false) => write!(f, "false"),
            Self::Null => write!(f, "null"),
            Self::List(_) | Self::Object(_) => {
                #[cfg(feature = "serde")]
                {
                    write!(f, "{}", self.to_json().unwrap_or_default())
                }
                #[cfg(not(feature = "serde"))]
                {
                    write!(f, "[complex value]")
                }
            }
        }
    }
}

#[cfg(feature = "serde")]
impl serde::Serialize for ConfigValue {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        match self {
            Self::String(s) => serializer.serialize_str(s),
            Self::Integer(i) => serializer.serialize_i64(*i),
            Self::Float(fl) => serializer.serialize_f64(*fl),
            Self::Boolean(b) => serializer.serialize_bool(*b),
            Self::Null => serializer.serialize_none(),
            Self::List(v) => serializer.serialize_seq(Some(v.len())),
            Self::Object(pairs) => {
                use serde::ser::SerializeMap;
                let mut map = serializer.serialize_map(Some(pairs.len()))?;
                for (k, v) in pairs {
                    map.serialize_entry(k, v)?;
                }
                map.end()
            }
        }
    }
}

#[cfg(feature = "serde")]
impl<'de> serde::Deserialize<'de> for ConfigValue {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        use serde::de;

        const FIELDS: &[&str] = &[];
        deserializer.deserialize_any(ConfigValueVisitor {
            marker: core::marker::PhantomData,
        })
    }
}

#[cfg(feature = "serde")]
struct ConfigValueVisitor {
    marker: core::marker::PhantomData<ConfigValue>,
}

#[cfg(feature = "serde")]
impl<'de> de::Visitor<'de> for ConfigValueVisitor {
    type Value = ConfigValue;

    fn expecting(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        formatter.write_str("a config value")
    }

    fn visit_str<E>(self, value: &str) -> Result<Self::Value, E>
    where
        E: de::Error,
    {
        Ok(ConfigValue::String(value.to_string()))
    }

    fn visit_i64<E>(self, value: i64) -> Result<Self::Value, E>
    where
        E: de::Error,
    {
        Ok(ConfigValue::Integer(value))
    }

    fn visit_f64<E>(self, value: f64) -> Result<Self::Value, E>
    where
        E: de::Error,
    {
        Ok(ConfigValue::Float(value))
    }

    fn visit_bool<E>(self, value: bool) -> Result<Self::Value, E>
    where
        E: de::Error,
    {
        Ok(ConfigValue::Boolean(value))
    }

    fn visit_none<E>(self) -> Result<Self::Value, E>
    where
        E: de::Error,
    {
        Ok(ConfigValue::Null)
    }

    fn visit_seq<A>(self, mut seq: A) -> Result<Self::Value, A::Error>
    where
        A: de::SeqAccess<'de>,
    {
        let mut values = Vec::new();
        while let Some(value) = seq.next_element()? {
            values.push(value);
        }
        Ok(ConfigValue::List(values))
    }

    fn visit_map<A>(self, mut map: A) -> Result<Self::Value, A::Error>
    where
        A: de::MapAccess<'de>,
    {
        let mut pairs = Vec::new();
        while let Some((key, value)) = map.next_entry()? {
            pairs.push((key, value));
        }
        Ok(ConfigValue::Object(pairs))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_string_value() {
        let val = ConfigValue::string("hello");
        assert_eq!(val.as_string(), Some("hello"));
        assert_eq!(val.as_integer(), None);
    }

    #[test]
    fn test_integer_value() {
        let val = ConfigValue::integer(42);
        assert_eq!(val.as_integer(), Some(42));
        assert_eq!(val.as_float(), Some(42.0));
    }

    #[test]
    fn test_boolean_coercion() {
        let true_val = ConfigValue::boolean(true);
        assert_eq!(true_val.as_string(), None);
        assert!(true_val.as_boolean(), Some(true));

        let str_true = ConfigValue::string("true");
        assert_eq!(str_true.as_boolean(), Some(true));

        let str_yes = ConfigValue::string("yes");
        assert_eq!(str_yes.as_boolean(), Some(true));
    }

    #[test]
    fn test_nested_path() {
        let obj = ConfigValue::object(vec![
            ("database", ConfigValue::object(vec![
                ("host", ConfigValue::string("localhost")),
                ("port", ConfigValue::integer(5432)),
            ])),
        ]);

        assert_eq!(
            obj.get_path("database.host"),
            Some(&ConfigValue::String("localhost".to_string()))
        );
        assert_eq!(
            obj.get_path("database.port"),
            Some(&ConfigValue::Integer(5432))
        );
        assert_eq!(obj.get_path("database.missing"), None);
        assert_eq!(obj.get_path("missing"), None);
    }

    #[test]
    fn test_null_coercion() {
        let val = ConfigValue::Null;
        assert!(val.is_null());
        assert_eq!(val.as_string(), None);
    }
}
