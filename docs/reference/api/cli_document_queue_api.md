# cli_document_queue API Reference

> **Source**: `src/thegent/cli_document_queue.py`

Document Queue CLI Commands for thegent

Integrates document queue management into thegent's typer-based CLI.
Uses centralized path utilities for cross-platform consistency.

---

## analyze_cmd

```python
analyze_cmd(filepath: Path)
```

Analyze a document.

---

## files_cmd

```python
files_cmd(month: str, location: Any, queue_file: Any, output: Any)
```

Get files for a specific month.

---

## list_cmd

```python
list_cmd(queue_file: Any)
```

List all months in the queue.

---

## next_cmd

```python
next_cmd(queue_file: Any, files: bool)
```

Get next month to process.

---

## process_cmd

```python
process_cmd(filepath: Path, queue_file: Any, analyze: bool)
```

Process a single file.

---

## scan_cmd

```python
scan_cmd(config: Any, output: Any, min_date: Any, location: Any)
```

Scan for markdown files and create queue.

---

## summary_cmd

```python
summary_cmd(queue_file: Any)
```

Get queue summary statistics.

---

