#![allow(
    clippy::needless_borrows_for_generic_args,
    clippy::explicit_counter_loop,
    clippy::collapsible_if,
    clippy::implicit_saturating_sub,
    clippy::io_other_error,
    clippy::useless_format,
    clippy::useless_asref,
    clippy::unwrap_or_default,
    clippy::manual_strip,
    clippy::trim_split_whitespace,
    clippy::manual_div_ceil,
    unused_assignments,
    unused_variables,
    dead_code
)]

pub mod affected_tests;
pub mod changed_files;
pub mod config;
pub mod cost;
pub mod file_discovery;
pub mod git_cache;
pub mod git_ops;
pub mod policy;
pub mod prewarm;
pub mod quality;
pub mod report;
pub mod security;
/// thegent-hooks: Rust governance library for hook runtime
pub mod types;
pub mod utils;

pub use types::{
    CostEstimate, HookConfig, HookError, LintIssue, PolicyOutcome, PolicyRule, QualityMetrics,
    QualityThresholds, RuleType, SecurityFinding, SecurityRule, Severity,
};

pub use affected_tests::{
    AffectedTestsAnalyzer, AffectedTestsError, DetectionStrategy, ImportDetector, PatternDetector,
    TestFile,
};
pub use changed_files::{
    ChangeStatus, ChangedFile, ChangedFilesDetector, ChangedFilesError, DependencyGraph,
    FilterOptions, ImpactType,
};
pub use config::ConfigLoader;
pub use cost::CostCalculator;
pub use file_discovery::{find_files, FileDiscoveryError, FileType};
pub use git_cache::{GitCache, GitCacheError};
pub use git_ops::{GitOps, GitOpsError};
pub use policy::PolicyEngine;
pub use prewarm::{
    PrewarmError, PrewarmManager, PrewarmMetadata, PrewarmReport, RuffCache, SharedDataCache,
    ShellcheckCache, SystemInfoCache,
};
pub use quality::QualityEvaluator;
pub use report::{
    HookReport, Issue, IssueSeverity, IssueType, PerformanceMetrics, ReportError, ReportManager,
    Statistics, SummaryReport,
};
pub use security::SecurityScanner;
pub use utils::{command_exists, get_safe_path, resolve_git_binary, resolve_real_binary};
