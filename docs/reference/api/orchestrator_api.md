# orchestrator API Reference

> **Source**: `src/thegent/govern/vetter/orchestrator.py`

VetterOrchestrator: runs checks in order, aggregates verdict, emits governance events.

WL-092 baseline behavior is preserved by default:
- failed checks -> rejected

Opt-in extensions:
- WL-093 escalation path (policy.escalate_on)
- WL-094 evidence append (always when evidence_store is configured)
- WL-096 revision queue path (run_context enable_revision_queue=true)

# @trace WL-092
# @trace WL-093
# @trace WL-094
# @trace WL-096

---

## VetterOrchestrator

Orchestrates VetterCheck instances against agent output per a VetterPolicy.

Constructor parameters:
  session_dir:      Path to the session directory where governance_events.jsonl is written.
  check_registry:   Mapping of check name -> VetterCheck instance (structural protocol).
  evidence_store:   Optional; not wired in WL-092 (reserved for WL-094).
  hitl_workflow:    Optional; not wired in WL-092 (reserved for WL-093).
  event_log:        Optional; not wired in WL-092 (reserved for WL-094).
  prompt_queue:     Optional; not wired in WL-092 (reserved for WL-096).
  federated_policy: Optional; not wired in WL-092 (reserved for WL-099).

Fail fast, fail loudly. No silent error handling. No fallbacks.
# @trace WL-092

### Methods

#### VetterOrchestrator.__init__

```python
__init__(self: Any, session_dir: Path, check_registry: Any, evidence_store: Any, hitl_workflow: Any, event_log: Any, prompt_queue: Any, federated_policy: Any)
```

---

---

