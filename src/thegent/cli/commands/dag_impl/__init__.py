"""Stub module."""
from dataclasses import dataclass


@dataclass
class DagDocument:
    """Document representing a DAG."""
    name: str = ""
    nodes: list = None

    def __post_init__(self) -> None:
        if self.nodes is None:
            self.nodes = []


__all__ = ["DagDocument"]
