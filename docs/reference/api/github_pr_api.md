# github_pr API Reference

> **Source**: `src/thegent/integrations/github_pr.py`

GitHub Pull Request integration helpers for thegent.

Provides helper methods for listing, inspecting, creating, and merging GitHub
pull requests via the ``gh`` CLI subprocess. The ``gh`` CLI must be
authenticated and available on PATH.

All public functions raise ``RuntimeError`` on failure — no silent degradation.

---

## CheckRun

Summary of a single CI check run.

---

## PRStatus

Mergeable state and CI check summary for a pull request.

### Methods

#### PRStatus.all_checks_passed

```python
all_checks_passed(self: Any)
```

Return True if every check concluded with 'success'.

---

#### PRStatus.ready_to_merge

```python
ready_to_merge(self: Any)
```

Return True if PR is mergeable and all checks passed.

---

---

## PullRequest

Represents a GitHub Pull Request.

### Methods

#### PullRequest.from_dict

```python
from_dict(cls: Any, data: dict[(str, Any)])
```

Construct from a GitHub API response dict.

---

---

## add_pr_labels

```python
add_pr_labels(repo: str, pr_number: int, labels: list[str])
```

Add labels to a pull request.

**Parameters**:

- `repo`: Repository in ``owner/repo`` format.
- `pr_number`: The PR number.
- `labels`: Label names to add.

**Raises**:

- `RuntimeError`: On API failure.

---

## all_checks_passed

```python
all_checks_passed(self: Any)
```

Return True if every check concluded with 'success'.

---

## close_pr

```python
close_pr(repo: str, pr_number: int)
```

Close (without merging) a pull request.

**Parameters**:

- `repo`: Repository in ``owner/repo`` format.
- `pr_number`: The PR number.

**Raises**:

- `RuntimeError`: On API failure.

---

## create_pr

```python
create_pr(repo: str, head: str, base: str, title: str, body: str) -> PullRequest
```

Create a new pull request.

**Parameters**:

- `repo`: Repository in ``owner/repo`` format.
- `head`: Source branch (``owner:branch`` or plain branch name for same-repo).
- `base`: Target branch (e.g. ``main``).
- `title`: PR title.
- `body`: PR description/body markdown.
- `draft`: When ``True``, creates the PR in draft state.

**Returns** (`PullRequest`): The newly created pull request.

**Raises**:

- `RuntimeError`: On API failure (e.g. branch does not exist, PR already exists).

---

## from_dict

```python
from_dict(cls: Any, data: dict[(str, Any)])
```

Construct from a GitHub API response dict.

---

## get_pr_status

```python
get_pr_status(repo: str, pr_number: int) -> PRStatus
```

Get the current mergeable state and CI checks for a pull request.

**Parameters**:

- `repo`: Repository in ``owner/repo`` format.
- `pr_number`: The PR number.

**Returns** (`PRStatus`): Mergeable state and check summary.

**Raises**:

- `RuntimeError`: On API failure.

---

## list_open_prs

```python
list_open_prs(repo: str) -> list[PullRequest]
```

List open pull requests for a repository.

**Parameters**:

- `repo`: Repository in ``owner/repo`` format.
- `base`: Optional base branch filter (e.g. ``main``).
- `author`: Optional GitHub login to filter by PR author.
- `label`: Optional label name to filter by.
- `limit`: Maximum number of PRs to return (default 30).

**Returns** (`list[PullRequest]`): Open PRs, newest first.

**Raises**:

- `RuntimeError`: On API failure.

---

## merge_pr

```python
merge_pr(repo: str, pr_number: int, method: MergeMethod) -> dict[str, Any]
```

Merge a pull request.

**Parameters**:

- `repo`: Repository in ``owner/repo`` format.
- `pr_number`: The PR number.
- `method`: One of ``"merge"``, ``"squash"``, or ``"rebase"``.
- `commit_title`: Optional override for the merge commit title.
- `commit_message`: Optional override for the merge commit message body.
- `delete_branch`: When ``True``, deletes the head branch after merging (default True).

**Returns** (`dict[str, Any]`): Raw merge response from the GitHub API.

**Raises**:

- `RuntimeError`: On API failure (e.g. not mergeable, conflicts).

---

## ready_to_merge

```python
ready_to_merge(self: Any)
```

Return True if PR is mergeable and all checks passed.

---

## request_pr_review

```python
request_pr_review(repo: str, pr_number: int, reviewers: list[str])
```

Request reviews from specific GitHub users.

**Parameters**:

- `repo`: Repository in ``owner/repo`` format.
- `pr_number`: The PR number.
- `reviewers`: List of GitHub login names to request reviews from.

**Raises**:

- `RuntimeError`: On API failure.

---

