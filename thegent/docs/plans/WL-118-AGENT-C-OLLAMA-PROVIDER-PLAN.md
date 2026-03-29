# WL-118 Agent-C Plan: Ollama Provider

## Completed in this slice
- Added doctor visibility check for local Ollama endpoint (`127.0.0.1:11434/api/tags`).
- Added provider normalization for `ollama-local -> ollama`.
- Added catalog route seed (`llama3.3`) and LiteLLM config mapping to `http://127.0.0.1:11434/v1`.

## Remaining (implementation-ready)
1. Add `ollama` provider route and alias normalization.
- Files: `src/thegent/models/catalog.py`, `src/thegent/routing/provider_types.py`
- Behavior: `ollama/<model>` aliases resolve to local provider.

2. Implement provider execution path.
- Files: `src/thegent/routing/litellm_router.py` or dedicated `src/thegent/routing/ollama_provider.py`
- Endpoint: `http://localhost:11434/v1` OpenAI-compatible mode.

3. Add run command parity.
- File: `src/thegent/cli/commands/impl.py`
- Support: `thegent run --provider ollama --model llama3.3 "..."`.

4. Tests.
- Add: `tests/test_wl118_ollama_routing.py`, `tests/test_wl118_ollama_run_cmd.py`, `tests/test_wl118_ollama_doctor_slice.py`.

## Validation commands
- `pytest -q tests/test_wl118_ollama_doctor_slice.py`
- `python -m py_compile src/thegent/doctor.py`

## Wave-2 Delta (2026-02-21)
- Completed:
  - execution-path classification + alias normalization for Ollama.
  - route resolution + LiteLLM config tests for local endpoint wiring.
- Remaining blockers:
  - full run command parity and provider execution hardening across failure modes.

## Wave-10 Delta (2026-02-21)
- Completed:
  - Doctor actionable-hint dedupe now collapses punctuation variants in addition to existing case/whitespace normalization.
  - Added regression coverage for duplicate hints that differ only by trailing punctuation.
- Evidence:
  - `src/thegent/doctor.py`
  - `tests/test_wl118_ollama_doctor_slice.py`
