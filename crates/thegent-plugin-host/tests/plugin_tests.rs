//! Unit tests for thegent-plugin-host
//!
//! Traces to:
//! - FR-THEGENT-007: Plugin host and tooling consolidation

use thegent_plugin_host::{
    Plugin, PluginId, PluginManifest, PluginType, PluginStatus,
    PluginHost,
};

fn create_test_manifest(name: &str) -> PluginManifest {
    PluginManifest {
        name: name.to_string(),
        version: "1.0.0".to_string(),
        description: "Test plugin".to_string(),
        author: "test".to_string(),
        plugin_type: PluginType::Native,
        entry_point: "test.wasm".to_string(),
        permissions: vec![],
        dependencies: vec![],
        config: serde_json::json!({}),
    }
}

/// @trace FR-THEGENT-007
#[test]
fn test_plugin_creation() {
    let manifest = create_test_manifest("test-plugin");
    let plugin = Plugin::new(manifest.clone());
    
    assert_eq!(plugin.manifest.name, "test-plugin");
    assert_eq!(plugin.status, PluginStatus::Inactive);
}

#[test]
fn test_plugin_id_generation() {
    let manifest1 = create_test_manifest("plugin-1");
    let manifest2 = create_test_manifest("plugin-2");
    
    let plugin1 = Plugin::new(manifest1);
    let plugin2 = Plugin::new(manifest2);
    
    assert_ne!(plugin1.id.0, plugin2.id.0);
}

#[test]
fn test_plugin_status_transitions() {
    let manifest = create_test_manifest("test-plugin");
    let mut plugin = Plugin::new(manifest);
    
    assert_eq!(plugin.status, PluginStatus::Inactive);
    
    plugin.activate();
    assert_eq!(plugin.status, PluginStatus::Active);
    
    plugin.deactivate();
    assert_eq!(plugin.status, PluginStatus::Inactive);
}

#[test]
fn test_plugin_host_creation() {
    let host = PluginHost::new();
    let plugins = host.list_plugins();
    assert!(plugins.is_empty());
}

#[test]
fn test_plugin_host_load_unsupported() {
    let host = PluginHost::new();
    
    // Loading WASM plugins is not yet supported in this simplified version
    let manifest = create_test_manifest("test-plugin");
    let plugin = Plugin::new(manifest);
    
    // This should return an error since WASM loading is not implemented
    let result = host.load_plugin(plugin);
    assert!(result.is_err());
}

#[test]
fn test_plugin_type_display() {
    assert_eq!(format!("{:?}", PluginType::Native), "Native");
    assert_eq!(format!("{:?}", PluginType::Wasm), "Wasm");
    assert_eq!(format!("{:?}", PluginType::Python), "Python");
    assert_eq!(format!("{:?}", PluginType::JavaScript), "JavaScript");
}

#[test]
fn test_plugin_status_display() {
    assert_eq!(format!("{:?}", PluginStatus::Inactive), "Inactive");
    assert_eq!(format!("{:?}", PluginStatus::Active), "Active");
    assert_eq!(format!("{:?}", PluginStatus::Error), "Error");
}

#[test]
fn test_plugin_with_dependencies() {
    let mut manifest = create_test_manifest("test-plugin");
    manifest.dependencies.push("dep-plugin >= 1.0.0".to_string());
    
    let plugin = Plugin::new(manifest);
    assert_eq!(plugin.manifest.dependencies.len(), 1);
}

#[test]
fn test_plugin_with_permissions() {
    let mut manifest = create_test_manifest("test-plugin");
    manifest.permissions.push("fs.read".to_string());
    manifest.permissions.push("net.request".to_string());
    
    let plugin = Plugin::new(manifest);
    assert_eq!(plugin.manifest.permissions.len(), 2);
}
