"""Pane tree management for the compositor."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from yaml import safe_dump, safe_load


@dataclass
class Pane:
    """Leaf pane model."""

    pane_id: str
    working_dir: str = "."
    is_active: bool = True
    is_leaf: bool = True


@dataclass
class PaneNode:
    """A node in the pane tree."""

    pane_id: str
    is_leaf: bool = True
    direction: str | None = None
    pane: Pane | None = None
    children: list["PaneNode"] = field(default_factory=list)
    parent: "PaneNode | None" = None

    def __post_init__(self) -> None:
        if self.pane is None and self.is_leaf:
            self.pane = Pane(self.pane_id)
        if not self.is_leaf:
            self.pane = None

    def leaves(self) -> list["PaneNode"]:
        """Return all leaf nodes."""
        if self.is_leaf:
            return [self]
        out: list[PaneNode] = []
        for child in self.children:
            out.extend(child.leaves())
        return out


def _new_pane_id(counter: int) -> str:
    return f"pane-{counter}"


class PaneManager:
    """Tree manager used for splitter-aware pane operations."""

    def __init__(self) -> None:
        self.root: PaneNode = PaneNode("root")
        self.focus_pane_id: str = "root"
        self._next_pane_index = 1

    def _find_node(self, node_id: str, node: PaneNode | None = None) -> PaneNode | None:
        if node is None:
            node = self.root
        if node.pane_id == node_id:
            return node
        for child in node.children:
            result = self._find_node(node_id, child)
            if result is not None:
                return result
        return None

    def _find_parent(self, node_id: str, node: PaneNode | None = None) -> PaneNode | None:
        if node is None:
            node = self.root
        for child in node.children:
            if child.pane_id == node_id:
                return node
            parent = self._find_parent(node_id, child)
            if parent is not None:
                return parent
        return None

    def _leaf_nodes(self) -> list[PaneNode]:
        return self.root.leaves()

    def get_focused_pane(self) -> PaneNode:
        focused = self._find_node(self.focus_pane_id)
        if focused is None and self._leaf_nodes():
            self.focus_pane_id = self._leaf_nodes()[0].pane_id
            focused = self._leaf_nodes()[0]
        if focused is None:
            raise RuntimeError("no panes")
        return focused

    def get_pane_count(self) -> int:
        return len(self._leaf_nodes())

    def get_all_panes(self) -> list[Pane]:
        return [leaf.pane for leaf in self._leaf_nodes() if leaf.pane is not None]

    def get_pane_by_id(self, pane_id: str) -> PaneNode | None:
        node = self._find_node(pane_id)
        if node is None or not node.is_leaf:
            return None
        return node

    def create_root_pane(self, pane_id: str) -> PaneNode:
        self.root = PaneNode(pane_id)
        self.focus_pane_id = pane_id
        return self.root

    def split_pane(self, direction: str) -> PaneNode:
        direction = direction.upper()
        if direction not in {"H", "V"}:
            raise ValueError("direction must be H or V")

        focused = self.get_focused_pane()
        if not focused.parent:
            # root leaf split
            old_root = self.root
            new_node = PaneNode(_new_pane_id(self._next_pane_index))
            self._next_pane_index += 1
            branch = PaneNode(
                pane_id=old_root.pane_id,
                is_leaf=False,
                direction="V" if direction == "V" else "H",
            )
            old_root.parent = branch
            new_node.parent = branch
            branch.children = [old_root, new_node]
            self.root = branch
            self.focus_pane_id = new_node.pane_id
            return new_node

        # splitting a leaf inside a branch
        parent = focused.parent
        new_node = PaneNode(_new_pane_id(self._next_pane_index))
        self._next_pane_index += 1
        new_node.parent = parent
        old_direction = parent.direction or "V"
        if old_direction != ("V" if direction == "V" else "H"):
            # keep branch orientation; create a small wrapper for mixed splits
            branch = PaneNode(
                pane_id=focused.pane_id,
                is_leaf=False,
                direction=("V" if direction == "V" else "H"),
            )
            focused.parent = branch
            new_node.parent = branch
            branch.children = [focused, new_node]
            idx = parent.children.index(focused)
            parent.children[idx] = branch
            self.focus_pane_id = new_node.pane_id
            return new_node
        parent.children = [*parent.children, new_node]
        self.focus_pane_id = new_node.pane_id
        return new_node

    def close_pane(self, pane_id: str | None = None) -> bool:
        if pane_id is None:
            pane_id = self.focus_pane_id

        leaves = self._leaf_nodes()
        if len(leaves) <= 1:
            return False

        target = self._find_node(pane_id)
        if target is None or target.is_leaf is False:
            return False
        parent = self._find_parent(target.pane_id)
        if parent is None:
            return False

        parent.children = [child for child in parent.children if child.pane_id != target.pane_id]
        if parent.children:
            self.focus_pane_id = parent.children[0].pane_id

        if parent is self.root and len(parent.children) == 1:
            # promote the remaining child to root
            only = parent.children[0]
            only.parent = None
            self.root = only
            self.focus_pane_id = only.pane_id
            return True
        return True

    def focus_next(self) -> bool:
        leaves = self._leaf_nodes()
        if not leaves:
            return False
        ids = [leaf.pane_id for leaf in leaves]
        if self.focus_pane_id not in ids:
            self.focus_pane_id = ids[0]
            return True
        current = ids.index(self.focus_pane_id)
        self.focus_pane_id = ids[(current + 1) % len(ids)]
        return True

    def save_layout(self) -> dict[str, Any]:
        def serialize(node: PaneNode) -> dict[str, Any]:
            if node.is_leaf or node.pane is not None:
                return {
                    "type": "pane",
                    "id": node.pane_id,
                    "working_dir": node.pane.working_dir if node.pane else ".",
                }
            return {
                "type": "branch",
                "direction": node.direction or "H",
                "children": [serialize(child) for child in node.children],
            }

        return serialize(self.root)

    def restore_layout(self, layout: dict[str, Any] | None) -> bool:
        if not isinstance(layout, dict) or "type" not in layout:
            return False

        def build(data: dict[str, Any], parent: PaneNode | None = None) -> PaneNode:
            node_type = data.get("type")
            if node_type == "pane":
                node = PaneNode(data.get("id", _new_pane_id(self._next_pane_index)), is_leaf=True)
                node.pane = Pane(node.pane_id, working_dir=data.get("working_dir", "."))
                if node.pane.pane_id == "":
                    node.pane.pane_id = _new_pane_id(self._next_pane_index)
                node.parent = parent
                return node
            if node_type == "branch":
                children = [build(child, None) for child in data.get("children", [])]
                node = PaneNode(
                    pane_id=data.get("id", _new_pane_id(self._next_pane_index)),
                    is_leaf=False,
                    direction=data.get("direction", "H"),
                    children=children,
                )
                for child in children:
                    child.parent = node
                node.parent = parent
                if not children:
                    node.children = [PaneNode(_new_pane_id(self._next_pane_index))]
                    node.children[0].parent = node
                return node
            raise ValueError("invalid node type")

        try:
            self.root = build(layout)
        except Exception:
            return False
        self.root.parent = None
        self._next_pane_index += 1
        leaves = self._leaf_nodes()
        self.focus_pane_id = leaves[0].pane_id if leaves else "root"
        return True

    def _to_yaml(self) -> str:
        return safe_dump(self.save_layout())


__all__ = ["PaneManager"]
