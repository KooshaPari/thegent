"""WL-116 low-risk slice tests."""

from __future__ import annotations

import inspect

import pytest
from thegent.cli.commands.impl import (
    _build_audio_summary_metadata,
    _build_run_event_details,
    _resolve_audio_transcript_for_output,
    run_impl,
)

from thegent.agents.audio_inputs import load_transcripts


def test_run_impl_accepts_audio_files_and_google_grounding() -> None:
    sig = inspect.signature(run_impl)
    assert "audio_files" in sig.parameters
    assert "google_grounding" in sig.parameters


def test_load_transcripts_reads_text_files(tmp_path) -> None:
    p1 = tmp_path / "a.txt"
    p2 = tmp_path / "b.md"
    p1.write_text("first", encoding="utf-8")
    p2.write_text("second", encoding="utf-8")

    transcript, used = load_transcripts([str(p1), str(p2)])

    assert transcript == "first\n\nsecond"
    assert used == [str(p1), str(p2)]


def test_load_transcripts_strips_utf8_bom_in_text_files(tmp_path) -> None:
    p1 = tmp_path / "bom.txt"
    p1.write_text("\ufefftranscript with bom", encoding="utf-8")

    transcript, used = load_transcripts([str(p1)])

    assert transcript == "transcript with bom"
    assert used == [str(p1)]


def test_load_transcripts_reads_srt_files(tmp_path) -> None:
    srt = tmp_path / "clip.srt"
    srt.write_text(
        "1\n00:00:00,000 --> 00:00:01,500\nhello world\n\n2\n00:00:02,000 --> 00:00:03,000\nsecond line\n",
        encoding="utf-8",
    )
    transcript, used = load_transcripts([str(srt)])
    assert transcript == "hello world\nsecond line"
    assert used == [str(srt)]


def test_load_transcripts_rejects_missing_file(tmp_path) -> None:
    missing = tmp_path / "missing.txt"
    with pytest.raises(FileNotFoundError):
        load_transcripts([str(missing)])


def test_load_transcripts_rejects_unknown_suffix(tmp_path) -> None:
    unknown = tmp_path / "sample.xyz"
    unknown.write_bytes(b"data")
    with pytest.raises(ValueError, match="Unsupported --audio input"):
        load_transcripts([str(unknown)])


def test_resolve_audio_transcript_prefers_runner_metadata() -> None:
    resolved = _resolve_audio_transcript_for_output(
        injected_audio_transcript="from-input-file",
        result_audio_transcript="from-runner",
    )
    assert resolved == "from-runner"


def test_build_audio_summary_metadata_includes_length_and_sources() -> None:
    meta = _build_audio_summary_metadata(
        audio_transcript="hello world",
        audio_sources=["/tmp/a.txt", "/tmp/b.srt"],
    )
    assert meta == {
        "transcript_length_chars": 11,
        "source_count": 2,
        "sources": ["/tmp/a.txt", "/tmp/b.srt"],
    }


def test_build_run_event_details_includes_audio_and_grounding() -> None:
    details = _build_run_event_details(
        grounding_sources=["https://a.example/1"],
        audio_transcript="speaker line",
        audio_sources=["/tmp/clip.srt"],
        context_usage_ratio=0.67891,
    )
    assert details == {
        "grounding_sources": ["https://a.example/1"],
        "audio_transcript": "speaker line",
        "audio_sources": ["/tmp/clip.srt"],
        "context_usage_ratio": 0.6789,
    }
