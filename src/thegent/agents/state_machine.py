"""Fallback State Machine for agent orchestration.

Manages the lifecycle of a task run across multiple providers and retry attempts,
enforcing fallback policies and semantic validation gates.
"""

import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from thegent.agents.base import RunResult
from thegent.agents.resilience import FailureKind, classify_failure
from thegent.contracts.adapters import AdapterResult, normalize_output
from thegent.contracts.policy import FallbackPolicy, evaluate_fallback
from thegent.contracts.telemetry import (
    EVENT_NORMALIZATION,
    EVENT_SCHEMA_DRIFT_SEMANTIC,
    EVENT_SCHEMA_DRIFT_STRUCTURAL,
    ContractTelemetry,
)
from thegent.contracts.validation import validate_csm

_log = logging.getLogger(__name__)


@dataclass
class OrchestrationState:
    """State of an orchestration attempt."""

    agent: str
    run_id: str
    model: str | None = None
    attempt: int = 0
    provider_index: int = 0
    providers_tried: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    status: str = "pending"  # pending, running, success, failed, fallback
    last_result: RunResult | None = None
    last_normalization: AdapterResult | None = None
    policy_issues: list[str] = field(default_factory=list)
    semantic_issues: list[str] = field(default_factory=list)


class FallbackStateMachine:
    """State machine for managing orchestration fallbacks."""

    def __init__(
        self,
        providers: list[str],
        run_id: str | None = None,
        policy: FallbackPolicy | None = None,
        telemetry: ContractTelemetry | None = None,
        max_retries_per_provider: int = 3,
        retry_delay_base: float = 2.0,
    ) -> None:
        self.providers = providers
        self.run_id = run_id or f"run_{uuid.uuid4().hex[:8]}"
        self.policy = policy or FallbackPolicy()
        self.telemetry = telemetry
        self.max_retries = max_retries_per_provider
        self.retry_delay = retry_delay_base
        self.state = OrchestrationState(
            agent=providers[0] if providers else "unknown",
            run_id=self.run_id,
        )

    def run(
        self,
        runner_factory: Any,  # Callable[[str], Optional[AgentRunner]]
        prompt: str,
        model: str | None = None,
        **run_kwargs,
    ) -> tuple[RunResult, AdapterResult | None]:
        """Execute the orchestration loop."""
        if not self.providers:
            raise ValueError("No providers specified for orchestration.")

        self.state.model = model
        self.state.status = "running"

        # Get stats for global fallback rate check
        stats = self.telemetry.get_stats(limit=100) if self.telemetry else None

        while self.state.provider_index < len(self.providers):
            current_agent = self.providers[self.state.provider_index]
            self.state.agent = current_agent
            if current_agent not in self.state.providers_tried:
                self.state.providers_tried.append(current_agent)

            for attempt in range(1, self.max_retries + 1):
                self.state.attempt = attempt
                _log.info("Attempting %s (attempt %d/%d)", current_agent, attempt, self.max_retries)

                # 1. Resolve runner
                runner = runner_factory(current_agent)
                if runner is None:
                    _log.error("No runner found for %s", current_agent)
                    self.state.errors.append(f"No runner for {current_agent}")
                    break

                # 2. Execution
                try:
                    result = runner.run(prompt=prompt, **run_kwargs)
                except Exception as e:
                    _log.error("Execution error for %s: %s", current_agent, e)
                    self.state.errors.append(f"Execution error ({current_agent}): {e}")
                    break

                self.state.last_result = result

                # 3. Failure Classification
                failure_kind = classify_failure(result)
                if failure_kind == FailureKind.USAGE_LIMIT:
                    _log.warning("Usage limit reached for %s. Falling back.", current_agent)
                    self.state.errors.append(f"Usage limit ({current_agent})")
                    break

                if result.exit_code != 0:
                    _log.warning("Run failed for %s (code %d)", current_agent, result.exit_code)
                    if failure_kind in (FailureKind.RATE_LIMIT, FailureKind.TRANSIENT):
                        if attempt < self.max_retries:
                            wait_time = self.retry_delay * (2 ** (attempt - 1))
                            _log.info("Retryable failure. Waiting %.1fs...", wait_time)
                            time.sleep(wait_time)
                            continue

                    self.state.errors.append(f"Run failed ({current_agent}, code {result.exit_code})")
                    break

                # 4. Normalization and Semantic Validation
                norm_res = normalize_output(
                    current_agent,
                    {"stdout": result.stdout, "stderr": result.stderr, "exit_code": result.exit_code},
                    context={"run_id": self.run_id},
                )
                self.state.last_normalization = norm_res

                semantic_issues = validate_csm(norm_res.csm)
                self.state.semantic_issues = semantic_issues
                if semantic_issues:
                    _log.warning("Semantic validation failed for %s: %s", current_agent, semantic_issues)

                # 5. Fallback Policy Evaluation
                is_fallback = norm_res.csm.source_contract == "fallback-plain"
                policy_violations = evaluate_fallback(
                    provider=current_agent,
                    confidence=norm_res.confidence,
                    is_fallback=is_fallback,
                    policy=self.policy,
                    stats=stats,
                )
                self.state.policy_issues = policy_violations

                # 6. Record Telemetry (G-RV-07: drift event types)
                if self.telemetry:
                    success = not norm_res.parse_errors and not policy_violations and not semantic_issues
                    errors = (norm_res.parse_errors or []) + policy_violations + semantic_issues
                    if norm_res.parse_errors:
                        event_type = EVENT_SCHEMA_DRIFT_STRUCTURAL
                        self.telemetry.emit_drift_event(
                            self.run_id,
                            current_agent,
                            norm_res.csm.source_contract,
                            "structural",
                            {"parse_errors": norm_res.parse_errors},
                        )
                    elif semantic_issues:
                        event_type = EVENT_SCHEMA_DRIFT_SEMANTIC
                        self.telemetry.emit_drift_event(
                            self.run_id,
                            current_agent,
                            norm_res.csm.source_contract,
                            "semantic",
                            {"semantic_issues": semantic_issues},
                        )
                    else:
                        event_type = EVENT_NORMALIZATION
                    self.telemetry.record_normalization(
                        run_id=self.run_id,
                        provider=current_agent,
                        contract=norm_res.csm.source_contract,
                        confidence=norm_res.confidence,
                        success=success,
                        errors=errors,
                        event_type=event_type,
                    )

                if not policy_violations and not semantic_issues:
                    self.state.status = "success"
                    return result, norm_res

                # If we have other providers, move to next provider
                if self.state.provider_index < len(self.providers) - 1:
                    _log.info("Violations found and fallbacks available. Moving to next provider.")
                    self.state.errors.append(f"Policy/Semantic violation ({current_agent})")
                    break
                # No more providers. Accept if not a hard block.
                hard_block = any("disabled" in v or "strict" in v for v in policy_violations)
                if not hard_block:
                    _log.info("No more providers. Accepting output despite violations.")
                    self.state.status = "success"
                    return result, norm_res
                self.state.status = "failed"
                self.state.errors.append("Policy blocked all available providers.")
                return result, norm_res

            self.state.provider_index += 1
            self.state.status = "fallback"

        self.state.status = "failed"
        return self.state.last_result, self.state.last_normalization
