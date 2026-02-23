"""CLI output formatting."""

from __future__ import annotations

import json
from typing import Literal

from pydantic import BaseModel


class CLIOutput(BaseModel):
    """All CLI output formatted via this class."""

    status: Literal["pending", "running", "success", "error", "partial"]
    result: str | dict
    timing_ms: int = 0
    agent_id: str | None = None
    session_id: str | None = None

    def to_pretty_print(self) -> str:
        """Render to terminal."""
        if self.status == "error":
            return f"Error: {self.result}"
        return str(self.result)

    def to_json(self) -> str:
        """Render as JSON for piping."""
        return self.model_dump_json(indent=2)


def format_output(
    status: Literal["pending", "running", "success", "error", "partial"],
    result: str | dict,
    agent_id: str | None = None,
    session_id: str | None = None,
    timing_ms: int = 0,
) -> CLIOutput:
    """Create a CLIOutput instance."""
    return CLIOutput(
        status=status,
        result=result,
        agent_id=agent_id,
        session_id=session_id,
        timing_ms=timing_ms,
    )
