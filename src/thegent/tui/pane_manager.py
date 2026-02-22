"""Pane manager for TUI compositor.

Handles pane tree structure, splitting, merging, and layout management.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .widgets.terminal_pane import TerminalPane


class SplitDirection(Enum):
    """Direction for pane splits."""

    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"


@dataclass
class PaneNode:
    """Node in pane tree structure.

    Can be either a leaf node (contains TerminalPane) or a branch node
    (contains left/right children).
    """

    id: str
    pane: TerminalPane | None = None
    left: PaneNode | None = None
    right: PaneNode | None = None
    direction: SplitDirection | None = None

    def is_leaf(self) -> bool:
        """Check if this node is a leaf (contains a pane)."""
        return self.pane is not None

    def is_branch(self) -> bool:
        """Check if this node is a branch (contains children)."""
        return self.pane is None and (self.left is not None or self.right is not None)


class PaneManager:
    """Manages pane layout and lifecycle.

    Maintains a binary tree of panes, handles split/merge operations,
    focus tracking, and layout serialization.
    """

    def __init__(self) -> None:
        self.root: PaneNode | None = None
        self.focus_pane: TerminalPane | None = None
        self._pane_map: dict[str, TerminalPane] = {}

    def create_pane(self, pane_id: str | None = None, working_dir: str = ".") -> TerminalPane:
        """Create a new terminal pane.

        Args:
            pane_id: Optional ID for the pane (generates UUID if not provided)
            working_dir: Working directory for the pane

        Returns:
            The newly created TerminalPane
        """
        from .widgets.terminal_pane import TerminalConfig, TerminalPane

        if pane_id is None:
            pane_id = str(uuid.uuid4())[:8]

        config = TerminalConfig(cwd=working_dir)  # type: ignore
        pane = TerminalPane(config=config)
        self._pane_map[pane_id] = pane

        if self.root is None:
            self.root = PaneNode(id=pane_id, pane=pane)
        self.focus_pane = pane

        return pane

    def split_pane(
        self,
        direction: str,
        pane_id: str | None = None,
        working_dir: str = ".",
    ) -> TerminalPane:
        """Split the current pane in the given direction.

        Args:
            direction: "vertical" or "horizontal"
            pane_id: Optional ID for new pane
            working_dir: Working directory for new pane

        Returns:
            The newly created TerminalPane
        """
        if self.focus_pane is None:
            return self.create_pane(pane_id, working_dir)

        new_pane = self.create_pane(pane_id, working_dir)
        direction_enum = SplitDirection(direction)

        # Find the node containing the focus pane
        node = self._find_node_with_pane(self.root, self.focus_pane)
        if node is None:
            return new_pane

        # Create new branch node
        old_pane_node = node
        split_node = PaneNode(
            id=str(uuid.uuid4())[:8],
            left=old_pane_node,
            right=PaneNode(id=str(new_pane.id) if hasattr(new_pane, "id") else str(uuid.uuid4())[:8], pane=new_pane),
            direction=direction_enum,
        )

        # Update root if splitting root
        if self.root == old_pane_node:
            self.root = split_node
        else:
            # Find parent and update reference
            parent = self._find_parent_node(self.root, old_pane_node)
            if parent:
                if parent.left == old_pane_node:
                    parent.left = split_node
                else:
                    parent.right = split_node

        self.focus_pane = new_pane
        return new_pane

    def close_pane(self, pane: TerminalPane | None = None) -> None:
        """Close a pane and rebalance layout.

        Args:
            pane: Pane to close (defaults to focus pane)
        """
        if pane is None:
            pane = self.focus_pane
        if pane is None:
            return

        node = self._find_node_with_pane(self.root, pane)
        if node is None:
            return

        # Remove from map
        for pane_id, p in list(self._pane_map.items()):
            if p == pane:
                del self._pane_map[pane_id]
                break

        # If only one pane, just clear root
        if len(self._pane_map) == 0:
            self.root = None
            self.focus_pane = None
            return

        # Find parent and replace with sibling
        parent = self._find_parent_node(self.root, node)
        if parent is None:
            # Closing root
            if self.root and self.root.left and not self.root.left.is_leaf():
                self.root = self.root.left
            elif self.root and self.root.right and not self.root.right.is_leaf():
                self.root = self.root.right
            elif self.root and self.root.left:
                self.root = self.root.left
            elif self.root and self.root.right:
                self.root = self.root.right
            else:
                self.root = None
        else:
            # Replace with sibling
            sibling = parent.left if parent.right == node else parent.right
            if parent == self.root:
                self.root = sibling
            else:
                grandparent = self._find_parent_node(self.root, parent)
                if grandparent:
                    if grandparent.left == parent:
                        grandparent.left = sibling
                    else:
                        grandparent.right = sibling

        # Update focus to first remaining pane
        panes = self.collect_panes()
        if panes:
            self.focus_pane = panes[0]
        else:
            self.focus_pane = None

    def focus_next(self) -> None:
        """Rotate focus to next pane."""
        panes = self.collect_panes()
        if not panes or self.focus_pane is None:
            return

        try:
            current_idx = panes.index(self.focus_pane)
            next_idx = (current_idx + 1) % len(panes)
            self.focus_pane = panes[next_idx]
        except ValueError:
            if panes:
                self.focus_pane = panes[0]

    def focus_prev(self) -> None:
        """Rotate focus to previous pane."""
        panes = self.collect_panes()
        if not panes or self.focus_pane is None:
            return

        try:
            current_idx = panes.index(self.focus_pane)
            prev_idx = (current_idx - 1) % len(panes)
            self.focus_pane = panes[prev_idx]
        except ValueError:
            if panes:
                self.focus_pane = panes[-1]

    def collect_panes(self) -> list[TerminalPane]:
        """Collect all panes in in-order traversal."""
        if self.root is None:
            return []

        panes: list[TerminalPane] = []
        self._collect_panes_recursive(self.root, panes)
        return panes

    def save_layout(self) -> dict[str, Any]:
        """Serialize current layout to dict."""
        if self.root is None:
            return {}
        return self._serialize_tree(self.root)

    def restore_layout(self, layout_data: dict[str, Any]) -> None:
        """Restore pane layout from serialized data."""
        self.root = self._deserialize_tree(layout_data)
        panes = self.collect_panes()
        if panes:
            self.focus_pane = panes[0]

    # Private helper methods

    def _find_node_with_pane(self, node: PaneNode | None, pane: TerminalPane) -> PaneNode | None:
        """Find the node containing the given pane."""
        if node is None:
            return None

        if node.is_leaf() and node.pane == pane:
            return node

        left_result = self._find_node_with_pane(node.left, pane)
        if left_result:
            return left_result

        return self._find_node_with_pane(node.right, pane)

    def _find_parent_node(self, node: PaneNode | None, target: PaneNode) -> PaneNode | None:
        """Find the parent of the target node."""
        if node is None or node == target:
            return None

        if target in (node.left, node.right):
            return node

        left_result = self._find_parent_node(node.left, target)
        if left_result:
            return left_result

        return self._find_parent_node(node.right, target)

    def _collect_panes_recursive(self, node: PaneNode | None, panes: list[TerminalPane]) -> None:
        """Recursively collect panes in in-order traversal."""
        if node is None:
            return

        if node.is_leaf():
            if node.pane:
                panes.append(node.pane)
        else:
            self._collect_panes_recursive(node.left, panes)
            self._collect_panes_recursive(node.right, panes)

    def _serialize_tree(self, node: PaneNode | None) -> dict[str, Any]:
        """Serialize pane tree to dict."""
        if node is None:
            return {}

        if node.is_leaf():
            return {
                "type": "pane",
                "id": node.id,
                "working_dir": ".",  # TODO: Store actual working dir from pane
            }

        return {
            "type": "split",
            "direction": node.direction.value if node.direction else "vertical",
            "left": self._serialize_tree(node.left),
            "right": self._serialize_tree(node.right),
        }

    def _deserialize_tree(self, data: dict[str, Any]) -> PaneNode | None:
        """Deserialize pane tree from dict."""
        if not data:
            return None

        if data.get("type") == "pane":
            from .widgets.terminal_pane import TerminalConfig, TerminalPane

            config = TerminalConfig(cwd=data.get("working_dir", "."))  # type: ignore
            pane = TerminalPane(config=config)
            return PaneNode(id=data.get("id", str(uuid.uuid4())[:8]), pane=pane)

        # Recursively deserialize children
        left = self._deserialize_tree(data.get("left", {}))
        right = self._deserialize_tree(data.get("right", {}))

        direction_str = data.get("direction", "vertical")
        return PaneNode(
            id=str(uuid.uuid4())[:8],
            left=left,
            right=right,
            direction=SplitDirection(direction_str),
        )
