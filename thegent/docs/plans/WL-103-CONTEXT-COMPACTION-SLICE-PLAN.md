# WL-103 Implementation Slice Plan: Context Compaction Layer

## Scope
- Add a reusable `ContextCompactor` primitive and integrate it into one runner path.
- Expose `context_usage_ratio` in `RunResult` without changing existing output shape consumers.

## Proposed Files
- `src/thegent/agents/context_compactor.py`
- `src/thegent/agents/base.py` (extend `RunResult`)
- `src/thegent/agents/direct_agents.py` (single integration point for slice)
- `tests/test_wl103_context_compactor.py`

## Functional Slice
- Token estimator using deterministic heuristics (character-to-token ratio) for V1.
- Trigger compaction when estimated usage exceeds 80% of model window.
- Compact by summarizing oldest turns into one synthetic summary turn.
- Record `context_usage_ratio` on `RunResult`.

## Out-of-Scope for This Slice
- External tokenizer dependency rollout (`tiktoken`) across all environments.
- Multi-model adaptive compaction policy tuning.
- Integration into all runner implementations.

## Implementation Steps
1. Add pure `ContextCompactor` with deterministic input/output and no I/O side effects.
2. Add `context_usage_ratio: float | None` to `RunResult`.
3. Integrate compactor in one runner (`DirectAgentRunner`) after each completed turn.
4. Add unit tests for trigger threshold, compaction behavior, and ratio bounds.
5. Add regression test ensuring no compaction under threshold.

## Validation Commands
- `uv run pytest -q tests/test_wl103_context_compactor.py`
- `uv run python -m py_compile src/thegent/agents/context_compactor.py src/thegent/agents/base.py`

## Risks
- Heuristic token counting can diverge from provider-side accounting.
- Prompt quality degradation if summary prompt is too aggressive.

## Exit Criteria
- 12+ tests for compaction primitive + runner integration pass.
- `RunResult.context_usage_ratio` available and bounded `[0.0, 1.0+]`.
