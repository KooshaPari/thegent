"""Label/Tag Parity Checker for workstream-to-remote tag synchronization.

Detects mismatches between local and remote tags, enabling correction workflows.

# @trace WL-287
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TagParityResult:
    """Result of a tag parity check for a single workstream item.

    Attributes:
        wl_id: The workstream item identifier.
        local_tags: Tags present in the local system.
        remote_tags: Tags present in the remote system.
        missing_remote: Tags in local but not in remote (need to sync to remote).
        missing_local: Tags in remote but not in local (need to sync to local).
    """

    wl_id: str
    local_tags: list[str]
    remote_tags: list[str]
    missing_remote: list[str]
    missing_local: list[str]


class TagParityChecker:
    """Checks and validates tag parity between local and remote systems.

    Computes symmetric differences between local and remote tag sets
    to identify synchronization gaps.
    """

    def check(
        self,
        wl_id: str,
        local_tags: list[str],
        remote_tags: list[str],
    ) -> TagParityResult:
        """Check tag parity between local and remote.

        Computes symmetric difference to find tags that need synchronization.

        Args:
            wl_id: The workstream item identifier.
            local_tags: List of tags in local system.
            remote_tags: List of tags in remote system.

        Returns:
            TagParityResult with parity information.

        Raises:
            ValueError: If wl_id is empty or tags are not lists.
        """
        if not wl_id:
            raise ValueError("wl_id cannot be empty")

        if not isinstance(local_tags, list) or not isinstance(remote_tags, list):
            raise ValueError("local_tags and remote_tags must be lists")

        local_set = set(local_tags)
        remote_set = set(remote_tags)

        # Tags in local but not in remote
        missing_remote = sorted(local_set - remote_set)

        # Tags in remote but not in local
        missing_local = sorted(remote_set - local_set)

        return TagParityResult(
            wl_id=wl_id,
            local_tags=sorted(local_tags),
            remote_tags=sorted(remote_tags),
            missing_remote=missing_remote,
            missing_local=missing_local,
        )

    def is_in_parity(self, result: TagParityResult) -> bool:
        """Check if a parity result indicates full parity.

        Full parity means no tags are missing in either direction.

        Args:
            result: The TagParityResult to check.

        Returns:
            True if both missing_remote and missing_local are empty.
        """
        return len(result.missing_remote) == 0 and len(result.missing_local) == 0

    def check_batch(self, items: list[dict]) -> list[TagParityResult]:
        """Check tag parity for a batch of items.

        Each item dict must contain:
        - wl_id: str
        - local_tags: list[str]
        - remote_tags: list[str]

        Args:
            items: List of dicts with wl_id, local_tags, remote_tags.

        Returns:
            List of TagParityResult objects.

        Raises:
            ValueError: If any item is missing required keys.
        """
        results = []

        for item in items:
            required_keys = {"wl_id", "local_tags", "remote_tags"}
            if not all(key in item for key in required_keys):
                raise ValueError(
                    f"Item missing required keys. Must have: {required_keys}"
                )

            result = self.check(
                wl_id=item["wl_id"],
                local_tags=item["local_tags"],
                remote_tags=item["remote_tags"],
            )
            results.append(result)

        return results
