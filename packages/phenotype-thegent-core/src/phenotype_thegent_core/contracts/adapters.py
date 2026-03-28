"""Output adapter protocol and scaffolding for provider-specific normalization.

Adapters convert copilot/gemini/codex/claude (and other) outputs into
CanonicalStructuredMessage for orchestration pipelines.
"""

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from phenotype_thegent_core.contracts.csm import CanonicalStructuredMessage, CSMPhase, CSMStatus
from phenotype_thegent_core.contracts.validation import validate_csm


@dataclass
class AdapterResult:
    """Result of adapter normalization."""

    csm: CanonicalStructuredMessage
    confidence: float = 1.0  # 0.0-1.0 adapter confidence in normalization
    parse_errors: list[str] = field(default_factory=list)
    source_provider: str = ""


@runtime_checkable
class OutputAdapter(Protocol):
    """Protocol for provider output adapters.

    Each provider (copilot, gemini, codex, claude, etc.) should implement
    an adapter that normalizes raw output into CanonicalStructuredMessage.
    """

    @property
    def provider(self) -> str:
        """Provider identifier (e.g. copilot, gemini, codex, claude)."""
        ...

    def normalize(self, raw: str | dict[str, Any], context: dict[str, Any] | None = None) -> AdapterResult:
        """Normalize raw provider output to CSM.

        Args:
            raw: Raw stdout string or parsed dict from provider.
            context: Optional context (run_id, chunk_id, etc.).

        Returns:
            AdapterResult with CSM and confidence.
        """
        ...


class XMLOutputAdapter:
    """Base adapter for XML-structured agent outputs."""

    def __init__(self, provider_name: str) -> None:
        self._provider = provider_name

    @property
    def provider(self) -> str:
        return self._provider

    def normalize(self, raw: str | dict[str, Any], context: dict[str, Any] | None = None) -> AdapterResult:
        from phenotype_thegent_core.contracts.parser import extract_tags, IncrementalXMLParser

        text = raw if isinstance(raw, str) else str(raw.get("stdout", raw.get("content", "")))
        tags = extract_tags(text)
        normalized_tags = {str(k).upper().replace("-", "_"): v for k, v in tags.items()}

        parse_errors = []

        # Check for truncation using partial state detection FIRST
        # This catches cases like <SUMMARY>running<DETAILS>work where tags extraction returns {}
        parser = IncrementalXMLParser()
        partial = parser.get_partial_state(text)

        # Determine parse errors - check truncation BEFORE checking empty tags
        if partial.get("is_truncated"):
            parse_errors.append("parse_truncated")
        elif not normalized_tags:
            parse_errors.append("no_xml_tags_detected")

        # Early return for empty/invalid cases
        if not normalized_tags:
            return AdapterResult(
                csm=CanonicalStructuredMessage(
                    task_id=(context or {}).get("task_id", ""),
                    run_id=(context or {}).get("run_id", ""),
                    status=CSMStatus.PENDING,
                    source_contract="xml-tags",
                    raw_payload={},
                ),
                confidence=0.0,
                parse_errors=parse_errors,
                source_provider=self._provider,
            )

        # Mapping common tags to CSM (case-insensitive keys from extract_tags)
        # Handle both snake_case (impl) and PascalCase (docs) and UPPERCASE (standard)
        def get_tag(*aliases: str) -> str:
            for a in aliases:
                val = normalized_tags.get(a.upper().replace("-", "_"))
                if val is not None:
                    return val
            return ""

        status_raw = get_tag("STATUS", "TASK_STATUS").lower()
        status_map = {
            "pending": CSMStatus.PENDING,
            "in_progress": CSMStatus.IN_PROGRESS,
            "completed": CSMStatus.COMPLETED,
            "failed": CSMStatus.FAILED,
            "done": CSMStatus.COMPLETED,
            "blocked": CSMStatus.BLOCKED,
            "cancelled": CSMStatus.CANCELLED,
            "skipped": CSMStatus.CANCELLED,
        }

        progress_val = get_tag("PROGRESS", "TASK_PROGRESS", "PERCENT_COMPLETE").rstrip("%")
        try:
            progress = float(progress_val) / 100.0 if float(progress_val) > 1.0 else float(progress_val)
        except ValueError:
            progress = 1.0 if status_map.get(status_raw, CSMStatus.PENDING) == CSMStatus.COMPLETED else 0.0

        csm = CanonicalStructuredMessage(
            task_id=get_tag("TASK_ID", "TASKID") or (context or {}).get("task_id", ""),
            run_id=(context or {}).get("run_id", ""),
            status=status_map.get(status_raw, CSMStatus.PENDING),
            progress=progress,
            objective=get_tag("OBJECTIVE", "TASK_OBJECTIVE"),
            summary=get_tag("SUMMARY", "TASK_SUMMARY", "TASK_UPDATE", "TASKUPDATE"),
            actions_completed=get_tag("ACTIONS_COMPLETED").split("\n") if get_tag("ACTIONS_COMPLETED") else [],
            issues=get_tag("ISSUES", "TASK_ISSUES").split("\n") if get_tag("ISSUES", "TASK_ISSUES") else [],
            next_steps=get_tag("NEXT_STEPS", "TASK_NEXT_STEPS").split("\n")
            if get_tag("NEXT_STEPS", "TASK_NEXT_STEPS")
            else [],
            source_contract="xml-tags",
            raw_payload=normalized_tags,
        )

        issues = validate_csm(csm)
        # WP-7007: Fallback confidence scoring and downgrade path
        # Base confidence for XML success is 1.0.
        # If there are semantic issues, reduce.
        confidence = 1.0
        if issues:
            confidence -= 0.2 * len(issues)

        # Check for structural downgrades (e.g. missing tags that are normally expected)
        if not normalized_tags.get("SUMMARY"):
            confidence -= 0.3  # Heavy penalty for missing summary

        return AdapterResult(
            csm=csm, confidence=max(0.1, confidence), parse_errors=issues, source_provider=self._provider
        )


class GenericOutputAdapter:
    """Default adapter using output_parser.extract_condensed for all providers."""

    def __init__(self, provider: str) -> None:
        self._provider = provider

    @property
    def provider(self) -> str:
        return self._provider

    def normalize(self, raw: str | dict[str, Any], context: dict[str, Any] | None = None) -> AdapterResult:
        from phenotype_thegent_core.output_parser import extract_condensed

        if isinstance(raw, str):
            summary = extract_condensed(raw)
        else:
            text = str(raw.get("content", raw.get("text", raw)))
            summary = extract_condensed(text) if text else str(raw)

        run_id = (context or {}).get("run_id", "")
        chunk_id = (context or {}).get("chunk_id", "")

        return AdapterResult(
            csm=CanonicalStructuredMessage(
                summary=summary,
                status=CSMStatus.COMPLETED,
                phase=CSMPhase.UNKNOWN,
                source_contract="plain",
                run_id=run_id,
                chunk_id=chunk_id,
            ),
            confidence=0.7,
            source_provider=self._provider,
        )


# Registry of provider adapters: provider -> adapter instance
ADAPTER_REGISTRY: dict[str, OutputAdapter] = {}

# Default adapters for common providers (use GenericOutputAdapter until provider-specific ones exist)
_DEFAULT_PROVIDERS = ("gemini", "copilot", "codex", "claude", "cursor-agent", "antigravity", "minimax", "cliproxy")


def _ensure_default_adapters() -> None:
    """Register GenericOutputAdapter for providers that have no custom adapter."""
    for p in _DEFAULT_PROVIDERS:
        if p not in ADAPTER_REGISTRY:
            register_adapter(p, GenericOutputAdapter(p))


def register_adapter(provider: str, adapter: OutputAdapter) -> None:
    """Register an output adapter for a provider."""
    ADAPTER_REGISTRY[provider] = adapter


# Register default XML adapters (after registry + registration function are defined)
for p in ["copilot", "gemini", "claude", "codex", "cursor", "cursor-agent", "antigravity"]:
    register_adapter(p, XMLOutputAdapter(p))


def get_adapter(provider: str) -> OutputAdapter | None:
    """Get adapter for provider, or None if not registered."""
    return ADAPTER_REGISTRY.get(provider)


def normalize_output(
    provider: str,
    raw: str | dict[str, Any],
    context: dict[str, Any] | None = None,
    allow_fallback: bool = True,
) -> AdapterResult:
    """Normalize provider output via registered adapter, or fallback to plain extraction.

    If no adapter is registered or if adapter fails and allow_fallback is True,
    returns a best-effort CSM.
    """
    _ensure_default_adapters()
    adapter = get_adapter(provider)
    res = None
    if adapter:
        try:
            res = adapter.normalize(raw, context)
            if not res.parse_errors:
                return res
            # If it's just truncated, return the adapter result (likely PENDING/IN_PROGRESS)
            # instead of falling back to COMPLETED
            if "parse_truncated" in res.parse_errors:
                return res
        except Exception as e:
            _log.warning("Adapter %s failed: %s", provider, e)

    if not allow_fallback:
        from phenotype_thegent_core.contracts.validation import SemanticValidationError

        raise SemanticValidationError(f"Normalization failed for {provider} and fallback is disabled.")

    # Fallback: minimal CSM from plain text
    from phenotype_thegent_core.output_parser import extract_condensed

    text = raw if isinstance(raw, str) else str(raw.get("stdout", raw.get("content", str(raw))))
    summary = extract_condensed(text)

    return AdapterResult(
        csm=CanonicalStructuredMessage(
            task_id=(context or {}).get("task_id", ""),
            run_id=(context or {}).get("run_id", ""),
            summary=summary,
            status=CSMStatus.COMPLETED,
            progress=1.0,
            phase=CSMPhase.UNKNOWN,
            source_contract="fallback-plain",
        ),
        confidence=0.3 if res else 0.5,  # Lower confidence if adapter actually failed
        source_provider=provider,
        parse_errors=res.parse_errors if res else ["No adapter found"],
    )


import logging

_log = logging.getLogger(__name__)
