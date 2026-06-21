// SPDX-License-Identifier: MIT OR Apache-2.0
//! Native plugin loader - Loads dynamic libraries

use libloading::{Library, Symbol};
use std::path::Path;
use tracing::{info, debug};

use crate::domain::{Plugin, PluginManifest};
use crate::ports::PluginLoaderPort;
use crate::PluginError;

/// Native dynamic library loader
#[derive(Debug)]
pub struct NativePluginLoader;

impl NativePluginLoader {
    pub fn new() -> Self {
        Self
    }
    
    /// Get the appropriate library extension for the current platform
    fn library_extension() -> &'static str {
        #[cfg(target_os = "macos")]
        return "dylib";
        #[cfg(target_os = "linux")]
        return "so";
        #[cfg(target_os = "windows")]
        return "dll";
        #[cfg(not(any(target_os = "macos", target_os = "linux", target_os = "windows")))]
        return "so";
    }
}

impl PluginLoaderPort for NativePluginLoader {
    fn can_load(&self, path: &Path) -> bool {
        path.extension()
            .and_then(|ext| ext.to_str())
            .map(|ext| {
                ext == Self::library_extension() || 
                ext == "so" || ext == "dll" || ext == "dylib"
            })
            .unwrap_or(false)
    }
    
    fn load(&self, manifest: PluginManifest, path: &Path) -> Result<Plugin, PluginError> {
        debug!("Loading native plugin: {:?}", path);
        
        if !self.can_load(path) {
            return Err(PluginError::InvalidManifest(
                format!("Not a native library: {:?}", path)
            ));
        }
        
        // Try to load the library
        unsafe {
            let lib = Library::new(path)
                .map_err(|e| PluginError::NativeLoad(format!("Library load failed: {}", e)))?;
            
            // Look for required symbols
            // This validates that the plugin implements the expected interface
            let _: Symbol<unsafe extern "C" fn()> = lib.get(b"plugin_init")
                .map_err(|e| PluginError::NativeLoad(format!("Missing plugin_init symbol: {}", e)))?;
            
            // Library will be dropped when plugin is unloaded
            std::mem::forget(lib); // Prevent drop for now
        }
        
        info!("Successfully loaded native plugin: {}", manifest.name);
        
        let mut plugin = Plugin::new(manifest, path.to_path_buf());
        plugin.is_loaded = true;
        Ok(plugin)
    }
}

impl Default for NativePluginLoader {
    fn default() -> Self {
        Self::new()
    }
}
