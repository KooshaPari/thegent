# install_backups API Reference

> **Source**: `src/thegent/install_backups.py`

Backup and restore helpers for shell configuration files.

---

## backup_shell_config

```python
backup_shell_config(hook_file: Path, console: Any)
```

Backup shell config file before modification.

Returns backup path or None.

---

## cleanup_old_backups

```python
cleanup_old_backups(keep_count: int, console: Any)
```

Remove old backups, keeping only the most recent ones.

Returns (removed_count, removed_files).

---

## list_backups

```python
list_backups(console: Any)
```

List all available backups.

Returns list of backup paths.

---

## restore_shell_config

```python
restore_shell_config(backup_path: Path, console: Any)
```

Restore shell config from backup.

Returns (success, message).

---

