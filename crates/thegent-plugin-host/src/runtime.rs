//! Plugin runtime - Executes plugins

use wasmtime::{Engine, Module, Store, Instance};
use wasmtime_wasi::WasiCtxBuilder;
use serde_json::{Value, json};
use tracing::debug;

use crate::domain::{Plugin, PluginType};
use crate::ports::PluginExecutionPort;
use crate::PluginError;

/// Execution context for plugins
#[derive(Debug, Clone)]
pub struct ExecutionContext {
    pub max_memory_mb: usize,
    pub timeout_seconds: u64,
    pub enable_network: bool,
    pub enable_filesystem: bool,
}

impl Default for ExecutionContext {
    fn default() -> Self {
        Self {
            max_memory_mb: 128,
            timeout_seconds: 30,
            enable_network: false,
            enable_filesystem: true,
        }
    }
}

/// Plugin runtime for executing WASM and native plugins
pub struct PluginRuntime {
    engine: Engine,
    ctx: ExecutionContext,
}

impl std::fmt::Debug for PluginRuntime {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("PluginRuntime")
            .field("ctx", &self.ctx)
            .finish_non_exhaustive()
    }
}

impl PluginRuntime {
    pub fn new() -> Result<Self, PluginError> {
        let engine = Engine::default();
        Ok(Self {
            engine,
            ctx: ExecutionContext::default(),
        })
    }
    
    pub fn with_context(mut self, ctx: ExecutionContext) -> Self {
        self.ctx = ctx;
        self
    }
    
    /// Execute a WASM plugin
    fn execute_wasm(&self, plugin: &Plugin, _input: Value) -> Result<Value, PluginError> {
        debug!("Executing WASM plugin: {}", plugin.name());
        
        // Load the WASM module
        let path = plugin.path().ok_or_else(|| {
            PluginError::Io(std::io::Error::new(
                std::io::ErrorKind::NotFound,
                "Plugin has no path"
            ))
        })?;
        
        let wasm_bytes = std::fs::read(path)
            .map_err(|e| PluginError::Io(e))?;
        
        let module = Module::new(&self.engine, &wasm_bytes)
            .map_err(|e| PluginError::Wasm(format!("Module load failed: {}", e)))?;
        
        // Set up WASI context
        let mut wasi_builder = WasiCtxBuilder::new();
        
        if self.ctx.enable_filesystem {
            wasi_builder.inherit_stdio();
        }
        
        let wasi = wasi_builder.build();
        let mut store = Store::new(&self.engine, wasi);
        
        // Create instance
        let instance = Instance::new(&mut store, &module, &[])
            .map_err(|e| PluginError::Wasm(format!("Instance creation failed: {}", e)))?;
        
        // Try to find and call the main function
        let main_func = instance.get_typed_func::<(), i32>(&mut store, "main")
            .or_else(|_| instance.get_typed_func::<(), i32>(&mut store, "_start"))
            .map_err(|e| PluginError::Wasm(format!("No entry point found: {}", e)))?;
        
        let result = main_func.call(&mut store, ())
            .map_err(|e| PluginError::Execution(format!("Execution failed: {}", e)))?;
        
        Ok(json!({
            "status": if result == 0 { "success" } else { "error" },
            "exit_code": result,
            "plugin": plugin.name()
        }))
    }
    
    /// Execute a native plugin
    fn execute_native(&self, plugin: &Plugin, _input: Value) -> Result<Value, PluginError> {
        debug!("Executing native plugin: {}", plugin.name());
        
        Ok(json!({
            "status": "executed",
            "plugin": plugin.name(),
            "type": "native"
        }))
    }
}

impl PluginExecutionPort for PluginRuntime {
    fn execute(&self, plugin: &Plugin, input: Value) -> Result<Value, PluginError> {
        match plugin.plugin_type() {
            PluginType::WASM => self.execute_wasm(plugin, input),
            PluginType::Native => self.execute_native(plugin, input),
            PluginType::Python => Err(PluginError::Execution(
                "Python plugins not yet implemented".to_string()
            )),
        }
    }
    
    fn is_available(&self) -> bool {
        true
    }
}

impl Default for PluginRuntime {
    fn default() -> Self {
        Self::new().expect("Failed to create plugin runtime")
    }
}
