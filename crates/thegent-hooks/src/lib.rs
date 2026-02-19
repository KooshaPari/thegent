/// thegent-hooks: Rust governance library for hook runtime
pub mod types;
pub mod config;
pub mod policy;
pub mod cost;
pub mod quality;
pub mod security;
pub mod utils;
pub mod file_discovery;
pub mod git_cache;
pub mod git_ops;
pub mod changed_files;

pub use types::{
    HookConfig, HookError, PolicyRule, PolicyOutcome, QualityMetrics, SecurityFinding,
    CostEstimate, LintIssue, SecurityRule, QualityThresholds, RuleType, Severity,
};

pub use config::ConfigLoader;
pub use policy::PolicyEngine;
pub use cost::CostCalculator;
pub use quality::QualityEvaluator;
pub use security::SecurityScanner;
pub use utils::{resolve_real_binary, resolve_git_binary, command_exists, get_safe_path};
pub use file_discovery::{find_files, FileType, FileDiscoveryError};
pub use git_cache::{GitCache, GitCacheError};
pub use git_ops::{GitOps, GitOpsError};
pub use changed_files::{
    ChangedFilesDetector, ChangedFile, ChangeStatus, ImpactType, FilterOptions, DependencyGraph,
    ChangedFilesError,
};
