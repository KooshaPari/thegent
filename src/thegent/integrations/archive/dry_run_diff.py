"""Human-Readable Dry-Run Diffs — show exact field deltas before apply.

Renders field-level comparisons between local and remote states.

# @trace WL-186
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FieldDiff:
    """A single field-level difference.

    Attributes:
        field: The field name.
        local_value: The local (to-be-applied) value (as string).
        remote_value: The remote (current) value (as string).
        direction: One of: "local→remote", "remote→local", "conflict".
    """

    field: str
    local_value: str
    remote_value: str
    direction: str


@dataclass
class DryRunDiff:
    """Diff result for a single workstream item.

    Attributes:
        wl_id: The workstream item identifier.
        connector: The connector name (e.g., 'github', 'linear').
        diffs: List of FieldDiff objects.
    """

    wl_id: str
    connector: str
    diffs: list[FieldDiff]


class DryRunRenderer:
    """Renders dry-run diffs in human-readable format."""

    @staticmethod
    def compute_diff(
        wl_id: str,
        connector: str,
        local: dict,
        remote: dict,
        fields: list[str],
    ) -> DryRunDiff:
        """Compute diff between local and remote for specified fields.

        Args:
            wl_id: The workstream item identifier.
            connector: The connector name.
            local: Local state dict.
            remote: Remote state dict.
            fields: List of field names to compare.

        Returns:
            DryRunDiff with field diffs (only for differing fields).
        """
        diffs = []

        for field in fields:
            local_value = str(local.get(field, ""))
            remote_value = str(remote.get(field, ""))

            # Only add diff if values differ
            if local_value != remote_value:
                diffs.append(
                    FieldDiff(
                        field=field,
                        local_value=local_value,
                        remote_value=remote_value,
                        direction="local→remote",  # default direction
                    )
                )

        return DryRunDiff(
            wl_id=wl_id,
            connector=connector,
            diffs=diffs,
        )

    @staticmethod
    def render_text(diff: DryRunDiff) -> str:
        """Render a single diff as human-readable text.

        Args:
            diff: The DryRunDiff to render.

        Returns:
            Multiline string like: WL-123 [github]:\n  field: "old" → "new"
        """
        if not diff.diffs:
            return f"{diff.wl_id} [{diff.connector}]: (no changes)"

        lines = [f"{diff.wl_id} [{diff.connector}]:"]
        for field_diff in diff.diffs:
            line = f'  {field_diff.field}: "{field_diff.local_value}" → "{field_diff.remote_value}"'
            lines.append(line)

        return "\n".join(lines)

    @staticmethod
    def render_batch(diffs: list[DryRunDiff]) -> str:
        """Render multiple diffs with blank line separation.

        Args:
            diffs: List of DryRunDiff objects.

        Returns:
            Multiline string with all diffs, or "(no changes)" if empty.
        """
        if not diffs:
            return "(no changes)"

        rendered = [DryRunRenderer.render_text(diff) for diff in diffs]
        return "\n\n".join(rendered)
