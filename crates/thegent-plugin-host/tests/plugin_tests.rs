//! Integration tests for thegent-plugin-host
//!
//! Traces to:
//! FR: FR-THEGENT-007
//! - FR-THEGENT-007: Plugin host and tooling consolidation

use semver::Version;
use thegent_plugin_host::{Capability, Plugin, PluginDependency, PluginManifest, PluginState};

/// @trace FR-THEGENT-007
#[test]
fn test_plugin_lifecycle() {
    let mut plugin = Plugin::new("test-plugin", Version::new(1, 0, 0), "test-author");
    assert!(matches!(plugin.state, PluginState::Discovered));

    plugin.load();
    assert!(matches!(plugin.state, PluginState::Loaded));
    assert!(plugin.loaded_at.is_some());

    plugin.enable();
    assert!(matches!(plugin.state, PluginState::Enabled));

    plugin.disable();
    assert!(matches!(plugin.state, PluginState::Loaded));

    plugin.unload();
    assert!(matches!(plugin.state, PluginState::Unloaded));
    assert!(plugin.loaded_at.is_none());
}

#[test]
fn test_plugin_id_generation() {
    let plugin1 = Plugin::new("my-plugin", Version::new(1, 0, 0), "author");
    let plugin2 = Plugin::new("other-plugin", Version::new(1, 0, 0), "author");

    assert_ne!(plugin1.id(), plugin2.id());
    assert_eq!(plugin1.id().as_str(), "my_plugin");
    assert_eq!(plugin2.id().as_str(), "other_plugin");
}

#[test]
fn test_plugin_manifest() {
    let manifest = PluginManifest {
        name: "my-plugin".to_string(),
        version: "1.2.3".to_string(),
        description: Some("A test plugin".to_string()),
        author: Some("Test Author".to_string()),
        entry: "plugin.wasm".to_string(),
        capabilities: vec!["fs.read".to_string(), "net.request".to_string()],
        dependencies: vec![PluginDependency {
            name: "base-plugin".to_string(),
            version_req: ">=1.0.0".to_string(),
        }],
    };

    assert_eq!(manifest.name, "my-plugin");
    assert_eq!(manifest.capabilities.len(), 2);
    assert_eq!(manifest.dependencies.len(), 1);
}

#[test]
fn test_plugin_state_transitions() {
    let mut plugin = Plugin::new("test-plugin", Version::new(1, 0, 0), "test");

    // Cannot enable before loading
    plugin.enable();
    assert!(matches!(plugin.state, PluginState::Discovered));

    plugin.load();
    plugin.enable();
    assert!(matches!(plugin.state, PluginState::Enabled));

    plugin.disable();
    assert!(matches!(plugin.state, PluginState::Loaded));

    // Cannot disable before enabling
    plugin.disable();
    assert!(matches!(plugin.state, PluginState::Loaded));
}

#[test]
fn test_plugin_with_capabilities() {
    let mut plugin = Plugin::new("capable-plugin", Version::new(1, 0, 0), "test");
    plugin.capabilities.push(Capability {
        name: "fs.read".to_string(),
        version_req: ">=1.0.0".to_string(),
    });
    plugin.capabilities.push(Capability {
        name: "net.request".to_string(),
        version_req: ">=2.0.0".to_string(),
    });

    assert_eq!(plugin.capabilities.len(), 2);
    assert_eq!(plugin.capabilities[0].name, "fs.read");
}

#[test]
fn test_plugin_manifest_optional_fields() {
    let manifest = PluginManifest {
        name: "minimal-plugin".to_string(),
        version: "0.1.0".to_string(),
        description: None,
        author: None,
        entry: "plugin.wasm".to_string(),
        capabilities: vec![],
        dependencies: vec![],
    };

    assert!(manifest.description.is_none());
    assert!(manifest.author.is_none());
    assert!(manifest.dependencies.is_empty());
}

#[test]
fn test_plugin_dependency() {
    let dep = PluginDependency {
        name: "base-plugin".to_string(),
        version_req: ">=1.0.0,<2.0.0".to_string(),
    };
    assert_eq!(dep.name, "base-plugin");
    assert_eq!(dep.version_req, ">=1.0.0,<2.0.0");
}
