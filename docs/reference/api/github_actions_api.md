# github_actions API Reference

> **Source**: `src/thegent/integrations/github_actions.py`

GitHub Actions integration helpers for thegent.

Provides helper methods for interacting with GitHub Actions workflows and runs
via the ``gh`` CLI subprocess. The ``gh`` CLI must be authenticated and
available on PATH.

All public functions raise ``RuntimeError`` on failure — no silent degradation.

---

## WorkflowRun

Represents a single GitHub Actions workflow run.

### Methods

#### WorkflowRun.from_dict

```python
from_dict(cls: Any, data: dict[(str, Any)])
```

Construct from a GitHub API response dict.

---

---

## WorkflowRunStatus

Simplified status for a single workflow run.

### Methods

#### WorkflowRunStatus.from_run

```python
from_run(cls: Any, run: WorkflowRun)
```

Derive status from a WorkflowRun.

---

---

## cancel_workflow_run

```python
cancel_workflow_run(repo: str, run_id: int)
```

Cancel an in-progress workflow run.

**Parameters**:

- `repo`: Repository in ``owner/repo`` format.
- `run_id`: The numeric run ID.

**Raises**:

- `RuntimeError`: On API failure.

---

## from_dict

```python
from_dict(cls: Any, data: dict[(str, Any)])
```

Construct from a GitHub API response dict.

---

## from_run

```python
from_run(cls: Any, run: WorkflowRun)
```

Derive status from a WorkflowRun.

---

## get_workflow_run_status

```python
get_workflow_run_status(repo: str, run_id: int) -> WorkflowRunStatus
```

Get the current status of a specific workflow run.

**Parameters**:

- `repo`: Repository in ``owner/repo`` format.
- `run_id`: The numeric run ID.

**Returns** (`WorkflowRunStatus`): Status summary for the run.

**Raises**:

- `RuntimeError`: On API failure.

---

## get_workflow_runs

```python
get_workflow_runs(repo: str, workflow_id: Any) -> list[WorkflowRun]
```

List recent workflow runs for a given workflow.

**Parameters**:

- `repo`: Repository in ``owner/repo`` format.
- `workflow_id`: The workflow file name (e.g. ``ci.yml``) or numeric workflow ID.
- `branch`: Optional branch filter.
- `limit`: Maximum number of runs to return (default 20, GitHub max 100).

**Returns** (`list[WorkflowRun]`): Most recent runs, newest first.

**Raises**:

- `RuntimeError`: On API failure.

---

## list_workflows

```python
list_workflows(repo: str) -> list[dict[str, Any]]
```

List all workflows defined in a repository.

**Parameters**:

- `repo`: Repository in ``owner/repo`` format.

**Returns** (`list[dict[str, Any]]`): Raw workflow objects from the GitHub API.

**Raises**:

- `RuntimeError`: On API failure.

---

## rerun_workflow

```python
rerun_workflow(repo: str, run_id: int)
```

Re-run a completed workflow run (all jobs or failed jobs only).

**Parameters**:

- `repo`: Repository in ``owner/repo`` format.
- `run_id`: The numeric run ID.
- `failed_only`: When ``True``, only re-run failed jobs.

**Raises**:

- `RuntimeError`: On API failure.

---

## trigger_workflow

```python
trigger_workflow(repo: str, workflow_id: Any, ref: str, inputs: Any)
```

Dispatch a workflow via ``workflow_dispatch`` event.

**Parameters**:

- `repo`: Repository in ``owner/repo`` format.
- `workflow_id`: Workflow file name or numeric ID.
- `ref`: Branch or tag ref to run the workflow on.
- `inputs`: Optional key/value pairs passed as workflow inputs.

**Raises**:

- `RuntimeError`: On API failure or non-2xx response.

---

