# transactions API Reference

> **Source**: `src/thegent/orchestration/transactions.py`

WP-15003: Atomic Transactions and Commit-Log Orchestration (CLO).
MTSP-13/14: Ensure multi-step agent actions are atomic or revertible.

---

## TransactionManager

Manages atomic blocks of operations with rollback support.

### Methods

#### TransactionManager.__init__

```python
__init__(self, run_id)
```

#### TransactionManager.add_op

Add an operation to the transaction.

```python
add_op(self, description, do, undo)
```

---

## TransactionOperation

A single revertible operation within a transaction.

---

## add_op

Add an operation to the transaction.

```python
add_op(self, description, do, undo)
```

---

## apply_multi_file_transaction

MTSP-13: Prepare multi-file changes and apply as a single atomic transaction.

Writes each file to a temp path, then renames all atomically. On failure, no files are modified.
If git_commit=True and cwd is a git repo, stages and commits as a single transaction.

Returns:
    (success, message)

```python
apply_multi_file_transaction(changes, cwd, git_commit, commit_message)
```

---

