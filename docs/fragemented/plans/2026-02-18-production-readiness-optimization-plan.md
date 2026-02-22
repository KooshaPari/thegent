# Agent-Accelerated Production Readiness Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Accelerate the production readiness of thegent through parallelized agent batches, focusing on cross-platform runtime foundation, distribution, and UX.

**Architecture:** Decompose the 5-week packaging roadmap into 4 Execution Bundles (Foundation, Distribution, Quality, Knowledge) for parallel swarm execution.

**Tech Stack:** Python 3.12, Typer, Pydantic, GitHub Actions, Rust (shims), Homebrew/Winget.

---

### Task 1: Runtime Foundation - Platform Detection

**Files:**
- Create: `src/thegent/platform.py`
- Test: `tests/test_platform.py`

**Step 1: Write the failing test**

```python
import os
import platform
from thegent.platform import detect_platform, Platform

def test_detect_platform():
    p = detect_platform()
    assert isinstance(p, Platform)
    if platform.system().lower() == "darwin":
        assert p == Platform.MACOS
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_platform.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'thegent.platform'"

**Step 3: Write minimal implementation**

```python
import os
import platform
from enum import Enum

class Platform(Enum):
    MACOS = "macos"
    LINUX = "linux"
    WINDOWS = "windows"
    WSL2 = "wsl2"
    UNKNOWN = "unknown"

def detect_platform() -> Platform:
    system = platform.system().lower()
    if system == "linux":
        if os.path.exists("/proc/version"):
            with open("/proc/version") as f:
                if "microsoft" in f.read().lower():
                    return Platform.WSL2
        return Platform.LINUX
    if system == "darwin": return Platform.MACOS
    if system == "windows": return Platform.WINDOWS
    return Platform.UNKNOWN
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_platform.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/thegent/platform.py tests/test_platform.py
git commit -m "feat(platform): add cross-platform detection"
```

---

### Task 2: Runtime Foundation - Path Resolution

**Files:**
- Create: `src/thegent/platform_paths.py`
- Test: `tests/test_platform_paths.py`

**Step 1: Write the failing test**

```python
from pathlib import Path
from thegent.platform_paths import get_config_dir

def test_get_config_dir():
    config_dir = get_config_dir()
    assert isinstance(config_dir, Path)
    assert config_dir.name == "thegent"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_platform_paths.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write minimal implementation**

```python
import os
from pathlib import Path
from thegent.platform import detect_platform, Platform

def get_config_dir() -> Path:
    p = detect_platform()
    if p == Platform.MACOS:
        return Path.home() / "Library" / "Application Support" / "thegent"
    if p == Platform.WINDOWS:
        return Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")) / "thegent"
    return Path.home() / ".config" / "thegent"
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_platform_paths.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/thegent/platform_paths.py tests/test_platform_paths.py
git commit -m "feat(platform): add platform-aware path resolution"
```

---

### Task 3: Work Stream Consolidation

**Files:**
- Modify: `docs/reference/WORK_STREAM.md`

**Step 1: Inject PROD-READY tasks**

Append all items from `docs/research/PRODUCTION_PACKAGING_POLISH_OPTIMIZATION_AUDIT_AND_PLAN.md` §15 to the BACKLOG in `docs/reference/WORK_STREAM.md`.

**Step 2: Verify injection**

Run: `grep "PROD-READY" docs/reference/WORK_STREAM.md`
Expected: List of 30+ tasks.

**Step 3: Commit**

```bash
git add docs/reference/WORK_STREAM.md
git commit -m "docs(backlog): consolidate production readiness tasks"
```
