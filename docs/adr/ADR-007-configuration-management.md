# ADR-007: Configuration Management Strategy

**Date**: 2026-04-05  
**Status**: Accepted  
**Deciders**: Agent  

## Context

thegent manages configuration across multiple platforms (macOS, Linux, WSL) and multiple package managers (Nix, Homebrew, Cargo, apt, etc.). We need a unified configuration system that:

1. Supports declarative configuration
2. Handles platform-specific overrides
3. Enables hot-reloading without restart
4. Validates configuration before applying
5. Provides migration path for config format changes

## Decision Drivers

- **Declarativity**: Users specify desired state, not procedures
- **Idempotency**: Applying same config multiple times yields same result
- **Validation**: Catch errors before applying
- **Portability**: Same config works across platforms
- **Debuggability**: Clear diff between current and desired state

## Configuration Structure

```toml
# Global configuration
[thegent]
version = "1.0"

# Agent defaults
[thegent.agent]
default_role = "general"
max_iterations = 10
temperature = 0.7

# Sandbox defaults
[thegent.sandbox]
default_tier = "bubblewrap"
allow_override = true

# Storage
[thegent.storage]
type = "sqlite"  # or "postgresql"
path = "~/.thegent/thegent.db"
```

```toml
# User/team configuration (extends global)
[dotfiles]
source = "git@github.com:user/dotfiles.git"
branch = "main"

[managers]
enabled = ["nix", "homebrew", "cargo"]

[managers.nix]
enable flakes = true
profile = "home-manager"

[managers.homebrew]
tap = ["homebrew/core", "homebrew/bundle"]

[managers.cargo]
install_binary = true

[platform.linux]
package_manager = "apt"
enabled = true

[platform.darwin]
package_manager = "homebrew"
enabled = true

[platform.windows]
package_manager = "winget"  # Future
enabled = false
```

## Configuration Merge Strategy

```rust
pub struct ConfigManager {
    sources: Vec<ConfigSource>,
}

impl ConfigManager {
    pub fn load() -> Result<ThegentConfig> {
        // Load in order: system → user → workspace → CLI overrides
        let system = self.load_system_config()?;
        let user = self.load_user_config()?;
        let workspace = self.load_workspace_config()?;
        let cli = self.load_cli_overrides()?;
        
        // Merge with precedence (later wins)
        self.merge_configs(vec![system, user, workspace, cli])
    }
    
    fn merge_configs(&self, configs: Vec<ThegentConfig>) -> ThegentConfig {
        // Deep merge: CLI > workspace > user > system
        configs.into_iter().reduce(|acc, next| {
            ConfigMerger::merge(acc, next)
        }).unwrap_or_default()
    }
}

pub struct ConfigMerger;

impl ConfigMerger {
    pub fn merge(base: ThegentConfig, override: ThegentConfig) -> ThegentConfig {
        ThegentConfig {
            version: override.version.or(base.version),
            agent: Self::merge_agent(base.agent, override.agent),
            sandbox: Self::merge_sandbox(base.sandbox, override.sandbox),
            storage: Self::merge_storage(base.storage, override.storage),
            dotfiles: override.dotfiles.or(base.dotfiles),
            managers: Self::merge_managers(base.managers, override.managers),
            platform: Self::merge_platform(base.platform, override.platform),
        }
    }
}
```

## Configuration Validation

```rust
pub struct ConfigValidator;

impl ConfigValidator {
    pub fn validate(config: &ThegentConfig) -> Result<(), ValidationError> {
        self.validate_version(&config.version)?;
        self.validate_agent(&config.agent)?;
        self.validate_sandbox(&config.sandbox)?;
        self.validate_managers(&config.managers)?;
        self.validate_platforms(&config.platform)?;
        Ok(())
    }
    
    fn validate_sandbox(&self, sandbox: &SandboxConfig) -> Result<(), ValidationError> {
        if sandbox.default_tier == SandboxTier::NanoVMM && !sandbox.enable_nanovms {
            return Err(ValidationError::new(
                "NanoVMM tier requires enable_nanovms=true"
            ));
        }
        
        if let Some(ref limits) = sandbox.resource_limits {
            if limits.max_concurrent < limits.max_per_tier.iter().sum() {
                return Err(ValidationError::new(
                    "Total max concurrent must >= sum of per-tier limits"
                ));
            }
        }
        
        Ok(())
    }
}
```

## Platform-Specific Configuration

```rust
pub struct PlatformConfig {
    pub name: Platform,
    pub package_manager: PackageManager,
    pub enabled: bool,
    pub overrides: PlatformOverrides,
}

pub enum Platform {
    Linux,
    Darwin,
    Windows,
    Wsl,
}

pub struct PlatformOverrides {
    pub home_override: Option<PathBuf>,
    pub config_dir: Option<PathBuf>,
    pub data_dir: Option<PathBuf>,
}

impl PlatformConfig {
    pub fn detect() -> Self {
        #[cfg(target_os = "linux")]
        let platform = if std::env::var("WSL_DISTRO_NAME").is_ok() {
            Platform::Wsl
        } else {
            Platform::Linux
        };
        
        #[cfg(target_os = "macos")]
        let platform = Platform::Darwin;
        
        #[cfg(target_os = "windows")]
        let platform = Platform::Windows;
        
        Self {
            name: platform,
            package_manager: Self::detect_package_manager(),
            enabled: true,
            overrides: PlatformOverrides::default(),
        }
    }
}
```

## Hot-Reload Mechanism

```rust
pub struct ConfigWatcher {
    watcher: notify::Watcher,
    tx: mpsc::Sender<ConfigEvent>,
}

#[derive(Debug, Clone)]
pub enum ConfigEvent {
        ConfigChanged { path: PathBuf },
        ConfigError { error: String },
}

impl ConfigWatcher {
    pub fn new<P: AsRef<Path>>(config_paths: Vec<P>) -> Result<Self> {
        let (tx, rx) = mpsc::channel(100);
        
        let mut watcher = notify::recommended_watcher(move |res| {
            match res {
                Ok(events) => {
                    for event in events {
                        if event.kind.is_modify() || event.kind.is_create() {
                            let _ = tx.send(ConfigEvent::ConfigChanged {
                                path: event.paths[0].clone(),
                            });
                        }
                    }
                }
                Err(e) => {
                    let _ = tx.send(ConfigEvent::ConfigError {
                        error: e.to_string(),
                    });
                }
            }
        })?;
        
        // Watch all config files
        for path in config_paths {
            watcher.watch(path.as_ref(), notify::RecursiveMode::NonRecursive)?;
        }
        
        Ok(Self { watcher, tx })
    }
}

pub async fn config_reload_handler(mut rx: mpsc::Receiver<ConfigEvent>) {
    let manager = ConfigManager::new();
    
    while let Some(event) = rx.recv().await {
        match event {
            ConfigEvent::ConfigChanged { path } => {
                tracing::info!("Config changed: {:?}", path);
                match manager.reload() {
                    Ok(new_config) => {
                        config_store::set(new_config);
                        event_bus::publish(ConfigEvent::ConfigReloaded {
                            path,
                        });
                    }
                    Err(e) => {
                        tracing::error!("Failed to reload config: {}", e);
                    }
                }
            }
            ConfigEvent::ConfigError { error } => {
                tracing::error!("Config watcher error: {}", error);
            }
        }
    }
}
```

## Migration Strategy

```rust
pub struct ConfigMigrator {
    migrations: Vec<Box<dyn Migration>>,
}

impl ConfigMigrator {
    pub fn new() -> Self {
        Self {
            migrations: vec![
                Box::new(MigrationV1ToV2),
                Box::new(MigrationV2ToV3),
            ],
        }
    }
    
    pub fn migrate(&self, config: Value, from_version: &str) -> Result<Value> {
        let mut current = config;
        let mut current_version = from_version.to_string();
        
        for migration in &self.migrations {
            if migration.needs_migration(&current_version) {
                current = migration.migrate(current)?;
                current_version = migration.to_version();
            }
        }
        
        Ok(current)
    }
}

pub trait Migration: Send + Sync {
    fn needs_migration(&self, version: &str) -> bool;
    fn to_version(&self) -> String;
    fn migrate(&self, config: Value) -> Result<Value>;
}
```

## Consequences

### Positive
- **Declarative**: Users specify what, not how
- **Idempotent**: Safe to apply multiple times
- **Validated**: Catches errors early
- **Platform-aware**: Works across macOS/Linux/WSL
- **Hot-reload**: No restart needed for config changes

### Negative
- **Complexity**: Deep nested config can be confusing
- **Migration burden**: Need to maintain migrations
- **Performance**: Validation adds startup time

## References

- Nix configuration: https://nixos.org/manual/nix/stable/
- chezmoi templates: https://www.chezmoi.io/
- TOML specification: https://toml.io/
- JSON Schema validation: https://json-schema.org/

---

*This ADR will be updated as implementation progresses*
