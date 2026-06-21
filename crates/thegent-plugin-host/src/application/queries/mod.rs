// SPDX-License-Identifier: MIT OR Apache-2.0
//! # Queries

/// List plugins query
#[allow(dead_code)]
#[derive(Debug, Clone)]
pub struct ListPluginsQuery {
    pub include_disabled: bool,
}

/// Get plugin query
#[allow(dead_code)]
#[derive(Debug, Clone)]
pub struct GetPluginQuery {
    pub name: String,
}

/// Search plugins query
#[allow(dead_code)]
#[derive(Debug, Clone)]
pub struct SearchPluginsQuery {
    pub pattern: String,
}
