# MIGRATION NOTE: Migrate to cliproxyapi-plusplus Go SDK
from __future__ import annotations

import logging
from typing import Any

_log = logging.getLogger(__name__)


class ResponsesStreamState:
    """Stateful transformer: Chat Completions SSE -> Responses API v2 event sequence.

    Codex 0.104.0 requires this exact 8-event sequence:
      response.created           (once, carries response.id)
      response.output_item.added (once)
      response.content_part.added (once)
      response.output_text.delta (repeating, per token)
      response.output_text.done  (once)
      response.content_part.done (once)
      response.output_item.done  (once)
      response.completed         (once, full response object + usage)
    """

    def __init__(self, model: str = "proxy") -> None:
        import uuid

        self.response_id = f"resp_{uuid.uuid4().hex[:24]}"
        self.item_id = f"item_{uuid.uuid4().hex[:16]}"
        self.model = model
        self.seq = 0
        self._emitted_created = False
        self._emitted_item = False
        self._emitted_part = False
        self._full_text: list[str] = []
        self._usage: dict[str, Any] | None = None
        # Tool call state — GW-07: track per-index accumulation
        self._tool_calls: dict[int, dict[str, Any]] = {}  # index → {id, name, args_chunks}

    def _next_seq(self) -> int:
        s = self.seq
        self.seq += 1
        return s

    def preamble_events(self) -> list[dict[str, Any]]:
        """Events emitted before any delta: created, output_item.added, content_part.added."""
        import time

        events: list[dict[str, Any]] = []
        if not self._emitted_created:
            events.append(
                {
                    "type": "response.created",
                    "sequence_number": self._next_seq(),
                    "response": {
                        "id": self.response_id,
                        "object": "response",
                        "status": "in_progress",
                        "model": self.model,
                        "output": [],
                        "created_at": int(time.time()),
                    },
                }
            )
            self._emitted_created = True
        if not self._emitted_item:
            events.append(
                {
                    "type": "response.output_item.added",
                    "sequence_number": self._next_seq(),
                    "response_id": self.response_id,
                    "output_index": 0,
                    "item": {
                        "id": self.item_id,
                        "object": "response_output_item",
                        "type": "message",
                        "status": "in_progress",
                        "role": "assistant",
                        "content": [],
                    },
                }
            )
            self._emitted_item = True
        if not self._emitted_part:
            events.append(
                {
                    "type": "response.content_part.added",
                    "sequence_number": self._next_seq(),
                    "response_id": self.response_id,
                    "item_id": self.item_id,
                    "output_index": 0,
                    "content_index": 0,
                    "part": {"type": "text", "text": ""},
                }
            )
            self._emitted_part = True
        return events

    def delta_event(self, text: str) -> dict[str, Any]:
        """One response.output_text.delta event per token."""
        self._full_text.append(text)
        return {
            "type": "response.output_text.delta",
            "sequence_number": self._next_seq(),
            "response_id": self.response_id,
            "item_id": self.item_id,
            "output_index": 0,
            "content_index": 0,
            "delta": text,
        }

    def tool_call_delta_events(self, tool_calls: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Convert Chat Completions tool_call deltas to Responses API events — GW-07."""
        import uuid

        events: list[dict[str, Any]] = []
        for tc in tool_calls:
            idx = tc.get("index", 0)
            if idx not in self._tool_calls:
                call_id = tc.get("id") or f"call_{uuid.uuid4().hex[:16]}"
                fn = tc.get("function", {})
                self._tool_calls[idx] = {"call_id": call_id, "name": fn.get("name", ""), "args_chunks": []}
                item_id = f"item_{uuid.uuid4().hex[:16]}"
                self._tool_calls[idx]["item_id"] = item_id
                events.append(
                    {
                        "type": "response.output_item.added",
                        "sequence_number": self._next_seq(),
                        "response_id": self.response_id,
                        "output_index": 1 + idx,
                        "item": {
                            "id": item_id,
                            "object": "response_output_item",
                            "type": "function_call",
                            "status": "in_progress",
                            "call_id": call_id,
                            "name": self._tool_calls[idx]["name"],
                            "arguments": "",
                        },
                    }
                )
            fn = tc.get("function", {})
            args_chunk = fn.get("arguments", "")
            if args_chunk:
                self._tool_calls[idx]["args_chunks"].append(args_chunk)
                events.append(
                    {
                        "type": "response.function_call_arguments.delta",
                        "sequence_number": self._next_seq(),
                        "response_id": self.response_id,
                        "item_id": self._tool_calls[idx]["item_id"],
                        "output_index": 1 + idx,
                        "call_id": self._tool_calls[idx]["call_id"],
                        "delta": args_chunk,
                    }
                )
        return events

    def tool_call_closing_events(self) -> list[dict[str, Any]]:
        """Emit done events for all accumulated tool calls."""
        events: list[dict[str, Any]] = []
        for idx, tc in sorted(self._tool_calls.items()):
            full_args = "".join(tc["args_chunks"])
            events.append(
                {
                    "type": "response.function_call_arguments.done",
                    "sequence_number": self._next_seq(),
                    "response_id": self.response_id,
                    "item_id": tc["item_id"],
                    "output_index": 1 + idx,
                    "call_id": tc["call_id"],
                    "arguments": full_args,
                }
            )
            events.append(
                {
                    "type": "response.output_item.done",
                    "sequence_number": self._next_seq(),
                    "response_id": self.response_id,
                    "output_index": 1 + idx,
                    "item": {
                        "id": tc["item_id"],
                        "object": "response_output_item",
                        "type": "function_call",
                        "status": "completed",
                        "call_id": tc["call_id"],
                        "name": tc["name"],
                        "arguments": full_args,
                    },
                }
            )
        return events

    def set_usage(self, usage: dict[str, Any]) -> None:
        self._usage = usage

    def closing_events(self) -> list[dict[str, Any]]:
        """Events after all deltas: done, part done, item done, response.completed.

        OR-14: Includes usage.cost in response.completed when available from
        OpenRouter's total_cost field in the upstream usage object.
        """
        import time

        full_text = "".join(self._full_text)
        usage = self._usage or {}
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        # OR-14: include actual cost when OpenRouter reports it
        usage_block: dict[str, Any] = {
            "input_tokens": prompt_tokens,
            "output_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        }
        total_cost = usage.get("total_cost")
        if total_cost is not None:
            usage_block["cost"] = total_cost
            # Wire into cost tracker so budget enforcement sees actual spend
            try:
                from thegent.utils.routing_impl.cost_tracker import get_cost_tracker

                get_cost_tracker().track(
                    provider="openrouter",
                    model=self.model,
                    usage={"prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens},
                    cost=float(total_cost),
                    latency_ms=0.0,
                )
            except Exception:  # cost tracking is best-effort; never break the response path
                _log.debug("OR-14: cost tracker update skipped", exc_info=True)

        return [
            {
                "type": "response.output_text.done",
                "sequence_number": self._next_seq(),
                "response_id": self.response_id,
                "item_id": self.item_id,
                "output_index": 0,
                "content_index": 0,
                "text": full_text,
            },
            {
                "type": "response.content_part.done",
                "sequence_number": self._next_seq(),
                "response_id": self.response_id,
                "item_id": self.item_id,
                "output_index": 0,
                "content_index": 0,
                "part": {"type": "text", "text": full_text},
            },
            {
                "type": "response.output_item.done",
                "sequence_number": self._next_seq(),
                "response_id": self.response_id,
                "output_index": 0,
                "item": {
                    "id": self.item_id,
                    "object": "response_output_item",
                    "type": "message",
                    "status": "completed",
                    "role": "assistant",
                    "content": [{"type": "text", "text": full_text}],
                },
            },
            {
                "type": "response.completed",
                "sequence_number": self._next_seq(),
                "response": {
                    "id": self.response_id,
                    "object": "response",
                    "status": "completed",
                    "model": self.model,
                    "output": [
                        {
                            "id": self.item_id,
                            "object": "response_output_item",
                            "type": "message",
                            "status": "completed",
                            "role": "assistant",
                            "content": [{"type": "text", "text": full_text}],
                        }
                    ],
                    "created_at": int(time.time()),
                    "usage": usage_block,
                },
            },
        ]
