"""Pane tree management used by the UI compositor tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Pane:
    pane_id: str
    working_dir: str = "."
    is_active: bool = True
    is_leaf: bool = True


@dataclass
class PaneNode:
    pane_id: str
    is_leaf: bool = True
    direction: str | None = None
    pane: Pane | None = None
    children: list["PaneNode"] = field(default_factory=list)
    parent: "PaneNode | None" = None

    def __post_init__(self) -> None:
        if self.is_leaf and self.pane is None:
            self.pane = Pane(self.pane_id)
        if not self.is_leaf:
            self.pane = None

    def leaves(self) -> list["PaneNode"]:
        if self.is_leaf:
            return [self]
        result: list[PaneNode] = []
        for child in self.children:
            result.extend(child.leaves())
        return result


class PaneManager:
    def __init__(self) -> None:
        self.root: PaneNode | None = None
        self.focus_pane_id: str | None = None
        self.current_pane_id: str | None = None
        self._next_id = 1

    def _new_id(self) -> str:
        pane_id = f"pane-{self._next_id}"
        self._next_id += 1
        return pane_id

    def _leaves(self) -> list[PaneNode]:
        if self.root is None:
            return []
        return self.root.leaves()

    def _find(self, pane_id: str, node: PaneNode | None = None) -> PaneNode | None:
        node = self.root if node is None else node
        if node is None:
            return None
        if node.pane_id == pane_id:
            return node
        for child in node.children:
            found = self._find(pane_id, child)
            if found is not None:
                return found
        return None

    def _parent_of(self, pane_id: str, node: PaneNode | None = None) -> PaneNode | None:
        node = self.root if node is None else node
        if node is None:
            return None
        for child in node.children:
            if child.pane_id == pane_id:
                return node
            found = self._parent_of(pane_id, child)
            if found is not None:
                return found
        return None

    def get_focused_pane(self) -> PaneNode:
        if self.root is None:
            return self.create_root_pane("pane-0")
        node = self._find(self.focus_pane_id or "") or self._find(self.current_pane_id or "") or self._leaves()[0]
        self.focus_pane_id = node.pane_id
        self.current_pane_id = node.pane_id
        return node

    def get_pane_count(self) -> int:
        return len(self._leaves())

    def get_all_panes(self) -> list[Pane]:
        return [leaf.pane for leaf in self._leaves() if leaf.pane is not None]

    def get_pane_by_id(self, pane_id: str) -> PaneNode | None:
        node = self._find(pane_id)
        return node if node and node.is_leaf else None

    def create_root_pane(self, pane_id: str) -> PaneNode:
        self.root = PaneNode(pane_id)
        self.focus_pane_id = pane_id
        self.current_pane_id = pane_id
        return self.root

    def split_pane(self, direction: str) -> PaneNode:
        direction = direction.upper()
        if direction.startswith("VERT"):
            direction = "V"
        if direction.startswith("HOR"):
            direction = "H"
        if direction not in {"H", "V"}:
            raise ValueError("direction must be H or V")
        if self.root is None:
            self.create_root_pane("pane-0")
        focused = self.get_focused_pane()
        new_node = PaneNode(self._new_id())
        branch = PaneNode(focused.pane_id, is_leaf=False, direction=direction)
        branch.children = [focused, new_node]
        focused.parent = branch
        new_node.parent = branch
        parent = self._parent_of(focused.pane_id)
        if parent is None:
            self.root = branch
        else:
            parent.children = [branch if child.pane_id == focused.pane_id else child for child in parent.children]
            branch.parent = parent
        self.focus_pane_id = new_node.pane_id
        self.current_pane_id = new_node.pane_id
        return new_node

    def close_pane(self, pane_id: str | None = None) -> bool:
        pane_id = pane_id or self.focus_pane_id
        if self.get_pane_count() <= 1:
            return False
        target = self._find(pane_id)
        if target is None or not target.is_leaf:
            return False
        parent = self._parent_of(pane_id)
        if parent is None:
            return False
        parent.children = [child for child in parent.children if child.pane_id != pane_id]
        if len(parent.children) == 1 and parent is self.root:
            self.root = parent.children[0]
            self.root.parent = None
        self.focus_pane_id = self._leaves()[0].pane_id
        self.current_pane_id = self.focus_pane_id
        return True

    def focus_next(self) -> bool:
        leaves = self._leaves()
        if not leaves:
            return False
        ids = [leaf.pane_id for leaf in leaves]
        current = self.focus_pane_id if self.focus_pane_id in ids else ids[0]
        self.focus_pane_id = ids[(ids.index(current) + 1) % len(ids)]
        self.current_pane_id = self.focus_pane_id
        return True

    def save_layout(self) -> dict[str, Any]:
        if self.root is None:
            return {}

        def serialize(node: PaneNode) -> dict[str, Any]:
            if node.is_leaf:
                return {
                    "type": "pane",
                    "pane_id": node.pane_id,
                    "is_leaf": True,
                    "direction": None,
                    "working_dir": node.pane.working_dir if node.pane else ".",
                }
            return {
                "type": "branch",
                "pane_id": node.pane_id,
                "is_leaf": False,
                "direction": node.direction,
                "children": [serialize(child) for child in node.children],
            }

        return serialize(self.root)

    def restore_layout(self, layout: dict[str, Any] | None) -> bool:
        if not isinstance(layout, dict) or not layout:
            return False

        def build(data: dict[str, Any]) -> PaneNode:
            node = PaneNode(
                data.get("pane_id", self._new_id()), is_leaf=data.get("is_leaf", True), direction=data.get("direction")
            )
            if node.is_leaf:
                node.pane = Pane(node.pane_id, working_dir=data.get("working_dir", "."))
            else:
                node.children = [build(child) for child in data.get("children", [])]
                for child in node.children:
                    child.parent = node
            return node

        try:
            self.root = build(layout)
        except Exception:
            return False
        self.focus_pane_id = self._leaves()[0].pane_id
        self.current_pane_id = self.focus_pane_id
        return True


__all__ = ["Pane", "PaneManager", "PaneNode"]
