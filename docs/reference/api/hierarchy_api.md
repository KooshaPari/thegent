# hierarchy API Reference

> **Source**: `src/thegent/commands/hierarchy.py`

CLI commands for milestone and sprint hierarchy management.

Milestones and sprints are stored as projects with type metadata
in the ProjectRegistry, providing a lightweight hierarchy for
organizing agent work.

WBS: wp-71005-hierarchy-cli
FR Traceability: FR-VER-002 (milestone and sprint management)

Commands:
    thegent plan milestone list/create/complete
    thegent plan sprint list/create/complete

---

## milestone_complete

```python
milestone_complete(name: str)
```

Mark a milestone as completed.

---

## milestone_create

```python
milestone_create(name: str, label: Annotated[(Any, Any)])
```

Create a new milestone.

---

## milestone_list

List all milestones.

---

## sprint_complete

```python
sprint_complete(name: str)
```

Mark a sprint as completed.

---

## sprint_create

```python
sprint_create(name: str, label: Annotated[(Any, Any)])
```

Create a new sprint.

---

## sprint_list

List all sprints.

---

