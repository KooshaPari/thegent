# cli_document_queue API Reference

> **Source**: `src/thegent/cli_document_queue.py`

Document Queue CLI Commands for thegent

Integrates document queue management into thegent's typer-based CLI.

---

## analyze_cmd

Analyze a document.

```python
analyze_cmd(filepath)
```

---

## files_cmd

Get files for a specific month.

```python
files_cmd(month, location, queue_file, output)
```

---

## list_cmd

List all months in the queue.

```python
list_cmd(queue_file)
```

---

## next_cmd

Get next month to process.

```python
next_cmd(queue_file, files)
```

---

## process_cmd

Process a single file.

```python
process_cmd(filepath, queue_file, analyze)
```

---

## scan_cmd

Scan for markdown files and create queue.

```python
scan_cmd(config, output, min_date, location)
```

---

## summary_cmd

Get queue summary statistics.

```python
summary_cmd(queue_file)
```

---

