# WL-116 Agent-C Plan: Audio Transcript Passthrough

## Completed in this slice
- Added `--audio` plumbing to run entrypoints.
- Added transcript loader for `.txt`/`.md` inputs.
- Added `audio_transcript` and `audio_sources` to run payload.
- Added `.srt` transcript parsing support and CLI help text update.

## Structured output schema (Wave-6 docs update)

Current `thegent run` payload fields for transcript metadata:

```json
{
  "audio_transcript": "string",
  "audio_sources": ["path-or-uri"],
  "audio_metadata": {
    "transcript_length_chars": 1234,
    "source_count": 2,
    "sources": ["path-or-uri", "path-or-uri"]
  }
}
```

Notes:
- `audio_transcript` and `audio_sources` are emitted only when transcript input exists.
- `audio_metadata.transcript_length_chars` is derived from the resolved transcript used for output.
- `audio_metadata.source_count` and `audio_metadata.sources` mirror `audio_sources` for compact summary rendering and JSON consumers.

## Remaining (blocked for full WL)
1. Binary audio ingestion and transcript extraction.
- Files: `src/thegent/agents/audio_inputs.py`, new `src/thegent/agents/audio_transcribe.py`
- Support: `.wav/.mp3/.m4a`.
- Implementation: call OpenAI transcription path for direct mode; Codex include field passthrough.

2. Codex Responses include support.
- File: `src/thegent/agents/codex_proxy.py`
- Add request include: `item.input_audio.transcript` and map into `RunResult.audio_transcript`.

3. Direct OpenAI fallback path.
- Files: `src/thegent/agents/direct_agents.py`, `src/thegent/cli/commands/impl.py`
- If not Codex path, transcribe first then inject transcript context.

4. Tests.
- Add `tests/test_wl116_audio_binary_inputs.py` and integration tests for payload transcript propagation.

## Validation commands
- `pytest -q tests/test_wl116_audio_inputs.py`
- `python -m py_compile src/thegent/agents/audio_inputs.py src/thegent/cli/commands/impl.py`

## Wave-2 Delta (2026-02-21)
- Completed:
  - `.srt` transcript parsing with timestamp/index stripping.
  - test coverage for `.srt` ingestion path.
- Remaining blockers:
  - binary audio (`.wav/.mp3/.m4a`) transcription path still pending provider integration.

## Wave-10 Delta (2026-02-21)
- Completed:
  - Human summary formatter now uses singular grammar for one-character transcripts (`1 char`) while preserving grouped numeric formatting for larger values.
  - Added focused regression test for singular character output.
- Evidence:
  - `src/thegent/cli/commands/run_output_helpers.py`
  - `tests/test_wl119_run_cli_output.py`
