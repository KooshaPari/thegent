//! Tests for ConfigEntry domain entity

use phenotype_config::{ConfigEntry, ConfigValue, Namespace};

#[test]
fn test_create_config_entry() {
    let key = "app.version".to_string();
    let value = ConfigValue::string("1.0.0");
    let namespace = Namespace::new("app");
    let created_by = Some("admin".to_string());

    let result = ConfigEntry::new(key.clone(), value, namespace, created_by);
    assert!(result.is_ok());

    let entry = result.unwrap();
    assert_eq!(entry.key(), "app.version");
    assert_eq!(entry.version(), 1);
    assert_eq!(entry.namespace().path(), "app");
}

#[test]
fn test_create_config_entry_empty_key() {
    let key = String::new();
    let value = ConfigValue::string("test");
    let namespace = Namespace::root();
    let created_by = None;

    let result = ConfigEntry::new(key, value, namespace, created_by);
    assert!(result.is_err());
}

#[test]
fn test_create_config_entry_long_key() {
    let key = "a".repeat(300);
    let value = ConfigValue::string("test");
    let namespace = Namespace::root();
    let created_by = None;

    let result = ConfigEntry::new(key, value, namespace, created_by);
    assert!(result.is_err());
}

#[test]
fn test_update_config_entry() {
    let key = "db.host".to_string();
    let value = ConfigValue::string("localhost");
    let namespace = Namespace::new("db");
    let entry = ConfigEntry::new(key, value, namespace, None).unwrap();

    let new_value = ConfigValue::string("prod.db.example.com");
    let updated = entry.update_value(new_value, Some("devops".to_string()));

    assert_eq!(updated.version(), 2);
    assert_eq!(updated.id(), entry.id());
}

#[test]
fn test_config_value_string() {
    let value = ConfigValue::string("hello");
    assert_eq!(value.as_string(), "hello");
}

#[test]
fn test_config_value_integer() {
    let value = ConfigValue::integer(42);
    assert_eq!(value.as_string(), "42");
}

#[test]
fn test_config_value_float() {
    let value = ConfigValue::float(3.14);
    assert_eq!(value.as_string(), "3.14");
}

#[test]
fn test_config_value_boolean() {
    let value_true = ConfigValue::boolean(true);
    assert_eq!(value_true.as_string(), "true");

    let value_false = ConfigValue::boolean(false);
    assert_eq!(value_false.as_string(), "false");
}

#[test]
fn test_config_value_secret() {
    let value = ConfigValue::secret("my-secret-password");
    assert_eq!(value.as_string(), "***SECRET***");
}

#[test]
fn test_namespace_root() {
    let ns = Namespace::root();
    assert!(ns.is_root());
    assert_eq!(ns.path(), "");
}

#[test]
fn test_namespace_path() {
    let ns = Namespace::new("app.config.database");
    assert!(!ns.is_root());
    assert_eq!(ns.path(), "app.config.database");
}

#[test]
fn test_namespace_parent() {
    let ns = Namespace::new("app.config.database");
    let parent = ns.parent();
    assert!(parent.is_some());
    assert_eq!(parent.unwrap().path(), "app.config");
}

#[test]
fn test_namespace_parent_of_root() {
    let ns = Namespace::root();
    assert!(ns.parent().is_none());
}

#[test]
fn test_namespace_parent_of_single_level() {
    let ns = Namespace::new("app");
    let parent = ns.parent();
    assert!(parent.is_some());
    assert!(parent.unwrap().is_root());
}
