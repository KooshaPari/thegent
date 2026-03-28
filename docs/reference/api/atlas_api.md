# atlas API Reference

> **Source**: `src/thegent/cli/atlas.py`

Atlas CLI commands for thegent.

---

## generate

```python
generate(repo: Path, quiet: bool, format: str)
```

Generate codebase atlas for repository.

---

## install_hooks

```python
install_hooks(repo: Path)
```

Install git hooks for auto-atlas generation.

---

## serve

```python
serve(port: int, repo: Path)
```

Start an interactive web server for the atlas.

---

## stats

```python
stats(repo: Path, format: str)
```

Show quick statistics from atlas.

---

## view

```python
view(atlas_type: Optional[str], repo: Path)
```

View generated atlas files.

---

