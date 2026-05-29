//! WASM plugin loader - Loads and executes WASM plugins

use wasmtime::{Engine, Module, Store, Instance};
use wasmtime_wasi::WasiCtxBuilder;
use std::path::Path;
use tracing::{info, debug};

use crate::domain::{Plugin, PluginManifest};
use crate::ports::PluginLoaderPort;
use crate::PluginError;

/// WASM plugin loader
pub struct WasmPluginLoader {
    engine: Engine,
}

impl std::fmt::Debug for WasmPluginLoader {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("WasmPluginLoader")
            .finish_non_exhaustive()
    }
}

impl WasmPluginLoader {
    pub fn new() -> Result<Self, PluginError> {
        let engine = Engine::default();
        Ok(Self { engine })
    }
    
    /// Precompile a WASM module for faster loading
    pub fn precompile(&self, wasm_bytes: &[u8]) -> Result<Vec<u8>, PluginError> {
        self.engine
            .precompile_module(wasm_bytes)
            .map_err(|e| PluginError::Wasm(format!("Precompilation failed: {}", e)))
    }
}

impl PluginLoaderPort for WasmPluginLoader {
    fn can_load(&self, path: &Path) -> bool {
        path.extension()
            .and_then(|ext| ext.to_str())
            .map(|ext| ext == "wasm" || ext == "wat")
            .unwrap_or(false)
    }
    
    fn load(&self, manifest: PluginManifest, path: &Path) -> Result<Plugin, PluginError> {
        debug!("Loading WASM plugin: {:?}", path);
        
        // Verify it's actually a WASM file
        if !self.can_load(path) {
            return Err(PluginError::InvalidManifest(
                format!("Not a WASM file: {:?}", path)
            ));
        }
        
        // Try to load and validate the module
        let wasm_bytes = std::fs::read(path)
            .map_err(|e| PluginError::Io(e))?;
        
        let module = Module::new(&self.engine, &wasm_bytes)
            .map_err(|e| PluginError::Wasm(format!("Module creation failed: {}", e)))?;
        
        // Create a test store to verify the module can be instantiated
        let wasi = WasiCtxBuilder::new()
            .inherit_stdio()
            .inherit_env()
            .map_err(|e| PluginError::Wasm(format!("WASI env setup failed: {}", e)))?
            .build();
        
        let mut store = Store::new(&self.engine, wasi);
        
        // Try to instantiate (this validates the module)
        let _instance = Instance::new(&mut store, &module, &[])
            .map_err(|e| PluginError::Wasm(format!("Instantiation failed: {}", e)))?;
        
        info!("Successfully loaded WASM plugin: {}", manifest.name);
        
        let mut plugin = Plugin::new(manifest, path.to_path_buf());
        plugin.is_loaded = true;
        Ok(plugin)
    }
}

impl Default for WasmPluginLoader {
    fn default() -> Self {
        Self::new().expect("Failed to create WASM engine")
    }
}
