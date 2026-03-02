"""Background execution core for bg commands.

Split from run_execution_core_helpers.py for maintainability.
"""

import os
import platform
import socket
import subprocess
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

import structlog
from rich.console import Console

from thegent.agents import get_fallback_agents, get_runner, resolve_agent
from thegent.agents.resilience import is_usage_limit
from thegent.agents.base import AgentRunner, RunResult
from thegent.cli.commands.observability_impl import escalate_add_impl
from thegent.cli.services import run_session_helpers as _rsh
from thegent.cli.services import run_session_helpers as _rsh_impl
from thegent.cli.services.run_session_helpers import resolve_cwd as _resolve_cwd
from thegent.config import ThegentSettings
from thegent.execution import AgentSource, InteractivityMode, RunMeta, RunRegistry
from thegent.maif import MAIFRunner
from thegent.agents.registry import list_agent_names
from thegent.cli.commands.session_meta_impl import (
    _build_continuation_prompt,
    _save_session_meta,
)
from thegent.cli.services.run_execution_core_helpers import _LazyImpl

_impl_lazy = _LazyImpl()
_log = structlog.get_logger(__name__)
console = Console()
_default_owner_tag = _rsh.default_owner_tag
_session_dir = _rsh_impl.session_dir
_new_session_id = _rsh_impl.new_session_id
_session_paths = _rsh_impl.session_paths

if TYPE_CHECKING:
    from thegent.config_provider import ConfigProvider

def bg_impl_core(
    *,
    agent: str | None,
    prompt: str,
    cd: Path | None,
    mode: str,
    timeout: int,
    full: bool,
    droid: str | None = None,
    model: str | None = None,
    provider: str | None = None,
    owner: str | None = None,
    continue_from: str | None = None,
    continuation_include_stderr: bool = False,
    include_contract: bool = False,
    route_contract: dict[str, Any] | None = None,
    route_request: dict[str, str] | None = None,
    routing: str | None = None,
    failover: bool = False,
    run_id: str | None = None,
    lane: str | None = None,
    confidence: float | None = None,
    contract_version: str | None = None,
    domain: str | None = None,
    idempotency_token: str | None = None,
    speculative: bool = False,
    arbitration: str | None = None,
    override_reason: str | None = None,
    debug: bool = False,
    task_id: str | None = None,
    remote: str | None = None,
    image_paths: list[str] | None = None,
    config_provider: "ConfigProvider | None" = None,
    tenant_id: str | None = None,
    impl_ns: Any | None = None,
) -> dict[str, Any]:
    """
    Start a background run. Returns dict with keys: session_id, log_path, owner.
    """
    if impl_ns is None:
        raise ValueError("impl_ns is required")
    _bind_impl_namespace(impl_ns)

    import sys

    settings = ThegentSettings()
    from thegent.cost.tracker import get_run_cost_tracker

    tracker = get_run_cost_tracker()
    rid = run_id or f"bg_{uuid.uuid4().hex[:8]}"
    tracker.start_run(rid)

    # Pareto routing: routing="pareto" → build RouteCandidate list from catalog and select via ParetoRouter
    agent, model, route_contract, route_request = _impl_lazy._apply_pareto_routing(
        agent, model, routing, include_contract, route_contract, route_request
    )

    # Auto router: agent="auto" or model="auto" → classify + Pareto select
    if settings.auto_router_enabled and (agent == "auto" or model == "auto"):
        try:
            from thegent.utils.routing_impl.auto_router import auto_route

            ar = auto_route(
                prompt=prompt,
                classifier_model=settings.auto_router_classifier_model,
                use_classifier=settings.auto_router_use_classifier,
                min_quality=settings.auto_router_min_quality,
                max_cost_weight=settings.auto_router_max_cost_weight,
            )
            if ar:
                agent = ar.agent
                model = ar.model
                _log.info("Auto router: %s/%s (complexity=%s)", agent, model, ar.complexity)
            else:
                agent = "antigravity"
                model = "gemini-3-flash"
                _log.warning("Auto router failed; fallback to antigravity/gemini-3-flash")
        except Exception as e:
            _log.warning("Auto router error: %s; fallback to antigravity/gemini-3-flash", e)
            agent = "antigravity"
            model = "gemini-3-flash"

    if agent is None and model:
        from thegent.models import normalize_model_id
        from thegent.models.catalog import ModelCatalog, resolve_route

        model_id = normalize_model_id(model)
        route = resolve_route(model_id, provider_hint=provider)
        if route is None:
            routes = ModelCatalog.routes_for(model_id)
            available = ", ".join(sorted({r.provider for r in routes})) if routes else "none"
            suffix = f" Available: {available}." if available != "none" else ""
            return {
                "error": f"Model '{model}' not available via provider '{provider or 'any'}'.{suffix}",
                "agents": available,
                "exit_code": 1,
                "session_id": "failed",
            }
        agent = route[0]
    agent = resolve_agent(agent) or "unknown"

    # WP-X1/V7: Contract Migration & Version Negotiation
    from thegent.contracts.migration import MigrationController
    from thegent.contracts.registry import CONTRACT_SCHEMA_VERSION

    migrator = MigrationController()
    requested_version = contract_version or CONTRACT_SCHEMA_VERSION
    mig_res = migrator.evaluate_version("csm", requested_version)

    if not mig_res["allowed"]:
        return {
            "error": f"Contract version rejected: {mig_res['reason']}",
            "exit_code": 1,
            "session_id": "failed",
        }

    # ROB-010: Contract version downgrade prevention in critical lanes
    # Prevent silent quality regression by blocking version downgrades in critical lanes
    if lane == "critical" and requested_version != CONTRACT_SCHEMA_VERSION:
        # Check if requested version is older than current
        from thegent.contracts.registry import get_registry

        registry = get_registry()
        current_cv = registry.get("csm", CONTRACT_SCHEMA_VERSION)
        requested_cv = registry.get("csm", requested_version)

        if current_cv and requested_cv:
            # Simple version comparison: if requested is not compatible with current, it's a downgrade
            if not registry.is_compatible(requested_version, CONTRACT_SCHEMA_VERSION):
                return {
                    "error": f"ROB-010: Contract version downgrade prevented in critical lane. Requested: {requested_version}, Current: {CONTRACT_SCHEMA_VERSION}",
                    "exit_code": 1,
                    "session_id": "failed",
                    "remediation": f"Use --contract-version {CONTRACT_SCHEMA_VERSION} or remove --lane critical",
                }

    # ConfigProvider: resolve config (Phase 1: EnvConfigProvider; Phase 2+: CP when URL set)
    _bg_config: dict[str, Any] | None = None
    if config_provider is not None:
        _bg_config = config_provider.resolve(tenant_id=tenant_id, request_overrides={"default_timeout": timeout})
    effective_timeout = _bg_config.get("default_timeout", timeout) if _bg_config else timeout
    if agent == "claude":
        _min_claude = (
            _bg_config.get("default_timeout_claude", settings.default_timeout_claude)
            if _bg_config
            else settings.default_timeout_claude
        )
        effective_timeout = max(effective_timeout, _min_claude)
    cwd = _resolve_cwd(cd)
    if cwd is None:
        return {
            "error": "Ambiguous cwd detected. Run inside a project directory or pass --cd with a valid project path.",
            "exit_code": 1,
            "session_id": "failed",
            "run_id": run_id or f"bg_err_{uuid.uuid4().hex[:8]}",
        }

    full = full or True

    effective_prompt = prompt
    if continue_from:
        effective_prompt = _build_continuation_prompt(
            settings, continue_from, prompt, include_stderr=continuation_include_stderr
        )

    owner_tag = owner or _default_owner_tag(cwd, include_process_id=True)
    base = _session_dir(settings, owner_tag)
    session_id = _new_session_id(agent=agent, owner=owner_tag)
    p = _session_paths(base=base, session_id=session_id)

    # Registry integration
    registry = RunRegistry(settings.session_dir)

    # WP-1003/WP-1008: Idempotency
    # OPT-019: Use bloom filter for fast negative lookup before full registry scan
    if idempotency_token:
        # Generate session_id from token for bloom filter lookup
        session_id_from_token = f"run_{hashlib.sha256(idempotency_token.encode()).hexdigest()[:8]}"
        # Fast path: if not in bloom filter, definitely doesn't exist
        if registry.session_exists(session_id_from_token):
            # Might exist, do full lookup
            existing = registry.find_by_token(idempotency_token)
            if existing and existing.get("status") == "completed":
                _log.info("Replay detected for token %s in bg; skipping.", idempotency_token)
                return {
                    "session_id": existing.get("correlation_id") or "replayed",
                    "run_id": existing.get("run_id"),
                    "replayed": True,
                }

    effective_run_id = run_id or f"run_{uuid.uuid4().hex[:8]}"

    # WP-5001: Speculative Execution Mode
    if speculative:
        _log.info("Speculative execution active in background.")

    from thegent.execution import (
        Auditor,
        CircuitBreakerRegistry,
        OverrideRegistry,
        PolicyEngine,
        TrustBoundaryValidator,
    )

    _circuit_breaker = CircuitBreakerRegistry(settings.session_dir)
    trust_boundary = TrustBoundaryValidator(settings.session_dir)
    override_registry = OverrideRegistry(settings.session_dir)
    auditor = Auditor(registry.registry_path)
    policy_engine = PolicyEngine(settings)
    _effective_owner = owner or _default_owner_tag(cwd)
    escalation_sla_minutes = 30
    try:
        escalation_sla_minutes = int(settings.escalation_sla_minutes)
    except (TypeError, ValueError):
        escalation_sla_minutes = 30

    # WP-3007: Trust Boundary Checks
    last_env = trust_boundary.get_last_environment()
    allowed, boundary_reason = trust_boundary.validate_transition(last_env, settings.environment.lower())
    if not allowed:
        return {
            "error": f"Trust boundary violation: {boundary_reason}",
            "exit_code": 1,
            "session_id": "failed",
        }

    resolved_domain_tag = str(domain) if domain else str(settings.default_domain_tag)

    run_meta = RunMeta(
        run_id=effective_run_id,
        correlation_id=session_id,
        source=AgentSource.THEGENT_SUBAGENT if task_id else AgentSource.THEGENT_RUN,
        interactivity=InteractivityMode.HEADLESS_LOGS,
        stdout_path=str(p["stdout"]),
        stderr_path=str(p["stderr"]),
        chat_path=str(base / f"{session_id}.chat.jsonl"),
        messages_path=str(base / f"{session_id}.messages.jsonl"),
        audit_path=str(base / f"{session_id}.audit.jsonl"),
        agent=agent,
        model=model,
        mode=mode,
        prompt=prompt,
        cwd=str(cwd),
        owner=owner_tag,
        is_background=True,
        task_id=task_id,
        route_contract=route_contract,
        route_request=route_request,
        domain_tag=resolved_domain_tag,
        lane=lane or "standard",
        confidence=confidence,
        idempotency_token=idempotency_token,
        contract_version=requested_version,
        arbitration=arbitration,
    )

    # G-GP-05: Policy pre-check for background runs
    pol_res, pol_reason = policy_engine.evaluate(run_meta, registry)

    # WP-3003: Overrides with TTL (revalidation on expiry)
    if pol_res == "deny" and override_registry.has_unexpired(owner_tag):
        _log.info("Policy override (cached, within TTL) for background run")
        pol_res = "allow"
        pol_reason = f"Overridden (cached): {pol_reason}"

    run_meta.policy_result = pol_res
    run_meta.policy_reason = pol_reason
    run_meta.signature = auditor.sign_run(run_meta)

    if pol_res == "deny":
        escalate_add_impl(
            run_id=run_meta.run_id,
            reason=pol_reason,
            sla_minutes=escalation_sla_minutes,
            owner=run_meta.owner,
            agent=run_meta.agent,
            lane=run_meta.lane,
        )
        registry.register_start(run_meta)
        registry.register_end(
            run_id=run_meta.run_id,
            exit_code=1,
            status="failed",
            ended_at_utc=datetime.now(UTC).isoformat(),
            duration_s=0.0,
            error_class="policy_violation",
        )
        return {"error": f"Policy Violation: {pol_reason}", "exit_code": 1}

    if pol_res == "pause":
        from thegent.execution import CheckpointRegistry

        registry.register_start(run_meta)
        registry.register_pause(run_meta.run_id, reason=pol_reason)

        ckpt_registry = CheckpointRegistry(settings.session_dir)
        ckpt_registry.create_checkpoint(
            reason=f"HITL Pause (bg): {pol_reason}",
            dag_content=run_meta.model_dump_json(),
            owner=run_meta.owner,
        )

        escalate_add_impl(
            run_id=run_meta.run_id,
            reason=f"HITL Pause (bg): {pol_reason}",
            sla_minutes=escalation_sla_minutes,
            owner=run_meta.owner,
            agent=run_meta.agent,
            lane=run_meta.lane,
            priority=1,
        )
        return {
            "error": f"HITL PAUSE: {pol_reason}",
            "session_id": session_id,
            "status": "paused",
            "run_id": run_meta.run_id,
        }

    registry.register_start(run_meta)

    # WP-RC-01: Remote Compute Offload (Phase 4)
    if remote:
        from thegent.research.remote_compute import RemoteComputeClient

        client = RemoteComputeClient(remote)

        import tempfile

        remote_path = Path(tempfile.gettempdir()) / f"thegent-run-{run_meta.run_id}"
        _log.info(f"Offloading background execution to remote host: {remote}")

        # 1. Sync files to remote
        if cwd is None:
            return {"error": "Cannot transfer files: cwd is not set", "exit_code": 1}
        if not client.transfer_files(cwd, str(remote_path)):
            return {"error": f"Failed to sync project to remote host: {remote}", "exit_code": 1}

        # 2. Reconstruct command without --remote to avoid infinite loops
        remote_args = [a for a in sys.argv if not a.startswith("--remote")]
        # Ensure we use background 'bg' on remote if we want it to be backgrounded there too
        # Or just 'run' since we are already backgrounding this call?
        # Actually, if we use 'bg' on remote, we get another layer of backgrounding.
        # Let's use 'run' on remote.
        remote_command = " ".join(f'"{a}"' if " " in a else a for a in remote_args)

        # 3. Execute remote in background (using nohup or similar)
        # For simplicity, we'll just execute it and return the "session"
        _log.info(f"Running remote background command in {remote_path}")
        # We wrap in nohup and redirect to a file on remote
        bg_remote_command = f"nohup {remote_command} > {remote_path}/remote_bg.log 2>&1 & echo $!"
        remote_res = client.execute_remote(bg_remote_command, cwd=Path(remote_path))

        if remote_res.get("status") == "success":
            remote_pid = remote_res.get("stdout", "").strip()
            return {
                "session_id": f"remote-{remote_pid}",
                "run_id": run_meta.run_id,
                "remote_host": remote,
                "remote_path": remote_path,
                "status": "started_remote",
            }
        return remote_res

    # Build command against Thegent 3.0 apps layout.
    cmd: list[str] = [sys.executable, "-m", "thegent.main", "run", "agent", effective_prompt]
    cmd.extend(["--cd", str(cwd), "--timeout", str(effective_timeout), "--lane", lane or "standard"])
    if agent:
        cmd.extend(["--agent", agent])
    if full:
        cmd.append("--full")
    if routing:
        cmd.extend(["--routing", routing])
    if failover:
        cmd.append("--failover")
    if model:
        cmd.extend(["--model", model])
    if requested_version:
        cmd.extend(["--contract-version", requested_version])
    if domain:
        cmd.extend(["--domain", domain])
    if task_id:
        cmd.extend(["--task-id", task_id])
    if idempotency_token:
        cmd.extend(["--idempotency-token", idempotency_token])
    if speculative:
        cmd.append("--speculative")

    # Pass run_id to the spawned run so registry lifecycle is correlated.
    cmd.extend(["--run-id", effective_run_id])

    # Phase P4: holdpty wrapper
    if settings.use_holdpty is True:
        in_path = p.get("in")
        if in_path is None:
            raise RuntimeError("Session paths missing 'in' key")
        socket_path = in_path.with_suffix(".sock")
        holdpty_cmd = [
            sys.executable,
            "-m",
            "thegent.main",
            "holdpty",
            "--socket",
            str(socket_path),
            "--session-id",
            session_id,
            "--",
        ]
        cmd = holdpty_cmd + cmd

    stdout_handle = p["stdout"].open("wb")
    stderr_handle = p["stderr"].open("wb")

    # macOS sandbox wrapping (THGENT_SANDBOX_LEVEL)
    from thegent.security.macos_sandbox import MacOSSandbox, SandboxLevel

    _sandbox = MacOSSandbox.from_env()  # from_env() is fine, it just returns cls()
    _sandbox_level = MacOSSandbox.level_from_settings()
    if _sandbox_level not in (SandboxLevel.NONE, SandboxLevel.FULL):
        cmd = _sandbox.apply_to_command(cmd, _sandbox_level, project_root=cwd)
        _log.debug("macOS sandbox level %r applied to agent command", _sandbox_level.value)

    # G-GP-08: Sandbox environment filtering
    if settings.sandbox_env_filter:
        allowlist = settings.sandbox_env_allowlist
        env = {k: v for k, v in os.environ.items() if k in allowlist or k.startswith("THGENT_")}
    else:
        env = os.environ.copy()

    env["PYTHONUNBUFFERED"] = "1"
    env.update(
        {
            "THGENT_SESSION_ID": session_id,
            "THGENT_SESSION_META_PATH": str(p["meta"]),
            "THGENT_SESSION_RC_PATH": str(p["rc"]),
            "THGENT_SESSION_STDOUT_PATH": str(p["stdout"]),
            "THGENT_SESSION_STDERR_PATH": str(p["stderr"]),
            "THGENT_OWNER_TAG": owner_tag,
        }
    )

    stdin_handle = subprocess.DEVNULL
    if settings.use_fifo is True:
        try:
            # On Unix, create a FIFO
            if platform.system() != "Windows":
                in_path = p.get("in")
                if in_path is None:
                    raise RuntimeError("Session paths missing 'in' key")
                if not in_path.exists():
                    os.mkfifo(str(in_path))
                # Open for reading in non-blocking mode to avoid hanging the parent
                # but then set to blocking for the child if needed.
                # Actually, opening a FIFO for reading will block until a writer opens it.
                # To avoid blocking bg_impl, we should open it in the background or use O_NONBLOCK.
                fifo_fd = os.open(str(in_path), os.O_RDONLY | os.O_NONBLOCK)
                stdin_handle = fifo_fd
            else:
                _log.warning("FIFO not supported on Windows; falling back to DEVNULL.")
        except Exception as e:
            _log.warning("Failed to create FIFO: %s", e)

    try:
        proc = _impl_lazy._spawn_with_eagain_retry(
            cmd,
            cwd=str(cwd),
            env=env,
            stdin=stdin_handle,
            stdout=stdout_handle,
            stderr=stderr_handle,
        )
    except Exception:
        stdout_handle.close()
        stderr_handle.close()
        if isinstance(stdin_handle, int) and stdin_handle > 0:
            os.close(stdin_handle)
        raise
    finally:
        stdout_handle.close()
        stderr_handle.close()
        # Do not close stdin_handle here if it's an FD being inherited

    meta: dict[str, Any] = {
        "version": 1,
        "session_id": session_id,
        "agent": agent,
        "owner": owner_tag,
        "cwd": str(cwd),
        "prompt": prompt,
        "mode": mode,
        "timeout_hint_s": effective_timeout,
        "host": socket.gethostname(),
        "launcher_pid": os.getpid(),
        "launcher_ppid": os.getppid(),
        "launcher_uid": os.getuid(),
        "status": "running",
        "started_at_utc": datetime.now(UTC).isoformat(),
        "pid": proc.pid,
        "command": cmd,
        "paths": {k: str(v) for k, v in p.items()},
    }
    if include_contract:
        if route_contract is not None:
            meta["route_contract"] = route_contract
        if route_request is not None:
            meta["route_request"] = route_request
    if continue_from:
        meta["continued_from"] = continue_from.split(",")[0].strip()
    _save_session_meta(p["meta"], meta)

    return {
        "session_id": session_id,
        "log_path": str(p["stdout"]),
        "owner": owner_tag,
    }
