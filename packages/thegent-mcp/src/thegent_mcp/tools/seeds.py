"""MCP tools for idea seed detection and storage.

Provides tools for:
- Detecting seeds in text using pattern matching
- Storing seeds persistently in JSONL format
- Querying and managing seed ideas
- Exporting seeds to markdown
"""

import json
import logging
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

from fastmcp.tools.tool import ToolResult

if TYPE_CHECKING:
    from fastmcp import FastMCP

from datetime import UTC

from thegent.cli.commands.impl import _resolve_cwd
from thegent.memory.seed_detector import SeedDetector, SeedSource
from thegent.memory.seed_storage import SeedStorage

_log = logging.getLogger(__name__)


async def _ctx_info(ctx: Any, message: str) -> None:
    """Send an info log message via FastMCP Context if available, else Python logging."""
    if ctx is not None:
        try:
            await ctx.info(message)
            return
        except Exception:
            pass
    _log.info(message)


async def _ctx_warning(ctx: Any, message: str) -> None:
    """Send a warning log message via FastMCP Context if available, else Python logging."""
    if ctx is not None:
        try:
            await ctx.warning(message)
            return
        except Exception:
            pass
    _log.warning(message)


def register_seed_tools(mcp: "FastMCP") -> None:
    """Register seed detection and storage tools."""
    # Import CurrentContext for FastMCP dependency injection
    try:
        from fastmcp.server.dependencies import CurrentContext

        _current_context = CurrentContext()
    except Exception:
        _current_context = None  # type: ignore[assignment]

    @mcp.tool(annotations={"readOnlyHint": False, "idempotentHint": False})
    async def thegent_seed_detect(
        text: str,
        source: str = "user_prompt",
        use_llm: bool = False,
        ctx: Any = _current_context,
    ) -> ToolResult:
        """
        Detect idea seeds in text using pattern matching.

        Seed ideas are nascent concepts, half-formed requirements, design sketches,
        or problem statements that could grow into full features.

        Pattern detection:
        - Explicit markers: "What if...", "Consider...", "We should..."
        - Code quality: TODO, FIXME, XXX comments
        - Design keywords: architecture, refactor, optimize, performance, security

        Args:
            text: Input text to analyze (max 5000 chars)
            source: Source of text (user_prompt, agent_output, claude_history, etc.)
            use_llm: Use LLM for classification (slower but catches non-obvious seeds)

        Returns:
            Detected seeds with metadata
        """
        start = time.perf_counter()

        if not text or not isinstance(text, str):
            return ToolResult(
                content=json.dumps({"error": "Invalid input", "seeds": [], "count": 0}),
                structured_content={"error": "Invalid input", "seeds": [], "count": 0},
                meta={"execution_time_ms": 0},
            )

        try:
            await _ctx_info(ctx, f"thegent_seed_detect source={source} use_llm={use_llm} text_len={len(text)}")
            # Map source string to SeedSource enum
            source_map = {
                "user_prompt": SeedSource.USER_PROMPT,
                "agent_output": SeedSource.AGENT_OUTPUT,
                "claude_history": SeedSource.CLAUDE_HISTORY,
                "codex_history": SeedSource.CODEX_HISTORY,
                "cursor_transcript": SeedSource.CURSOR_TRANSCRIPT,
                "manual": SeedSource.MANUAL,
            }
            seed_source = source_map.get(source, SeedSource.MANUAL)

            detector = SeedDetector(use_llm=use_llm)
            seeds = detector.detect_seeds(text[:5000], seed_source)

            # Extract flags if present
            flags = SeedDetector.extract_flags(text)

            result = {
                "count": len(seeds),
                "flags": flags,
                "seeds": [s.to_dict() for s in seeds],
            }

            await _ctx_info(ctx, f"thegent_seed_detect found {len(seeds)} seed(s)")
            elapsed = int((time.perf_counter() - start) * 1000)
            return ToolResult(
                content=json.dumps(result),
                structured_content=result,
                meta={"execution_time_ms": elapsed},
            )

        except Exception as e:
            await _ctx_warning(ctx, f"thegent_seed_detect error: {e}")
            _log.exception("Seed detection error")
            return ToolResult(
                content=json.dumps({"error": str(e), "seeds": [], "count": 0}),
                structured_content={"error": str(e), "seeds": [], "count": 0},
                meta={"execution_time_ms": 0},
            )

    @mcp.tool(annotations={"readOnlyHint": False, "idempotentHint": False})
    async def thegent_seed_store(
        text: str,
        source: str = "manual",
        confidence: float = 0.5,
        tags: list[str] | None = None,
        cd: str | None = None,
        ctx: Any = _current_context,
    ) -> ToolResult:
        """
        Store an idea seed in persistent JSONL storage.

        Seeds are stored in docs/research/seeds.jsonl (one JSON object per line).

        Args:
            text: Seed text (max 500 chars stored, full text in context)
            source: Source of seed
            confidence: Confidence level 0.0-1.0
            tags: Optional tags (e.g., ["performance", "security"])
            cd: Project directory (auto-detected if not provided)

        Returns:
            Stored seed with ID and metadata
        """
        start = time.perf_counter()

        if not text or not isinstance(text, str):
            return ToolResult(
                content=json.dumps({"error": "Invalid input", "seed": None}),
                structured_content={"error": "Invalid input", "seed": None},
                meta={"execution_time_ms": 0},
            )

        try:
            await _ctx_info(ctx, f"thegent_seed_store source={source} confidence={confidence}")
            root = _resolve_cwd(Path(cd) if cd else None)
            if not root:
                return ToolResult(
                    content=json.dumps({"error": "No project root", "remediation": "Set cwd or cd"}),
                    structured_content={
                        "error": "No project root",
                        "remediation": "Set cwd or cd",
                    },
                    meta={"execution_time_ms": 0},
                )

            # Resolve storage path
            storage_path = root / "docs" / "research" / "seeds.jsonl"
            storage = SeedStorage(storage_path=storage_path)

            # Detect seeds in text to get metadata
            detector = SeedDetector()
            detected_seeds = detector.detect_seeds(text, SeedSource.MANUAL)

            if detected_seeds:
                # Use detected seed but override with provided params
                seed = detected_seeds[0]
                seed.confidence = confidence
                if tags:
                    seed.tags = tags
            else:
                # Create manual seed
                from datetime import datetime

                from thegent.memory.seed_detector import Seed

                seed = Seed(
                    id="",  # Will be set in detector
                    text=text[:500],
                    source=SeedSource.MANUAL,
                    confidence=confidence,
                    timestamp=datetime.now(UTC).isoformat(),
                    tags=tags or [],
                    detected_by="manual",
                )

            # Store seed
            seed_id = storage.store_seed(seed)

            await _ctx_info(ctx, f"thegent_seed_store stored seed_id={seed_id}")
            result = {
                "seed_id": seed_id,
                "stored": True,
                "seed": seed.to_dict(),
            }

            elapsed = int((time.perf_counter() - start) * 1000)
            return ToolResult(
                content=json.dumps(result),
                structured_content=result,
                meta={"execution_time_ms": elapsed},
            )

        except Exception as e:
            await _ctx_warning(ctx, f"thegent_seed_store error: {e}")
            _log.exception("Seed storage error")
            return ToolResult(
                content=json.dumps({"error": str(e), "seed": None}),
                structured_content={"error": str(e), "seed": None},
                meta={"execution_time_ms": 0},
            )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    async def thegent_seed_list(
        status: str = "new",
        tag: str | None = None,
        source: str | None = None,
        cd: str | None = None,
        ctx: Any = _current_context,
    ) -> ToolResult:
        """
        List stored seeds with optional filtering.

        Args:
            status: Filter by status (new, developing, implemented, archived)
            tag: Filter by tag (e.g., "performance", "security")
            source: Filter by source
            cd: Project directory

        Returns:
            List of matching seeds
        """
        start = time.perf_counter()

        try:
            await _ctx_info(ctx, f"thegent_seed_list status={status} tag={tag} source={source}")
            root = _resolve_cwd(Path(cd) if cd else None)
            if not root:
                return ToolResult(
                    content=json.dumps({"error": "No project root", "seeds": []}),
                    structured_content={"error": "No project root", "seeds": []},
                    meta={"execution_time_ms": 0},
                )

            storage_path = root / "docs" / "research" / "seeds.jsonl"
            storage = SeedStorage(storage_path=storage_path)

            seeds = storage.load_seeds()
            total = len(seeds)
            await _ctx_info(ctx, f"thegent_seed_list loaded {total} seed(s) before filtering")

            # Apply filters
            if status:
                seeds = [s for s in seeds if s.status == status]
            if tag:
                seeds = [s for s in seeds if tag in s.tags]
            if source:
                seeds = [s for s in seeds if s.source == source]

            result = {
                "count": len(seeds),
                "seeds": [s.to_dict() for s in seeds],
            }

            elapsed = int((time.perf_counter() - start) * 1000)
            return ToolResult(
                content=json.dumps(result),
                structured_content=result,
                meta={"execution_time_ms": elapsed},
            )

        except Exception as e:
            await _ctx_warning(ctx, f"thegent_seed_list error: {e}")
            _log.exception("Seed listing error")
            return ToolResult(
                content=json.dumps({"error": str(e), "seeds": []}),
                structured_content={"error": str(e), "seeds": []},
                meta={"execution_time_ms": 0},
            )

    @mcp.tool(annotations={"readOnlyHint": False, "idempotentHint": False})
    def thegent_seed_update(
        seed_id: str,
        status: str | None = None,
        tags: list[str] | None = None,
        context: str | None = None,
        cd: str | None = None,
    ) -> ToolResult:
        """
        Update seed metadata.

        Args:
            seed_id: Seed ID to update
            status: New status (new, developing, implemented, archived)
            tags: New tags
            context: Additional context
            cd: Project directory

        Returns:
            Updated seed or error
        """
        start = time.perf_counter()

        try:
            root = _resolve_cwd(Path(cd) if cd else None)
            if not root:
                return ToolResult(
                    content=json.dumps({"error": "No project root", "updated": False}),
                    structured_content={"error": "No project root", "updated": False},
                    meta={"execution_time_ms": 0},
                )

            storage_path = root / "docs" / "research" / "seeds.jsonl"
            storage = SeedStorage(storage_path=storage_path)

            # Build update dict
            update_kwargs = {}
            if status:
                update_kwargs["status"] = status
            if tags:
                update_kwargs["tags"] = tags
            if context:
                update_kwargs["context"] = context

            updated = storage.update_seed(seed_id, **update_kwargs)

            if updated:
                seed = storage.find_by_id(seed_id)
                result = {
                    "updated": True,
                    "seed_id": seed_id,
                    "seed": seed.to_dict() if seed else None,
                }
            else:
                result = {
                    "updated": False,
                    "error": f"Seed {seed_id} not found",
                }

            elapsed = int((time.perf_counter() - start) * 1000)
            return ToolResult(
                content=json.dumps(result),
                structured_content=result,
                meta={"execution_time_ms": elapsed},
            )

        except Exception as e:
            _log.exception("Seed update error")
            return ToolResult(
                content=json.dumps({"error": str(e), "updated": False}),
                structured_content={"error": str(e), "updated": False},
                meta={"execution_time_ms": 0},
            )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def thegent_seed_export(
        cd: str | None = None,
    ) -> ToolResult:
        """
        Export seeds to markdown format.

        Generates a human-readable markdown file with all seeds grouped by status.

        Args:
            cd: Project directory

        Returns:
            Markdown content and export status
        """
        start = time.perf_counter()

        try:
            root = _resolve_cwd(Path(cd) if cd else None)
            if not root:
                return ToolResult(
                    content=json.dumps({"error": "No project root", "markdown": None}),
                    structured_content={"error": "No project root", "markdown": None},
                    meta={"execution_time_ms": 0},
                )

            storage_path = root / "docs" / "research" / "seeds.jsonl"
            storage = SeedStorage(storage_path=storage_path)

            # Export to markdown
            output_path = root / "docs" / "research" / "seeds.md"
            markdown = storage.export_markdown(output_path)

            result = {
                "exported": True,
                "output_path": str(output_path),
                "markdown": markdown,
            }

            elapsed = int((time.perf_counter() - start) * 1000)
            return ToolResult(
                content=json.dumps(result),
                structured_content=result,
                meta={"execution_time_ms": elapsed},
            )

        except Exception as e:
            _log.exception("Seed export error")
            return ToolResult(
                content=json.dumps({"error": str(e), "markdown": None}),
                structured_content={"error": str(e), "markdown": None},
                meta={"execution_time_ms": 0},
            )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def thegent_seed_stats(
        cd: str | None = None,
    ) -> ToolResult:
        """
        Get seed storage statistics.

        Returns:
            Stats: total count, breakdown by status/source/confidence

        Args:
            cd: Project directory

        Returns:
            Storage statistics
        """
        start = time.perf_counter()

        try:
            root = _resolve_cwd(Path(cd) if cd else None)
            if not root:
                return ToolResult(
                    content=json.dumps({"error": "No project root", "stats": {}}),
                    structured_content={"error": "No project root", "stats": {}},
                    meta={"execution_time_ms": 0},
                )

            storage_path = root / "docs" / "research" / "seeds.jsonl"
            storage = SeedStorage(storage_path=storage_path)

            stats = storage.get_stats()

            result = {
                "stats": stats,
            }

            elapsed = int((time.perf_counter() - start) * 1000)
            return ToolResult(
                content=json.dumps(result),
                structured_content=result,
                meta={"execution_time_ms": elapsed},
            )

        except Exception as e:
            _log.exception("Seed stats error")
            return ToolResult(
                content=json.dumps({"error": str(e), "stats": {}}),
                structured_content={"error": str(e), "stats": {}},
                meta={"execution_time_ms": 0},
            )

    _ = (
        thegent_seed_detect,
        thegent_seed_store,
        thegent_seed_list,
        thegent_seed_update,
        thegent_seed_export,
        thegent_seed_stats,
    )
