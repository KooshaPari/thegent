"""PaneManager - Pane tree management for split/merge operations."""

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class PaneNode:
    """Represents a node in the pane tree."""

    pane_id: str
    direction: str | None = None  # "horizontal", "vertical", or None for leaf
    children: list["PaneNode"] = field(default_factory=list)
    is_leaf: bool = True


class PaneManager:
    """Manages pane tree structure and operations."""

    def __init__(self) -> None:
        """Initialize PaneManager."""
        self.root: PaneNode | None = None
        self.current_pane_id: str | None = None
        logger.info("PaneManager initialized")

    def create_root_pane(self, pane_id: str) -> PaneNode:
        """Create the root pane.

        Args:
            pane_id: ID for the root pane

        Returns:
            The root pane node
        """
        logger.info(f"Creating root pane {pane_id}")
        self.root = PaneNode(pane_id=pane_id, is_leaf=True)
        self.current_pane_id = pane_id
        return self.root

    def split_pane(self, direction: str) -> PaneNode | None:
        """Split the current pane.

        Args:
            direction: "horizontal" or "vertical"

        Returns:
            The new pane node, or None if no current pane
        """
        if not self.current_pane_id or not self.root:
            logger.warning("Cannot split: no current pane")
            return None

        if direction not in ("horizontal", "vertical"):
            logger.warning(f"Invalid direction: {direction}")
            return None

        logger.info(f"Splitting pane {self.current_pane_id} {direction}")

        # Find the current pane node
        current_node = self._find_node(self.root, self.current_pane_id)
        if not current_node:
            logger.warning(f"Pane {self.current_pane_id} not found")
            return None

        # Create new pane node
        import uuid

        new_pane_id = f"pane-{uuid.uuid4().hex[:8]}"
        new_node = PaneNode(pane_id=new_pane_id, is_leaf=True)

        # If current node is a leaf, convert it to a split container
        if current_node.is_leaf:
            # Save the current pane as first child
            old_pane_id = current_node.pane_id
            current_node.pane_id = f"split-{uuid.uuid4().hex[:8]}"
            current_node.direction = direction
            current_node.is_leaf = False
            current_node.children = [
                PaneNode(pane_id=old_pane_id, is_leaf=True),
                new_node,
            ]
        else:
            # Add to existing split
            current_node.children.append(new_node)

        self.current_pane_id = new_pane_id
        return new_node

    def close_pane(self) -> bool:
        """Close the current pane.

        Returns:
            True if successful, False otherwise
        """
        if not self.current_pane_id or not self.root:
            logger.warning("Cannot close: no current pane")
            return False

        logger.info(f"Closing pane {self.current_pane_id}")

        # Don't close if it's the only pane
        if self.root.is_leaf and self.root.pane_id == self.current_pane_id:
            logger.warning("Cannot close the last remaining pane")
            return False

        # Find parent of current pane
        parent, current_node = self._find_parent(self.root, self.current_pane_id)

        if not current_node:
            logger.warning(f"Pane {self.current_pane_id} not found")
            return False

        if parent is None:
            # Closing root pane - not allowed if it's the only one
            return False

        # Remove current node from parent's children
        parent.children = [c for c in parent.children if c.pane_id != self.current_pane_id]

        # If parent now has only one child, collapse the split
        if len(parent.children) == 1:
            # Replace parent with its remaining child
            remaining = parent.children[0]
            if parent == self.root:
                # Replace root
                self.root = remaining
            else:
                # Replace parent in grandparent
                grandparent, _ = self._find_parent(self.root, parent.pane_id)
                if grandparent:
                    idx = grandparent.children.index(parent)
                    grandparent.children[idx] = remaining

        # Focus on first available pane
        if self.root:
            self.current_pane_id = self._get_first_leaf(self.root).pane_id

        return True

        logger.info(f"Closing pane {self.current_pane_id}")
        # TODO: Implement tree manipulation in P2.1
        return False

    def focus_next(self) -> bool:
        """Focus the next pane in rotation.

        Returns:
            True if successful, False otherwise
        """
        if not self.current_pane_id or not self.root:
            logger.warning("Cannot focus: no current pane")
            return False

        logger.info(f"Focusing next pane from {self.current_pane_id}")

        # Get all leaf nodes in order
        leaves = self._get_all_leaves(self.root)
        if len(leaves) <= 1:
            return False

        # Find current index
        try:
            current_idx = next(i for i, leaf in enumerate(leaves) if leaf.pane_id == self.current_pane_id)
            next_idx = (current_idx + 1) % len(leaves)
            self.current_pane_id = leaves[next_idx].pane_id
            return True
        except StopIteration:
            logger.warning(f"Current pane {self.current_pane_id} not found in leaves")
            return False

        logger.info(f"Focusing next pane from {self.current_pane_id}")
        # TODO: Implement tree traversal in P2.1
        return False

    def save_layout(self) -> dict:
        """Serialize the pane tree to a dict.

        Returns:
            Dictionary representation of the tree
        """
        if not self.root:
            return {}

        logger.debug("Saving layout")
        return self._serialize_tree(self.root)

    def restore_layout(self, layout_data: dict) -> bool:
        """Restore pane tree from a dict.

        Args:
            layout_data: Dictionary representation of tree

        Returns:
            True if successful, False otherwise
        """
        logger.debug("Restoring layout")
        if not layout_data:
            logger.warning("Empty layout data")
            return False

        try:
            self.root = self._deserialize_node(layout_data)
            if self.root:
                # Set current pane to first leaf
                first_leaf = self._get_first_leaf(self.root)
                self.current_pane_id = first_leaf.pane_id
                return True
            return False
        except Exception as e:
            logger.error(f"Error restoring layout: {e}", exc_info=True)
            return False

        # TODO: Implement deserialization in P2.3
        return False

    def _find_node(self, node: PaneNode | None, pane_id: str) -> PaneNode | None:
        """Find a node by pane_id in the tree."""
        if not node:
            return None
        if node.pane_id == pane_id:
            return node
        for child in node.children:
            found = self._find_node(child, pane_id)
            if found:
                return found
        return None

    def _find_parent(
        self, node: PaneNode | None, pane_id: str, parent: PaneNode | None = None
    ) -> tuple[PaneNode | None, PaneNode | None]:
        """Find parent and node by pane_id."""
        if not node:
            return None, None
        if node.pane_id == pane_id:
            return parent, node
        for child in node.children:
            p, n = self._find_parent(child, pane_id, node)
            if n:
                return p, n
        return None, None

    def _get_first_leaf(self, node: PaneNode) -> PaneNode:
        """Get the first leaf node in the tree."""
        if node.is_leaf:
            return node
        if node.children:
            return self._get_first_leaf(node.children[0])
        return node

    def _get_all_leaves(self, node: PaneNode | None) -> list[PaneNode]:
        """Get all leaf nodes in depth-first order."""
        if not node:
            return []
        if node.is_leaf:
            return [node]
        leaves = []
        for child in node.children:
            leaves.extend(self._get_all_leaves(child))
        return leaves

    def _deserialize_node(self, data: dict) -> PaneNode | None:
        """Deserialize a node from dict."""
        if not data:
            return None

        pane_id = data.get("pane_id", "")
        direction = data.get("direction")
        is_leaf = data.get("is_leaf", True)
        children_data = data.get("children", [])

        node = PaneNode(
            pane_id=pane_id,
            direction=direction,
            is_leaf=is_leaf,
        )

        if children_data:
            node.children = [n for n in (self._deserialize_node(child) for child in children_data if child) if n is not None]

        return node

    def _serialize_tree(self, node: PaneNode | None) -> dict:
        """Recursively serialize tree node to dict."""
        if not node:
            return {}

        result: dict = {
            "pane_id": node.pane_id,
            "direction": node.direction,
            "is_leaf": node.is_leaf,
        }

        if node.children:
            result["children"] = [self._serialize_tree(child) for child in node.children]

        return result
