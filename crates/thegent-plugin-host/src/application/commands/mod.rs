// SPDX-License-Identifier: MIT OR Apache-2.0
//! # Commands

/// Install plugin command
#[allow(dead_code)]
#[derive(Debug, Clone)]
pub struct InstallPluginCommand {
    pub name: String,
    pub version: Option<String>,
    pub path: Option<String>,
}

/// Uninstall plugin command
#[allow(dead_code)]
#[derive(Debug, Clone)]
pub struct UninstallPluginCommand {
    pub name: String,
}

/// Enable plugin command
#[allow(dead_code)]
#[derive(Debug, Clone)]
pub struct EnablePluginCommand {
    pub name: String,
}

/// Disable plugin command
#[allow(dead_code)]
#[derive(Debug, Clone)]
pub struct DisablePluginCommand {
    pub name: String,
}
