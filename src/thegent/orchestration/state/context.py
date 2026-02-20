"""Context management and semantic compression for thegent (WP-5001)."""

import logging
from pathlib import Path
from typing import Any

from thegent.execution import ContinuityPacket

_log = logging.getLogger(__name__)


class ContextCompressor:
    """WP-5001: Manages L1-L4 memory tiers and triggers semantic compression."""

    def __init__(self, session_dir: Path, threshold_pct: float = 0.85) -> None:
        self.session_dir = session_dir
        self.threshold_pct = threshold_pct
        self.cache_path = session_dir / "semantic_cache.jsonl"

    def should_compress(self, current_tokens: int, max_tokens: int) -> bool:
        """True if current token usage exceeds threshold."""
        if max_tokens <= 0:
            return False
        return (current_tokens / max_tokens) >= self.threshold_pct

    def generate_continuity_packet(
        self, intent: str, decisions: list[str], risks: list[str], context_files: list[Path]
    ) -> ContinuityPacket:
        """Create a compressed essence of progress for handoffs."""
        import hashlib

        hashes = {}
        for f in context_files:
            if f.exists():
                content = f.read_bytes()
                hashes[str(f)] = hashlib.sha256(content).hexdigest()

        packet = ContinuityPacket(
            intent=intent,
            decisions=decisions,
            risks=risks,
            context_hashes=hashes,
            token_count=len(intent.split()) + sum(len(d.split()) for d in decisions),  # rough estimate
        )

        # Persist to L2 (Short-term memory)
        self._persist_to_l2(packet)
        return packet

    def _persist_to_l2(self, packet: ContinuityPacket) -> None:
        """Save packet to Redis (simulated via JSONL for this phase)."""
        l2_path = self.session_dir / "l2_memory.jsonl"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        with l2_path.open("a", encoding="utf-8") as f:
            f.write(packet.model_dump_json() + "\n")

    def prune_context(self, conversation: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """WP-5001: Priority-based pruning of conversation history."""
        if not conversation:
            return []

        # 1. Always retain system prompt and last 3 interactions
        retained = conversation[:1]  # System prompt
        tail = conversation[-6:]  # Last 3 user/assistant pairs

        # 2. Middle part: identify candidates for pruning (e.g. verbose tool results)
        middle = conversation[1:-6]
        pruned_middle = []
        for msg in middle:
            if msg.get("role") == "tool" and len(msg.get("content", "")) > 1000:
                # Compress verbose tool results
                pruned_middle.append(
                    {
                        "role": "tool",
                        "content": f"[VERBOSE OUTPUT COMPRESSED: {len(msg['content'])} chars]",
                        "tool_call_id": msg.get("tool_call_id"),
                    }
                )
            else:
                pruned_middle.append(msg)

        return retained + pruned_middle + tail
