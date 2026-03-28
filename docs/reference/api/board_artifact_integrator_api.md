# board_artifact_integrator API Reference

> **Source**: `src/thegent/planning/board_artifact_integrator.py`

Board artifact integration for unified workstream.

Ingests CLIProxyAPI++ board artifacts (CSV, JSON, MD) and maps them
into thegent workstream items.

WL-158: Unified Workstream Integration for CLIProxyAPI++ Board Artifacts

---

## BoardArtifactIntegrator

Integrate board artifacts into unified workstream.

### Methods

#### BoardArtifactIntegrator.__init__

```python
__init__(self: Any, board_artifacts_dir: Any)
```

Initialize integrator.

**Parameters**:

- `board_artifacts_dir`: Directory containing board artifacts.
Defaults to cliproxyapi-plusplus/docs/planning/

---

#### BoardArtifactIntegrator.find_board_artifacts

```python
find_board_artifacts(self: Any)
```

Find all board artifact files in the artifacts directory.

**Returns**: Dict mapping artifact type to file path

---

#### BoardArtifactIntegrator.ingest_artifacts

```python
ingest_artifacts(self: Any)
```

Ingest all available board artifacts.

**Returns**: List of normalized workstream items from board artifacts

---

#### BoardArtifactIntegrator.to_workstream_format

```python
to_workstream_format(self: Any, items: list[dict[(str, Any)]])
```

Convert board items to workstream markdown table format.

**Returns**: Markdown table representation of items

---

---

## BoardArtifactParser

Parse board artifacts in multiple formats (CSV, JSON, Markdown).

### Methods

#### BoardArtifactParser.parse_csv

```python
parse_csv(file_path: Path)
```

Parse CSV board artifact.

Expected columns: id, title, status, priority, source, effort, depends_on, evidence

---

#### BoardArtifactParser.parse_json

```python
parse_json(file_path: Path)
```

Parse JSON board artifact.

Expected structure: list of items or root with 'items' key.

---

#### BoardArtifactParser.parse_markdown

```python
parse_markdown(file_path: Path)
```

Parse Markdown board artifact.

Expects table format:
| ID | Title | Status | Priority | Source | Effort | Depends | Evidence |

---

---

## create_board_artifact_integrator

```python
create_board_artifact_integrator(board_artifacts_dir: Any)
```

Factory function to create integrator instance.

---

## find_board_artifacts

```python
find_board_artifacts(self: Any)
```

Find all board artifact files in the artifacts directory.

**Returns**: Dict mapping artifact type to file path

---

## ingest_artifacts

```python
ingest_artifacts(self: Any)
```

Ingest all available board artifacts.

**Returns**: List of normalized workstream items from board artifacts

---

## parse_csv

```python
parse_csv(file_path: Path)
```

Parse CSV board artifact.

Expected columns: id, title, status, priority, source, effort, depends_on, evidence

---

## parse_json

```python
parse_json(file_path: Path)
```

Parse JSON board artifact.

Expected structure: list of items or root with 'items' key.

---

## parse_markdown

```python
parse_markdown(file_path: Path)
```

Parse Markdown board artifact.

Expects table format:
| ID | Title | Status | Priority | Source | Effort | Depends | Evidence |

---

## to_workstream_format

```python
to_workstream_format(self: Any, items: list[dict[(str, Any)]])
```

Convert board items to workstream markdown table format.

**Returns**: Markdown table representation of items

---

