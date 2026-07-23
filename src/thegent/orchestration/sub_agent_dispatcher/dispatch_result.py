"""DispatchResult — carried back from a runner to the executor."""

from __future__ import annotations


class DispatchResult:
    """Result of dispatching a single :class:`PlanNode`.

    Constructed by :class:`SubAgentDispatcher.dispatch_plan` consumers or by
    the legacy :class:`SubAgentDispatcher.execute_task` path.  Fields are
    positional but most callers use keyword arguments for clarity.
    """

    __slots__ = ("error", "node_id", "output", "success")

    def __hash__(self) -> int:  # noqa: PLW1641 — explicit eq/hash pair
        return hash((self.node_id, self.output, self.success, self.error))

    def __init__(
        self,
        node_id: str,
        output: str = "",
        success: bool = True,
        error: str = "",
    ) -> None:
        if not isinstance(node_id, str) or not node_id:
            raise ValueError("node_id must be a non-empty string")
        if not isinstance(output, str):
            raise TypeError(f"output must be str, got {type(output).__name__}")
        if not isinstance(success, bool):
            raise TypeError(f"success must be bool, got {type(success).__name__}")
        if not isinstance(error, str):
            raise TypeError(f"error must be str, got {type(error).__name__}")
        self.node_id = node_id
        self.output = output
        self.success = success
        self.error = error

    def __repr__(self) -> str:
        return (
            f"DispatchResult(node_id={self.node_id!r}, "
            f"output={self.output!r}, success={self.success!r}, "
            f"error={self.error!r})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DispatchResult):
            return NotImplemented
        return (
            self.node_id == other.node_id
            and self.output == other.output
            and self.success == other.success
            and self.error == other.error
        )
