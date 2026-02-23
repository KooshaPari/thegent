"""Merge policy for parallel local edits.

Provides strategy-based resolution for conflicts between local and remote values
during multi-agent editing scenarios.

FR traceability: WL-310 (Parallel Local Edit Merge Policy)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class MergeStrategy(str, Enum):
    """Strategy options for resolving merge conflicts."""

    LAST_WRITE_WINS = "last_write_wins"
    REMOTE_WINS = "remote_wins"
    LOCAL_WINS = "local_wins"
    FAIL_ON_CONFLICT = "fail_on_conflict"


class MergeConflict(Exception):
    """Raised when a merge conflict cannot be resolved."""


@dataclass
class MergePolicy:
    """Policy for resolving merge conflicts.

    Attributes:
        strategy: The merge strategy to use. Defaults to LAST_WRITE_WINS.
    """

    strategy: MergeStrategy = MergeStrategy.LAST_WRITE_WINS


class LocalEditMerger:
    """Merges local and remote edits according to a merge policy.

    Attributes:
        policy: The merge policy to apply.
    """

    def __init__(self, policy: MergePolicy) -> None:
        """Initialize the merger with a merge policy.

        Args:
            policy: The MergePolicy to apply.
        """
        self.policy = policy

    def merge(self, local: dict, remote: dict, field: str) -> Any:
        """Merge a single field between local and remote values.

        Applies the policy strategy to resolve the conflict:
        - LAST_WRITE_WINS: uses local value
        - REMOTE_WINS: uses remote value
        - LOCAL_WINS: uses local value
        - FAIL_ON_CONFLICT: raises MergeConflict if local[field] != remote[field]

        Args:
            local: Local record dictionary.
            remote: Remote record dictionary.
            field: Field name to merge.

        Returns:
            The resolved value for the field.

        Raises:
            MergeConflict: If strategy is FAIL_ON_CONFLICT and values differ.
            KeyError: If field is not present in local or remote.
        """
        local_value = local[field]
        remote_value = remote[field]

        if self.policy.strategy == MergeStrategy.LAST_WRITE_WINS:
            return local_value
        if self.policy.strategy == MergeStrategy.REMOTE_WINS:
            return remote_value
        if self.policy.strategy == MergeStrategy.LOCAL_WINS:
            return local_value
        if self.policy.strategy == MergeStrategy.FAIL_ON_CONFLICT:
            if local_value != remote_value:
                raise MergeConflict(f"Conflict on field '{field}': local={local_value!r}, remote={remote_value!r}")
            return local_value
        raise ValueError(f"Unknown merge strategy: {self.policy.strategy}")

    def merge_record(self, local: dict, remote: dict, fields: list[str]) -> dict:
        """Merge multiple fields from local and remote records.

        Applies the merge policy to each field in the provided list.

        Args:
            local: Local record dictionary.
            remote: Remote record dictionary.
            fields: List of field names to merge.

        Returns:
            Merged record with resolved values for each field.

        Raises:
            MergeConflict: If strategy is FAIL_ON_CONFLICT and any values differ.
            KeyError: If any field is not present in local or remote.
        """
        merged = {}
        for field in fields:
            merged[field] = self.merge(local, remote, field)
        return merged
