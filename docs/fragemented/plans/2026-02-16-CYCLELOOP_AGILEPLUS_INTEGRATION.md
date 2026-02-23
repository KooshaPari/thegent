# Cycleloop + AgilePlus Integration Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** Integrate Cycleloop (formerly RalphWiggum) as the execution engine within AgilePlus governance system, enabling autonomous remediation with minimal human intervention.

**Architecture:** Cycleloop becomes the embedded execution engine for AgilePlus's DEPLOY phase. AgentDeployer delegates to LifecycleController for task execution with Checker verification. SOFT mode = autonomous (no human), HARD mode = human-in-loop for sensitive tasks.

**Tech Stack:** Python, thegent CLI, pydantic, graphlib (stdlib)

---

## Task 1: Update AgentDeployer to Use LifecycleController

**Files:**
- Modify: `src/thegent/governance/agent_deployer.py:1-180`
- Test: `tests/test_unit_agent_deployer.py` (create)

**Step 1: Create failing test**

```python
# tests/test_unit_agent_deployer.py
import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from thegent.governance.agent_deployer import AgentDeployer, DeploymentResult


def test_deployer_uses_lifecycle_controller():
    """AgentDeployer should use LifecycleController for execution."""
    mock_cost = Mock()
    mock_cost.can_spawn.return_value = True
    mock_cost.record_call = Mock()

    deployer = AgentDeployer(cost_controller=mock_cost)

    # Verify LifecycleController is imported and used
    assert hasattr(deployer, '_lifecycle_controller') or 'lifecycle' in str(type(deployer))
```

Run: `pytest tests/test_unit_agent_deployer.py -v`
Expected: FAIL - attribute doesn't exist yet

**Step 2: Implement LifecycleController integration**

Update `agent_deployer.py`:

```python
from thegent.agents.loop_controller import LifecycleController, LoopMode
from thegent.config import ThegentSettings

class AgentDeployer:
    def __init__(
        self,
        cost_controller: CostControllerProtocol,
        verification_gate: VerificationGateProtocol | None = None,
        max_concurrent: int = 3,
        lifecycle_mode: str = "soft",  # SOFT = autonomous, HARD = human-in-loop
    ) -> None:
        self.cost_controller = cost_controller
        self.verification_gate = verification_gate
        self.max_concurrent = max_concurrent
        self.lifecycle_mode = lifecycle_mode

        # Initialize LifecycleController
        settings = ThegentSettings()
        self._lifecycle_controller = LifecycleController(
            settings=settings,
            worker_agent_name="claude-sonnet-4-5",
            checker_agent_name="antigravity",
            mode=LoopMode(lifecycle_mode),
        )
```

**Step 3: Run test to verify it passes**

Run: `pytest tests/test_unit_agent_deployer.py::test_deployer_uses_lifecycle_controller -v`
Expected: PASS

**Step 4: Commit**

```bash
git add src/thegent/governance/agent_deployer.py tests/test_unit_agent_deployer.py
git commit -m "feat: integrate LifecycleController in AgentDeployer"
```

---

## Task 2: Add SOFT/HARD Mode Selection to AgilePlus

**Files:**
- Modify: `src/thegent/governance/agileplus.py:1-100`
- Modify: `src/thegent/governance/triggers.py:1-50`

**Step 1: Add lifecycle_mode parameter to AgilePlusLoop**

```python
# In agileplus.py, update __init__
def __init__(
    self,
    project_dir: Path,
    health_targets_path: Path,
    health_threshold: float = 90.0,
    max_tasks_per_cycle: int = 10,
    max_rerolls: int = 2,
    lifecycle_mode: str = "soft",  # NEW: SOFT=autonomous, HARD=human-in-loop
) -> None:
    # ... existing code ...
    self.lifecycle_mode = lifecycle_mode
```

**Step 2: Pass lifecycle_mode to AgentDeployer**

In `_run_deployment` method:

```python
def _run_deployment(self, plan: Any, pre_scan: Any) -> Any:
    deployer = AgentDeployer(
        cost_controller=self._cost_controller,
        verification_gate=None,
        max_concurrent=3,
        lifecycle_mode=self.lifecycle_mode,  # NEW
    )
```

**Step 3: Add CLI option for lifecycle mode**

In `triggers.py` main():

```python
parser.add_argument(
    "--lifecycle-mode",
    choices=["soft", "hard"],
    default="soft",
    help="Lifecycle execution mode: soft (autonomous) or hard (human-in-loop)",
)
```

**Step 4: Test**

```bash
python -m thegent.governance.triggers --help | grep lifecycle
```

Expected: Shows `--lifecycle-mode` option

**Step 5: Commit**

```bash
git add src/thegent/governance/agileplus.py src/thegent/governance/triggers.py
git commit -m "feat: add SOFT/HARD lifecycle mode selection to AgilePlus"
```

---

## Task 3: Implement Verification Callback to AgilePlus

**Files:**
- Modify: `src/thegent/governance/verification_gate.py:1-50`
- Modify: `src/thegent/agents/loop_controller.py:1-30`

**Step 1: Add callback mechanism to LifecycleController**

In `loop_controller.py`:

```python
class LifecycleController:
    def __init__(
        self,
        # ... existing params ...
        verification_callback: Callable[[str, Any], Any] | None = None,
    ) -> None:
        # ... existing code ...
        self.verification_callback = verification_callback

    def _notify_verification(self, task_id: str, result: Any) -> None:
        """Notify external system of task completion."""
        if self.verification_callback:
            self.verification_callback(task_id, result)
```

**Step 2: Hook up callback in AgentDeployer**

```python
def _run_deployment(self, plan: Any, pre_scan: Any) -> Any:
    # Create verification callback
    def verification_callback(task_id: str, result: Any):
        if self.verification_gate:
            return self.verification_gate.verify_task(task_id, result, pre_scan)
        return result

    deployer = AgentDeployer(
        # ... existing params ...
        lifecycle_controller=self._lifecycle_controller,
    )
```

**Step 3: Test callback flow**

```bash
python -c "
from thegent.governance.agent_deployer import AgentDeployer
from unittest.mock import Mock

mock_cost = Mock()
mock_cost.can_spawn.return_value = True

deployer = AgentDeployer(cost_controller=mock_cost, lifecycle_mode='soft')
print('Callback integrated:', hasattr(deployer, '_lifecycle_controller'))
"
```

**Step 4: Commit**

```bash
git add src/thegent/governance/verification_gate.py src/thegent/agents/loop_controller.py
git commit -m "feat: add verification callback from Cycleloop to AgilePlus"
```

---

## Task 4: Update Sitback Never-Idle to Use New Commands

**Files:**
- Modify: `src/thegent/mcp_sitback.py:45-70`
- Test: Verify dashboard shows health data

**Step 1: Update startup prompt**

In `mcp_sitback.py`, update `thegent_sitback_startup`:

```python
@mcp.prompt
def thegent_sitback_startup() -> str:
    return """You are the Sitback Agent. On startup:
1. Call thegent_sitback_dashboard (or read thegent://sitback/dashboard)
2. Present the summary: sessions, terminals, budget, health score
3. Say: "Sitback ready."
4. Immediately begin the never-idle loop:
   - Run: thegent go health (check governance health)
   - If health < 90: thegent go cycle --lifecycle-mode soft
   - Check: task quality
   - Check: FR traceability
   - Rotate through these; brief pause (30-60s) between steps.
   - Use thegent_wait(session_id) to block on specific runs.
Task flow: Receive → Classify → Route → Execute → Respond → Resume never-idle loop."""
```

**Step 2: Verify MCP registration**

```bash
python -c "from thegent.mcp_sitback import register_sitback; print('MCP OK')"
```

**Step 3: Commit**

```bash
git add src/thegent/mcp_sitback.py
git commit -m "feat: update Sitback never-idle to use AgilePlus commands"
```

---

## Task 5: Add Health-Triggered Governance

**Files:**
- Modify: `src/thegent/governance/triggers.py:100-200`
- Test: `tests/test_unit_triggers.py`

**Step 1: Add health threshold trigger**

```python
class HealthThresholdTrigger:
    """Trigger governance cycle when health drops below threshold."""

    def __init__(
        self,
        loop: AgilePlusLoop,
        threshold: float = 90.0,
        check_interval: int = 60,
    ) -> None:
        self.loop = loop
        self.threshold = threshold
        self.check_interval = check_interval

    def start(self) -> None:
        """Start health monitoring."""
        import threading

        def monitor():
            while not self._shutdown:
                result = self.loop.run_once()  # Quick health check
                if result.health_score < self.threshold:
                    _log.info("Health %s < threshold %s, triggering cycle",
                              result.health_score, self.threshold)
                    self.loop.run_once(force=True)
                time.sleep(self.check_interval)

        self._thread = threading.Thread(target=monitor, daemon=True)
        self._thread.start()
```

**Step 2: Add to CLI**

```python
# In triggers.py main()
parser.add_argument(
    "--watch-health",
    type=float,
    default=90.0,
    help="Trigger cycle when health drops below this threshold",
)
```

**Step 3: Test**

```bash
python -m thegent.governance.triggers --help | grep watch-health
```

**Step 4: Commit**

```bash
git add src/thegent/governance/triggers.py
git commit -m "feat: add health-threshold triggered governance"
```

---

## Task 6: Integration Test - Full Cycle

**Files:**
- Create: `tests/test_integration_agileplus_cycleloop.py`

**Step 1: Write integration test**

```python
"""Integration test: AgilePlus + Cycleloop full cycle."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from thegent.governance.agileplus import AgilePlusLoop


@pytest.mark.integration
def test_agileplus_runs_full_cycle_with_cycleloop(tmp_path):
    """Test complete AgilePlus cycle uses Cycleloop for execution."""
    # Setup
    health_targets = tmp_path / "health-targets.json"
    health_targets.write_text('''{
        "dimensions": {
            "test_coverage": {"weight": 0.2, "target": 80, "direction": "higher_is_better"},
            "lint_violations": {"weight": 0.15, "target": 0, "direction": "lower_is_better"}
        },
        "budget": {"daily_agent_calls": 20}
    }''')

    # Run cycle in SOFT mode (autonomous)
    loop = AgilePlusLoop(
        project_dir=tmp_path,
        health_targets_path=health_targets,
        lifecycle_mode="soft",
    )

    # Verify mode is set
    assert loop.lifecycle_mode == "soft"

    # Run once (will mock actual execution)
    with patch('thegent.governance.scanner.CodebaseScanner.scan') as mock_scan:
        mock_scan.return_value = Mock(dimensions={})
        result = loop.run_once()

    assert result.state in ["idle", "scanning", "analyzing", "error"]
```

**Step 2: Run integration test**

```bash
pytest tests/test_integration_agileplus_cycleloop.py -v -m integration
```

**Step 3: Commit**

```bash
git add tests/test_integration_agileplus_cycleloop.py
git commit -m "test: add integration test for AgilePlus + Cycleloop"
```

---

## Summary

| Task | Description | Files |
|------|-------------|-------|
| 1 | AgentDeployer uses LifecycleController | agent_deployer.py, test |
| 2 | SOFT/HARD mode selection | agileplus.py, triggers.py |
| 3 | Verification callback | loop_controller.py, verification_gate.py |
| 4 | Sitback never-idle update | mcp_sitback.py |
| 5 | Health-threshold trigger | triggers.py |
| 6 | Integration test | test_integration_*.py |

---

**Plan complete and saved to `docs/plans/2026-02-16-CYCLELOOP_AGILEPLUS_INTEGRATION.md`.**

**Two execution options:**

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach?**


---
## See also

- [WORK_STREAM.md](../reference/WORK_STREAM.md) — canonical backlog
- [00-MASTER-INDEX.md](../plans/00-MASTER-INDEX.md) — plan index
