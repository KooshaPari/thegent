# release_packager API Reference

> **Source**: `src/thegent/tools/release_packager.py`

WP-12009: Automation of release docs packaging.

Compiles PRD, WBS, and test artifacts into a deterministic release package.

---

## ReleasePackager

Packager for system release documentation and artifacts.

### Methods

#### ReleasePackager.__init__

```python
__init__(self, workspace_root)
```

#### ReleasePackager.compile_package

Compile all required documents and generate checksums.

```python
compile_package(self, version)
```

---

## compile_package

Compile all required documents and generate checksums.

```python
compile_package(self, version)
```

---

