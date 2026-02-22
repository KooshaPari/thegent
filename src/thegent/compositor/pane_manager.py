"""Pane management for the TUI compositor.

Handles pane tree structure, splitting, merging, and layout operations.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from thegent.compositor.terminal_pane import TerminalPane


@dataclass
class PaneNode:
    """A node in the pane tree structure.

    Attributes:
        node_id: Unique identifier for this node
        pane: The TerminalPane widget (None for branch nodes)
        direction: Split direction ('H' for horizontal, 'V' for vertical, None for leaf)
        children: Child nodes
        parent: Parent node
    """

    node_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    pane: TerminalPane | None = None
    direction: str | None = None  # 'H' or 'V'
    children: list[PaneNode] = field(default_factory=list)
    parent: PaneNode | None = None

    def is_leaf(self) -> bool:
        """Check if this node is a leaf (contains a pane)."""
        return self.pane is not None

    def is_branch(self) -> bool:
        """Check if this node is a branch (has children)."""
        return not self.is_leaf() and len(self.children) > 0


class PaneManager:
    """Manages a tree of terminal panes with split/merge operations.

    Attributes:
        root: Root node of the pane tree
        focus_pane_id: ID of the currently focused pane
    """

    def __init__(self, initial_dir: str = ".") -> None:
        """Initialize the pane manager with a root pane.

        Args:
            initial_dir: Initial working directory for the root pane
        """
        root_pane = TerminalPane("root", initial_dir)
        self.root = PaneNode(node_id="root", pane=root_pane)
        self.focus_pane_id = "root"
        self.pane_map: dict[str, PaneNode] = {"root": self.root}

    def get_focused_pane(self) -> PaneNode | None:
        """Get the currently focused pane node."""
        return self.pane_map.get(self.focus_pane_id)

    def get_pane_by_id(self, pane_id: str) -> PaneNode | None:
        """Get a pane node by its ID."""
        return self.pane_map.get(pane_id)

    def split_pane(self, direction: str, pane_id: str | None = None) -> PaneNode | None:
        """Split a pane in the specified direction.

        Args:
            direction: 'H' for horizontal split, 'V' for vertical split
            pane_id: ID of pane to split (default: focused pane)

        Returns:
            The new pane node, or None if split failed
        """
        target_id = pane_id or self.focus_pane_id
        target_node = self.pane_map.get(target_id)

        if target_node is None or not target_node.is_leaf():
            return None

        # Create new pane
        new_pane = TerminalPane(str(uuid.uuid4()), target_node.pane.working_dir)
        new_pane_node = PaneNode(node_id=new_pane.pane_id, pane=new_pane)

        # Create a new node for the original pane
        original_pane = target_node.pane
        original_node = PaneNode(node_id=target_node.node_id, pane=original_pane)

        # Convert target node to branch
        target_node.pane = None
        target_node.direction = direction
        target_node.children = [original_node, new_pane_node]

        for child in target_node.children:
            child.parent = target_node

        # Update pane_map to point to the new node structure
        self.pane_map[target_id] = original_node
        self.pane_map[new_pane.pane_id] = new_pane_node
        self.focus_pane_id = new_pane.pane_id

        return new_pane_node

    def close_pane(self, pane_id: str | None = None) -> bool:
        """Close a pane and rebalance the tree.

        Args:
            pane_id: ID of pane to close (default: focused pane)

        Returns:
            True if pane was closed, False if it's the only pane
        """
        target_id = pane_id or self.focus_pane_id
        target_node = self.pane_map.get(target_id)

        if target_node is None or target_node is self.root:
            return False

        # Clean up the pane
        if target_node.pane:
            target_node.pane.cleanup()

        parent = target_node.parent
        if parent is None:
            return False

        # Remove from pane map
        del self.pane_map[target_id]

        # If parent has only one child left, promote it
        parent.children = [c for c in parent.children if c.node_id != target_id]

        if len(parent.children) == 1:
            remaining_child = parent.children[0]
            parent.pane = remaining_child.pane
            parent.direction = None
            parent.children = remaining_child.children
            for child in parent.children:
                child.parent = parent

        # Update focus
        if self.focus_pane_id == target_id:
            # Focus on sibling or parent
            siblings = [c for c in parent.children if c.is_leaf()]
            if siblings:
                self.focus_pane_id = siblings[0].pane.pane_id if siblings[0].pane else "root"
            else:
                self.focus_pane_id = "root"

        return True

    def focus_next(self) -> None:
        """Rotate focus to the next pane."""
        all_panes = [node for node in self.pane_map.values() if node.is_leaf()]

        if not all_panes:
            return

        current_index = next((i for i, node in enumerate(all_panes) if node.pane.pane_id == self.focus_pane_id), -1)

        if current_index == -1:
            self.focus_pane_id = all_panes[0].pane.pane_id
        else:
            next_index = (current_index + 1) % len(all_panes)
            self.focus_pane_id = all_panes[next_index].pane.pane_id

    def get_all_panes(self) -> list[TerminalPane]:
        """Get all panes in the tree."""
        panes = []
        for node in self.pane_map.values():
            if node.pane:
                panes.append(node.pane)
        return panes

    def get_pane_count(self) -> int:
        """Get the number of terminal panes."""
        return sum(1 for node in self.pane_map.values() if node.is_leaf())

    def save_layout(self) -> dict:
        """Serialize the pane tree to a dictionary."""
        return self._serialize_node(self.root)

    def _serialize_node(self, node: PaneNode) -> dict:
        """Recursively serialize a node and its children."""
        if node.is_leaf():
            return {
                "type": "pane",
                "id": node.pane.pane_id if node.pane else None,
                "working_dir": node.pane.working_dir if node.pane else ".",
            }
        return {
            "type": "branch",
            "direction": node.direction,
            "children": [self._serialize_node(child) for child in node.children],
        }

    def restore_layout(self, layout_data: dict) -> bool:
        """Restore a pane tree from a serialized layout.

        Args:
            layout_data: Serialized layout data

        Returns:
            True if restoration was successful
        """
        try:
            new_root = self._deserialize_node(layout_data, None)
            if new_root is None:
                return False

            # Clean up old panes
            for node in self.pane_map.values():
                if node.pane:
                    node.pane.cleanup()

            self.root = new_root
            self.pane_map = {}
            self._rebuild_pane_map(self.root)

            # Set focus to first leaf
            leaf_nodes = [node for node in self.pane_map.values() if node.is_leaf()]
            if leaf_nodes:
                self.focus_pane_id = leaf_nodes[0].pane.pane_id if leaf_nodes[0].pane else "root"
            else:
                self.focus_pane_id = "root"

            return True
        except Exception:
            return False

    def _deserialize_node(self, data: dict, parent: PaneNode | None) -> PaneNode | None:
        """Recursively deserialize a node and its children."""
        if data.get("type") == "pane":
            pane = TerminalPane(data.get("id", str(uuid.uuid4())), data.get("working_dir", "."))
            node = PaneNode(node_id=pane.pane_id, pane=pane, parent=parent)
            return node

        if data.get("type") == "branch":
            node = PaneNode(direction=data.get("direction"), parent=parent)
            node.children = [
                c for child in data.get("children", []) if (c := self._deserialize_node(child, node)) is not None
            ]
            return node

        return None

    def _rebuild_pane_map(self, node: PaneNode) -> None:
        """Rebuild the pane_map from the tree structure."""
        if node.is_leaf() and node.pane:
            self.pane_map[node.pane.pane_id] = node
        for child in node.children:
            self._rebuild_pane_map(child)
