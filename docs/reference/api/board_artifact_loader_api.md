# board_artifact_loader API Reference

> **Source**: `src/thegent/planning/board_artifact_loader.py`

Board artifact loader for CLIProxyAPI++ execution board integration into thegent workstream.

Loads board artifacts (markdown, CSV, JSON formats) and maps execution slices
into thegent unified workstream loop. Enables bidirectional sync between CLIProxyAPI++
board and thegent WORK_STREAM.md.

---

## BoardArtifactLoader

Load and parse CLIProxyAPI++ board artifacts for workstream integration.

### Methods

#### BoardArtifactLoader.__init__

```python
__init__(self: Any, board_dir: Path)
```

---

#### BoardArtifactLoader.get_completion_status

```python
get_completion_status(self: Any)
```

Get aggregated completion status for all slices.

---

#### BoardArtifactLoader.load_all

```python
load_all(self: Any)
```

Load all available board artifacts (MD, CSV, JSON).

---

#### BoardArtifactLoader.map_to_workstream

```python
map_to_workstream(self: Any)
```

Map loaded board items to thegent WORK_STREAM.md reference entries.

**Returns**: Dictionary mapping WL IDs to board items and metadata.

---

---

## BoardItem

Represents a single board item with CLIProxyAPI++ → thegent mapping.

---

## ExecutionSlice

Represents an execution slice with thegent workstream mapping.

---

## get_completion_status

```python
get_completion_status(self: Any)
```

Get aggregated completion status for all slices.

---

## load_all

```python
load_all(self: Any)
```

Load all available board artifacts (MD, CSV, JSON).

---

## map_to_workstream

```python
map_to_workstream(self: Any)
```

Map loaded board items to thegent WORK_STREAM.md reference entries.

**Returns**: Dictionary mapping WL IDs to board items and metadata.

---

