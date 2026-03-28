"""Helpers for formatting run command output."""

from __future__ import annotations

from urllib.parse import urlsplit

from phenotype_thegent_core.utils.routing_impl.grounding import normalize_grounding_source_url


def format_context_usage_line(context_usage: object) -> str | None:
    """Render a compact context budget line for user-facing CLI output."""
    if not isinstance(context_usage, dict):
        return None
    used = context_usage.get("used")
    max_val = context_usage.get("max")

    if isinstance(used, int) and isinstance(max_val, int):
        from phenotype_thegent_cli.services.run_input_helpers import build_context_usage_payload

        shared_payload = build_context_usage_payload(
            used=used,
            max_tokens=max_val,
            ratio=context_usage.get("ratio") if isinstance(context_usage.get("ratio"), (float | int)) else None,
        )
        if isinstance(shared_payload, dict):
            display = shared_payload.get("display")
            if isinstance(display, str) and display:
                return f"Context usage: {display}"

    display = context_usage.get("display")
    if not isinstance(display, str) or not display:
        return None
    return f"Context usage: {display}"


def format_transcript_summary_line(audio_metadata: object) -> str | None:
    """Render transcript metadata in run summary output."""
    if not isinstance(audio_metadata, dict):
        return None
    length = audio_metadata.get("transcript_length_chars")
    source_count = audio_metadata.get("source_count")
    if not isinstance(length, int) or not isinstance(source_count, int):
        return None
    if length < 0 or source_count < 0:
        return None
    if source_count == 0:
        return None
    unit = "file" if source_count == 1 else "files"
    if length == 0:
        return f"Transcript input: empty transcript from {source_count} {unit}"
    char_unit = "char" if length == 1 else "chars"
    if source_count > 1:
        avg = round(length / source_count)
        avg_unit = "char" if avg == 1 else "chars"
        return f"Transcript input: {length:,} {char_unit} from {source_count} {unit} (~{avg:,} {avg_unit}/file)"
    return f"Transcript input: {length:,} {char_unit} from {source_count} {unit}"


def _grounding_domains(urls: list[str], *, max_domains: int = 3) -> str | None:
    domains: list[str] = []
    seen: set[str] = set()
    for url in urls:
        netloc = urlsplit(url).netloc.lower()
        netloc = netloc.removeprefix("www.")
        if not netloc or netloc in seen:
            continue
        seen.add(netloc)
        domains.append(netloc)
    if not domains:
        return None
    shown = domains[:max_domains]
    remainder = len(domains) - len(shown)
    if remainder > 0:
        return f"{', '.join(shown)} (+{remainder} more)"
    return ", ".join(shown)


def format_grounding_sources_lines(grounding_sources: object, *, max_rows: int = 3) -> list[str]:
    """Render grounding source URLs in human-facing output."""
    if not isinstance(grounding_sources, list):
        return []
    urls: list[str] = []
    seen: set[str] = set()
    for item in grounding_sources:
        if not isinstance(item, str):
            continue
        url = normalize_grounding_source_url(item)
        if not url:
            continue
        dedupe_key = url.casefold()
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        urls.append(url)
    if not urls:
        return []
    shown_count = min(len(urls), max_rows)
    lines = [f"Grounding sources: showing {shown_count}/{len(urls)}"]
    lines.extend(f"  - {url}" for url in urls[:shown_count])
    remaining = len(urls) - shown_count
    if remaining > 0:
        lines.append(f"  - ... and {remaining} more")
    domains = _grounding_domains(urls)
    if domains:
        lines.append(f"  - domains: {domains}")
    return lines
