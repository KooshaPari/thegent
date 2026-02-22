"""Detect and classify idea seeds from user prompts and agent outputs.

Seed ideas are nascent concepts, half-formed requirements, design sketches,
problem statements that could grow into full features.

Provides:
- Pattern matching for explicit seed signals
- Optional LLM-based classification for non-obvious seeds
- Metadata extraction (source, timestamp, confidence)
"""

import logging
import re
from dataclasses import dataclass
from datetime import UTC
from enum import Enum
from typing import ClassVar

_log = logging.getLogger(__name__)


class SeedConfidence(Enum):
    """Confidence level of seed detection."""

    HIGH = 0.9  # Explicit seed markers
    MEDIUM = 0.6  # Strong indicators (TODO, FIXME, etc.)
    LOW = 0.3  # Weak indicators, LLM-detected


class SeedSource(Enum):
    """Source of the seed idea."""

    USER_PROMPT = "user_prompt"
    AGENT_OUTPUT = "agent_output"
    CLAUDE_HISTORY = "claude_history"
    CODEX_HISTORY = "codex_history"
    CURSOR_TRANSCRIPT = "cursor_transcript"
    MANUAL = "manual"


@dataclass
class Seed:
    """Represents a detected idea seed."""

    id: str  # UUID or generated ID
    text: str  # The seed idea text
    source: SeedSource  # Where it came from
    confidence: float  # 0.0 to 1.0
    timestamp: str  # ISO 8601 format
    tags: list[str]  # Optional tags (e.g., ["architecture", "performance"])
    status: str = "new"  # new, developing, implemented, archived
    context: str | None = None  # Additional context
    detected_by: str | None = None  # Detection method (pattern, llm, manual)

    def __post_init__(self) -> None:
        """Normalize source to always be a SeedSource enum."""
        if isinstance(self.source, str):
            self.source = SeedSource(self.source)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        # Ensure source is treated as enum (should be due to __post_init__)
        source_value = self.source.value if isinstance(self.source, SeedSource) else self.source
        return {
            "id": self.id,
            "text": self.text,
            "source": source_value,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
            "tags": self.tags,
            "status": self.status,
            "context": self.context,
            "detected_by": self.detected_by,
        }


class SeedDetector:
    """Detects idea seeds using pattern matching and optional LLM classification."""

    # Explicit seed markers - high confidence
    EXPLICIT_PATTERNS: ClassVar[tuple[str, ...]] = (
        r"(?i)\bwhat\s+if\b",  # What if ...
        r"(?i)\bconsider\b",  # Consider ...
        r"(?i)\bwe\s+should\b",  # We should ...
        r"(?i)\bwe\s+need\b",  # We need ...
        r"(?i)\bproposal\b",  # Proposal
        r"(?i)\bfeature\s+idea\b",  # Feature idea
        r"(?i)\bseed\s+idea\b",  # Seed idea (self-referential)
        r"(?i)\bworth\s+exploring\b",  # Worth exploring
        r"(?i)\bideally\b",  # Ideally ...
        r"(?i)\bin\s+the\s+future\b",  # In the future
        r"(?i)\beventually\b",  # Eventually
        r"(?i)\bstretch\s+goal\b",  # Stretch goal
    )

    # Code quality markers - medium confidence
    CODE_QUALITY_PATTERNS: ClassVar[tuple[str, ...]] = (
        r"^(?:[ \t]*)#\s*(?:TODO|FIXME|XXX|HACK|NOTE):",  # Code comments
        r"@pytest\.mark\.skip(?:if)?\(",  # Skipped tests
        r"\.skip\(",  # Skip markers
        r"pending|not implemented|stub",  # Common placeholders
    )

    # Design/architecture patterns - medium confidence
    DESIGN_PATTERNS: ClassVar[tuple[str, ...]] = (
        r"(?i)\barchitecture\b",
        r"(?i)\bdesign\b",
        r"(?i)\brefactor",
        r"(?i)\boptimiz",  # optimize/optimization
        r"(?i)\bscalability\b",
        r"(?i)\bperformance\b",
        r"(?i)\bsecurity\b",
        r"(?i)\breliability\b",
        r"(?i)\bmaintainability\b",
    )

    def __init__(self, use_llm: bool = False) -> None:
        """Initialize detector.

        Args:
            use_llm: Whether to use LLM for classification (requires API key)
        """
        self.use_llm = use_llm
        self._compiled_explicit = [re.compile(p) for p in self.EXPLICIT_PATTERNS]
        self._compiled_code_quality = [re.compile(p, re.MULTILINE) for p in self.CODE_QUALITY_PATTERNS]
        self._compiled_design = [re.compile(p) for p in self.DESIGN_PATTERNS]

    def detect_seeds(self, text: str, source: SeedSource) -> list[Seed]:
        """Detect seeds in text using pattern matching.

        Args:
            text: Input text to analyze
            source: Source of the text

        Returns:
            List of detected Seed objects
        """
        seeds = []

        # Check explicit patterns (highest confidence)
        for pattern in self._compiled_explicit:
            if pattern.search(text):
                seed = self._create_seed(text, source, SeedConfidence.HIGH, "explicit_marker")
                seeds.append(seed)
                break  # One seed per detection pass

        # Check code quality patterns
        if not seeds:
            for pattern in self._compiled_code_quality:
                if pattern.search(text):
                    seed = self._create_seed(text, source, SeedConfidence.MEDIUM, "code_quality_marker")
                    seeds.append(seed)
                    break

        # Check design/architecture patterns
        if not seeds:
            for pattern in self._compiled_design:
                if pattern.search(text):
                    seed = self._create_seed(text, source, SeedConfidence.MEDIUM, "design_marker")
                    seeds.append(seed)
                    break

        # Optional: LLM-based classification for non-obvious seeds
        if self.use_llm and not seeds:
            llm_seed = self._classify_with_llm(text, source)
            if llm_seed:
                seeds.append(llm_seed)

        return seeds

    def _create_seed(
        self,
        text: str,
        source: SeedSource,
        confidence: SeedConfidence,
        detection_method: str,
    ) -> Seed:
        """Create a Seed object with metadata.

        Args:
            text: Seed text
            source: Source of detection
            confidence: Confidence level
            detection_method: How it was detected

        Returns:
            Seed object
        """
        import uuid
        from datetime import datetime

        # Extract tags from text (simple heuristic)
        tags = self._extract_tags(text)

        seed_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now(UTC).isoformat()

        return Seed(
            id=seed_id,
            text=text[:500],  # Truncate to 500 chars
            source=source,
            confidence=confidence.value,
            timestamp=timestamp,
            tags=tags,
            detected_by=detection_method,
            context=text if len(text) > 500 else None,
        )

    def _extract_tags(self, text: str) -> list[str]:
        """Extract potential tags from text.

        Args:
            text: Input text

        Returns:
            List of tags
        """
        tags = []
        tag_keywords = {
            "architecture": r"(?i)\b(architecture|design|pattern)\b",
            "performance": r"(?i)\b(performance|speed|optimize|benchmark)\b",
            "security": r"(?i)\b(security|auth|encrypt|vulnerability)\b",
            "testing": r"(?i)\b(test|coverage|qa|e2e)\b",
            "documentation": r"(?i)\b(doc|readme|comment|guide)\b",
            "refactor": r"(?i)\b(refactor|clean|improve|simplify)\b",
            "api": r"(?i)\b(api|endpoint|rest|graphql)\b",
            "database": r"(?i)\b(database|db|sql|query)\b",
            "ui": r"(?i)\b(ui|ux|component|layout)\b",
            "infrastructure": r"(?i)\b(infra|deploy|container|cloud)\b",
        }

        for tag, pattern in tag_keywords.items():
            if re.search(pattern, text):
                tags.append(tag)

        return tags[:3]  # Limit to 3 tags

    def _classify_with_llm(self, text: str, source: SeedSource) -> Seed | None:
        """Classify text as seed using LLM (stub for future implementation).

        Args:
            text: Input text
            source: Source of the text

        Returns:
            Seed object if LLM classifies as seed, None otherwise
        """
        # TODO: Implement LLM classification using Claude/Anthropic API
        # For now, return None
        return None

    @staticmethod
    def extract_flags(text: str) -> dict[str, bool]:
        """Extract special flags from text (e.g., $idea, $defer, $pending).

        Args:
            text: Input text

        Returns:
            Dict with flag presence: {"idea": True, "defer": False, ...}
        """
        return {
            "idea": "$idea" in text or "#idea" in text,
            "defer": "$defer" in text or "#defer" in text,
            "pending": "$pending" in text or "#pending" in text,
            "fixme": "FIXME" in text or "fixme" in text.lower(),
            "todo": "TODO" in text or "todo" in text.lower(),
        }
