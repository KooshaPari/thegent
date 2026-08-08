"""Trial-merge conflict prediction between two ``EditIntent``s (TGNT-P7.2).

Canonical home for ``predict_merge_conflicts`` and the private
``_line_ranges_overlap`` helper. Backed by
``src/thegent/mesh/coordination/predict.py``. The legacy flat path
``from thegent.mesh.coordination import predict_merge_conflicts`` is
preserved as a re-export in ``src/thegent/mesh/coordination/__init__.py``.

Decision tree:
    * different files → no conflict
    * both delete → no conflict (idempotent)
    * one creates, other does anything else → conflict
    * both create → conflict
    * one deletes, other modifies → conflict
    * both modify + overlapping line ranges → conflict
    * both modify without line ranges → conservative conflict
"""

from __future__ import annotations

from .intent import ConflictPrediction, EditIntent


def _line_ranges_overlap(
    ranges_a: list[tuple[int, int]],
    ranges_b: list[tuple[int, int]],
) -> bool:
    """Return True if any range in ranges_a overlaps with any in ranges_b."""
    for start_a, end_a in ranges_a:
        for start_b, end_b in ranges_b:
            if start_a <= end_b and start_b <= end_a:
                return True
    return False


def _create_conflict(
    intent_a: EditIntent,
    intent_b: EditIntent,
    fp: str,
) -> ConflictPrediction:
    """Handle the create-vs-X case.

    Returns ``ConflictPrediction`` when at least one intent is ``create``.
    Both-create-same-file is also a conflict (concurrent writers).
    """
    if intent_a.operation != intent_b.operation:
        return ConflictPrediction(
            has_conflict=True,
            conflicting_files=[fp],
            details=f"Create vs {intent_a.operation}/{intent_b.operation} on {fp}",
        )
    return ConflictPrediction(
        has_conflict=True,
        conflicting_files=[fp],
        details=f"Dual create on {fp}",
    )


def _delete_conflict(fp: str) -> ConflictPrediction:
    """Handle the delete-vs-modify case."""
    return ConflictPrediction(
        has_conflict=True,
        conflicting_files=[fp],
        details=f"Delete vs modify on {fp}",
    )


def _modify_conflict(
    intent_a: EditIntent,
    intent_b: EditIntent,
    fp: str,
) -> ConflictPrediction:
    """Handle the modify-vs-modify case."""
    if intent_a.line_ranges and intent_b.line_ranges:
        if _line_ranges_overlap(intent_a.line_ranges, intent_b.line_ranges):
            return ConflictPrediction(
                has_conflict=True,
                conflicting_files=[fp],
                details=f"Overlapping line ranges on {fp}",
            )
        return ConflictPrediction(has_conflict=False)
    return ConflictPrediction(
        has_conflict=True,
        conflicting_files=[fp],
        details=f"Both modify {fp} without line ranges (conservative)",
    )


def predict_merge_conflicts(
    intent_a: EditIntent,
    intent_b: EditIntent,
) -> ConflictPrediction:
    """Predict whether two intents will conflict (TGNT-P7.2).

    Performs a trial-merge analysis by comparing planned edit operations:
    - Different files: no conflict.
    - Both delete the same file: no conflict (idempotent).
    - One creates, other modifies/deletes: conflict.
    - Both modify with overlapping line ranges: conflict.
    - Both modify with no line ranges specified: conflict (conservative).
    """
    if intent_a.file_path != intent_b.file_path:
        return ConflictPrediction(has_conflict=False)
    fp = intent_a.file_path
    if intent_a.operation == "delete" and intent_b.operation == "delete":
        return ConflictPrediction(has_conflict=False)
    if "create" in (intent_a.operation, intent_b.operation):
        return _create_conflict(intent_a, intent_b, fp)
    if "delete" in (intent_a.operation, intent_b.operation):
        return _delete_conflict(fp)
    return _modify_conflict(intent_a, intent_b, fp)


__all__ = ["predict_merge_conflicts", "_line_ranges_overlap"]
