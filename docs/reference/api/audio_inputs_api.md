# audio_inputs API Reference

> **Source**: `src/thegent/agents/audio_inputs.py`

Helpers for WL-116 audio transcript input handling.

---

## build_codex_audio_include

Return include list for Codex Responses API audio transcript passthrough.

# @trace WL-116

**Returns**: List of include strings to pass to the Codex Responses API so that
input audio transcripts are surfaced in the response.

---

## inject_transcript_into_prompt

```python
inject_transcript_into_prompt(prompt: str, transcript: str)
```

Inject audio transcript into agent prompt.

# @trace WL-116

**Parameters**:

- `prompt`: The original agent prompt.
- `transcript`: The transcript text to prepend.

**Returns**: Combined prompt with transcript block prepended.

---

## load_transcripts

```python
load_transcripts(paths: list[str])
```

Load transcript text from provided paths.

Accepts transcript text files (.txt, .md, .srt) and binary audio files
(.mp3, .wav, .m4a, .ogg, .flac, .webm, .mp4). Binary audio files are
transcribed via the OpenAI Whisper API (requires OPENAI_API_KEY).

# @trace WL-116

---

## transcribe_audio_file

```python
transcribe_audio_file(path: Path, model: str)
```

Transcribe audio file using OpenAI Whisper API.

# @trace WL-116

**Parameters**:

- `path`: Path to the binary audio file to transcribe.
- `model`: Whisper model identifier (default: "whisper-1").

**Returns**: Transcribed text from the audio file.

**Raises**:

- `FileNotFoundError`: If the audio file does not exist.
- `ValueError`: If the file suffix is not a supported binary audio format.
- `RuntimeError`: If OPENAI_API_KEY is not set or the API call fails.

---

