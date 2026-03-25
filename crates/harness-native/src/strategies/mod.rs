//! Execution strategies: coalesce, queue, debounce, retry, etc.

mod batch;
mod breaker;
mod cache;
mod causal_order;
mod circuit_breaker;
mod coalesce;
mod debounce;
mod incremental;
mod jobserver;
mod load_balance;
mod proactive_warm;
mod queue;
mod resource_throttle;
mod retry;
mod speculative;

use std::path::Path;

/// Rule options parsed from rules.conf
#[derive(Debug, Clone, Default)]
pub struct RuleOpts {
    pub ttl: u64,
    pub debounce_ms: u64,
    pub error_ttl: u64,
    pub max_concurrent: u32,
    pub priority: String,
    pub cache_key: String,
    pub batch_key: String,
    pub causal_domain: String,
    pub breaker_threshold: u32,
    pub breaker_window: u64,
    pub breaker_cooldown: u64,
    pub retry_max: u32,
    pub retry_backoff_ms: u64,
    pub retry_jitter: f64,
    pub jobserver_auth: String,
    pub jobserver_tokens: u32,
    pub jobserver_borrow: bool,
    pub stale_threshold: u64,
    pub semantic: bool,
}

/// Execute a strategy. Returns exit code.
pub fn execute(
    strategy: &str,
    harness_home: &Path,
    real_cmd: &Path,
    cmd_name: &str,
    subcmd: &str,
    cache_key: &str,
    opts: &RuleOpts,
    args: &[String],
    agent_name: &str,
) -> Result<i32, String> {
    let full_args: Vec<&str> = args.iter().map(|s| s.as_str()).collect();

    match strategy {
        "passthrough" => coalesce::exec_direct(real_cmd, &full_args),
        "coalesce" | "cache" => coalesce::run(
            harness_home,
            real_cmd,
            cache_key,
            opts.ttl,
            opts.debounce_ms,
            opts.error_ttl,
            opts.stale_threshold,
            &full_args,
        ),
        "queue" | "priority_queue" => queue::run(
            harness_home,
            real_cmd,
            cmd_name,
            opts.max_concurrent.max(1),
            &opts.priority,
            agent_name,
            &full_args,
        ),
        "debounce" => debounce::run(real_cmd, opts.debounce_ms, &full_args),
        "retry" => retry::run(
            real_cmd,
            opts.retry_max,
            opts.retry_backoff_ms,
            opts.retry_jitter,
            &full_args,
        ),
        "incremental" => incremental::run(harness_home, real_cmd, cache_key, opts.ttl, &full_args),
        "circuit_breaker" => circuit_breaker::run(
            harness_home,
            real_cmd,
            cache_key,
            opts.ttl,
            opts.debounce_ms,
            opts.error_ttl,
            opts.breaker_threshold,
            opts.breaker_window,
            opts.breaker_cooldown,
            &full_args,
        ),
        "resource_throttle" => resource_throttle::run(
            harness_home,
            real_cmd,
            cmd_name,
            opts.max_concurrent.max(1),
            &opts.priority,
            agent_name,
            &full_args,
        ),
        "jobserver" => jobserver::run(
            harness_home,
            real_cmd,
            cmd_name,
            opts.max_concurrent.max(1),
            &opts.priority,
            &opts.jobserver_auth,
            opts.jobserver_tokens,
            opts.jobserver_borrow,
            &full_args,
        ),
        "load_balance" => queue::run(
            harness_home,
            real_cmd,
            cmd_name,
            opts.max_concurrent.max(1),
            &opts.priority,
            agent_name,
            &full_args,
        ),
        "speculative" => speculative::run(
            harness_home,
            real_cmd,
            cmd_name,
            cache_key,
            opts.ttl,
            opts.debounce_ms,
            opts.error_ttl,
            opts.max_concurrent.max(1),
            &opts.priority,
            &full_args,
        ),
        "proactive_warm" => proactive_warm::run(
            harness_home,
            real_cmd,
            cmd_name,
            subcmd,
            cache_key,
            opts.ttl,
            opts.debounce_ms,
            opts.error_ttl,
            &full_args,
        ),
        "batch" => batch::run(
            harness_home,
            real_cmd,
            cmd_name,
            opts.max_concurrent.max(1),
            &opts.priority,
            &opts.batch_key,
            &full_args,
        ),
        "causal_order" => causal_order::run(
            harness_home,
            real_cmd,
            cmd_name,
            &opts.priority,
            &opts.causal_domain,
            &full_args,
        ),
        _ => coalesce::exec_direct(real_cmd, &full_args),
    }
}
