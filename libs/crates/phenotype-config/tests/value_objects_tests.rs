//! Tests for value objects

use phenotype_config::{ConfigValue, Namespace};

#[test]
fn test_config_value_equality() {
    let value1 = ConfigValue::string("hello");
    let value2 = ConfigValue::string("hello");
    assert_eq!(value1, value2);
}

#[test]
fn test_config_value_inequality() {
    let value1 = ConfigValue::string("hello");
    let value2 = ConfigValue::string("world");
    assert_ne!(value1, value2);
}

#[test]
fn test_config_value_clone() {
    let value = ConfigValue::string("test");
    let cloned = value.clone();
    assert_eq!(value, cloned);
}

#[test]
fn test_json_value_creation() {
    use serde_json::json;
    let json_obj = json!({"key": "value", "number": 42});
    let value = ConfigValue::json(json_obj);
    assert!(value.as_string().contains("key"));
}

#[test]
fn test_namespace_equality() {
    let ns1 = Namespace::new("app.config");
    let ns2 = Namespace::new("app.config");
    assert_eq!(ns1, ns2);
}

#[test]
fn test_namespace_inequality() {
    let ns1 = Namespace::new("app.config");
    let ns2 = Namespace::new("app.other");
    assert_ne!(ns1, ns2);
}

#[test]
fn test_namespace_hash() {
    use std::collections::HashSet;
    let ns1 = Namespace::new("app");
    let ns2 = Namespace::new("app");
    let ns3 = Namespace::new("db");

    let mut set = HashSet::new();
    set.insert(ns1);
    set.insert(ns2);
    set.insert(ns3);

    assert_eq!(set.len(), 2); // ns1 and ns2 should be the same
}

#[test]
fn test_namespace_display() {
    let ns = Namespace::new("app.config.database");
    assert_eq!(ns.to_string(), "app.config.database");
}

#[test]
fn test_namespace_default() {
    let ns = Namespace::default();
    assert!(ns.is_root());
}

#[test]
fn test_config_value_as_string_integer() {
    let value = ConfigValue::integer(12345);
    assert_eq!(value.as_string(), "12345");
}

#[test]
fn test_config_value_as_string_float() {
    let value = ConfigValue::float(99.99);
    assert_eq!(value.as_string(), "99.99");
}

#[test]
fn test_config_value_float_with_precision() {
    let value = ConfigValue::float(1.5);
    let as_str = value.as_string();
    assert!(as_str.contains("1.5"));
}

#[test]
fn test_value_type_as_str() {
    use phenotype_config::ValueType;

    assert_eq!(ValueType::String.as_str(), "string");
    assert_eq!(ValueType::Integer.as_str(), "integer");
    assert_eq!(ValueType::Float.as_str(), "float");
    assert_eq!(ValueType::Boolean.as_str(), "boolean");
    assert_eq!(ValueType::Json.as_str(), "json");
    assert_eq!(ValueType::Secret.as_str(), "secret");
}

#[test]
fn test_value_type_display() {
    use phenotype_config::ValueType;

    assert_eq!(ValueType::String.to_string(), "string");
    assert_eq!(ValueType::Integer.to_string(), "integer");
}

#[test]
fn test_value_type_from_str() {
    use phenotype_config::ValueType;

    assert_eq!("string".parse::<ValueType>().unwrap(), ValueType::String);
    assert_eq!("integer".parse::<ValueType>().unwrap(), ValueType::Integer);
    assert_eq!("float".parse::<ValueType>().unwrap(), ValueType::Float);
    assert_eq!("boolean".parse::<ValueType>().unwrap(), ValueType::Boolean);
    assert_eq!("json".parse::<ValueType>().unwrap(), ValueType::Json);
    assert_eq!("secret".parse::<ValueType>().unwrap(), ValueType::Secret);
}

#[test]
fn test_value_type_from_str_case_insensitive() {
    use phenotype_config::ValueType;

    assert_eq!("STRING".parse::<ValueType>().unwrap(), ValueType::String);
    assert_eq!("Integer".parse::<ValueType>().unwrap(), ValueType::Integer);
}

#[test]
fn test_value_type_from_str_aliases() {
    use phenotype_config::ValueType;

    assert_eq!("int".parse::<ValueType>().unwrap(), ValueType::Integer);
    assert_eq!("double".parse::<ValueType>().unwrap(), ValueType::Float);
    assert_eq!("bool".parse::<ValueType>().unwrap(), ValueType::Boolean);
    assert_eq!("object".parse::<ValueType>().unwrap(), ValueType::Json);
    assert_eq!("password".parse::<ValueType>().unwrap(), ValueType::Secret);
}

#[test]
fn test_value_type_from_str_invalid() {
    use phenotype_config::ValueType;

    assert!("invalid".parse::<ValueType>().is_err());
}

#[test]
fn test_config_value_integer_equality() {
    let v1 = ConfigValue::integer(100);
    let v2 = ConfigValue::integer(100);
    assert_eq!(v1, v2);
}

#[test]
fn test_config_value_boolean_equality() {
    let v1 = ConfigValue::boolean(true);
    let v2 = ConfigValue::boolean(true);
    assert_eq!(v1, v2);

    let v3 = ConfigValue::boolean(false);
    assert_ne!(v1, v3);
}
