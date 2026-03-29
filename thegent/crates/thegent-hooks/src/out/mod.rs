use crate::{CACHE_DIR, DEFAULT_TTL_SECS, VERSION};

pub(crate) fn print_version() {
    println!("thegent-hooks {}", VERSION);
}

pub(crate) fn print_help() {
    println!("thegent-hooks - Hook runtime for thegent");
    println!();
    println!("USAGE:");
    println!("    thegent-hooks <SUBCOMMAND> [ARGS]");
    println!();
    println!("SUBCOMMANDS:");
    println!("    init                    Initialize hook environment from stdin JSON");
    println!("    dispatch                Parallel hook dispatcher (replaces stop-dispatcher.sh)");
    println!("    quality-gate            Native quality gate (replaces quality-gate.sh)");
    println!(
        "    security-pipeline       Native security pipeline (replaces security-pipeline.sh)"
    );
    println!(
        "    complexity-ratchet      Native complexity ratchet (replaces complexity-ratchet.sh)"
    );
    println!("    cache-key               Generate cache key from hook name + git state");
    println!("    cache-check             Check if cache entry exists and is fresh");
    println!("    cache-read              Read cached result (JSON)");
    println!("    cache-write             Write result to cache");
    println!("    git                     Execute overhauled git with gix/multitenancy");
    println!("    uv                      Execute overhauled uv with tenant-isolation (RESTRICTED FOR AGENTS)");
    println!("    bun                     Execute overhauled bun with tenant-isolation (RESTRICTED FOR AGENTS)");
    println!("    cargo                   Execute overhauled cargo with tenant-isolation");
    println!("    go                      Execute overhauled go with tenant-isolation");
    println!("    ruff                    Execute overhauled ruff with tenant-isolation");
    println!("    pytest                  Execute overhauled pytest with tenant-isolation");
    println!("    sed                     Execute overhauled sed with ast-grep acceleration");
    println!("    cp                      Execute overhauled cp with verification");
    println!("    mv                      Execute overhauled mv with verification");
    println!("    rm                      Execute overhauled rm with protection");
    println!("    mise-setup              Generate OS-aware .mise.toml for global shadowing");
    println!("    NOTE: npm/pnpm/yarn are redirected to bun; pip/poetry are redirected to uv for agents.");
    println!("    changed-files           Get list of changed files");
    println!("    config-get              Get config value by key path");
    println!("    breaker-check           Check circuit breaker status");
    println!("    breaker-record          Record circuit breaker failure");
    println!("    breaker-reset           Reset circuit breaker status");
    println!("    debounce                Coordinated hook debounce");
    println!("    incremental-check       Check incremental manifest");
    println!("    incremental-record      Record incremental manifest");
    println!("    file-hash               Compute file hash (blake3)");
    println!(
        "    stop-reconcile          Native session reconciliation (replaces stop-reconcile.sh)"
    );
    println!("    spec-verify             Native spec verification (replaces spec-verifier.sh)");
    println!(
        "    test-maturity           Native test maturity assessment (replaces test-maturity.sh)"
    );
    println!("    agileplus-cycle         Native AgilePlus governance cycle (replaces agileplus-cycle.sh)");
    println!("    task-completion-verify  Native task completion verification (replaces task-completion-verifier.sh)");
    println!("    qa-artifact-gate        Native artifact quality gate (replaces qa-artifact-quality-gate.sh)");
    println!("    qa-assurance-gate       Native assurance case gate (replaces qa-assurance-case-gate.sh)");
    println!("    qa-policy-engine        Native policy engine (replaces qa-policy-engine.sh)");
    println!(
        "    suppression-blocker     Native suppression blocker (replaces suppression-blocker.sh)"
    );
    println!("    pre-write-validate      Native pre-write syntax validation (replaces pre-write-validator.sh)");
    println!("    post-edit-check         Native post-edit lightweight check (replaces post-edit-checker.sh)");
    println!("    schema-validate         Native JSON Schema validation helper");
    println!("    metric-contracts-eval   Native metric contracts evaluator");
    println!("    reliability-eval        Native reliability gate evaluator");
    println!("    reliability-slo-eval    Native reliability SLO evaluator");
    println!("    flake-quarantine-eval   Native flaky test quarantine evaluator");
    println!("    verifier-dispute-eval   Native verifier dispute evaluator");
    println!("    agent-claim-eval        Native agent claim validator");
    println!("    claim-lifecycle-eval    Native claim lifecycle evaluator");
    println!("    elicitation-closure-eval Native elicitation closure evaluator");
    println!("    methodology-eval        Native methodology attestation evaluator");
    println!("    artifact-quality-eval   Native artifact quality evaluator");
    println!("    playbook-contract-eval  Native playbook contract evaluator");
    println!("    debt-registry-eval      Native debt registry evaluator");
    println!("    formal-registry-eval    Native formal registry evaluator");
    println!("    doc-location-guard      Native doc organization enforcer (replaces doc-location-guard.sh)");
    println!("    change-doc-tracker      Native change boundary tracker (replaces change-doc-tracker.sh)");
    println!("    friction-detect         Native friction pattern detector (replaces friction-detector.sh)");
    println!("    antipattern-detect      Native agent anti-pattern detector (replaces agent-antipattern-detector.sh)");
    println!("    spec-preflight          Native session-start spec analysis (replaces spec-preflight.sh)");
    println!(
        "    prompt-submit-guard     Native user prompt analysis (replaces prompt-submit-guard.sh)"
    );
    println!("    subagent-gate           Native subagent start/stop timing (replaces subagent-quality-gate.sh)");
    println!("    pre-compact             Native pre-compact snapshot (replaces pre-compact-snapshot.sh & auto-checkpoint.sh)");
    println!(
        "    notify                  Native event notification (replaces notify-agent-event.sh)"
    );
    println!(
        "    task-completed          Native task completion hook (replaces task-completed.sh)"
    );
    println!(
        "    teammate-idle           Native teammate idle detection (replaces teammate-idle.sh)"
    );
    println!("    harvest                 Native session stop harvesting (replaces harvest-idea-seeds-stop.sh & harvest-pending-queue.sh)");
    println!("    governance-gates        Native governance gate dispatcher (replaces governance-gates.sh)");
    println!("    prune-orphans           Native orphan process pruning (replaces prune-orphans-stop.sh)");
    println!("    setup                   Generate shell aliases and environment setup");
    println!("    agent                   Unified agent wrapper with mesh coordination");
    println!("    version                 Show version");
    println!("    help                    Show this help");
    println!();
    println!("ENVIRONMENT:");
    println!(
        "    THEGENT_CACHE_DIR    Override cache directory (default: {})",
        CACHE_DIR
    );
    println!(
        "    THEGENT_TTL          Default cache TTL in seconds (default: {})",
        DEFAULT_TTL_SECS
    );
}
