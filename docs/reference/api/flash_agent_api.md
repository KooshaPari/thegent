# flash_agent API Reference

> **Source**: `src/thegent/agents/flash_agent.py`

Flash agent — ultra-short-lived agent that executes a single focused task and self-terminates.

Ported from the dex flash agent pattern. A FlashAgent fires a single LLM call via litellm,
enforces a strict timeout, and returns a structured result. Designed for sub-30-second
focused tasks without persistent state.

FR Traceability: FR-AGT-020 (flash agent lifecycle)

---

## FlashAgent

Ultra-short-lived agent that executes a single focused task via a single LLM call.

Designed for sub-30-second focused tasks. Fires one litellm.acompletion call,
enforces timeout via asyncio.wait_for, and self-terminates.

---

## FlashAgentConfig

Configuration for a flash agent execution.

---

## FlashAgentResult

Result of a flash agent execution.

---

