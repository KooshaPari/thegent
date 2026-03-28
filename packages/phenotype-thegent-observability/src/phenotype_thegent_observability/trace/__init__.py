"""Deterministic replay system for agent execution traces.

This package provides:
- TraceRecorder: Record agent execution to JSONL traces
- ReplayEngine: Replay traces with mocked LLM/file I/O
- DiffAnalyzer: Compare original vs. replayed execution
- TraceVariator: Generate parameterized trace variations
"""

from .integration import (
    ExecutionMetrics,
    TracedAgentRunner,
    TraceRecordingContext,
    create_traced_agent_runner,
    estimate_trace_overhead,
)
from .recorder import (
    RecorderConfig,
    RedactionConfig,
    TraceCleanup,
    TraceRecorder,
    TruncationConfig,
)
from .schema import (
    DecisionRecord,
    SessionRecord,
    ToolCallRecord,
    TraceFile,
    TraceRecord,
)

__all__ = [
    "DecisionRecord",
    "ExecutionMetrics",
    "RecorderConfig",
    "RedactionConfig",
    "SessionRecord",
    # Schema
    "ToolCallRecord",
    "TraceCleanup",
    "TraceFile",
    "TraceRecord",
    # Recorder
    "TraceRecorder",
    "TraceRecordingContext",
    # Integration
    "TracedAgentRunner",
    "TruncationConfig",
    "create_traced_agent_runner",
    "estimate_trace_overhead",
    "integration",
    "recorder",
    # Modules
    "schema",
]
