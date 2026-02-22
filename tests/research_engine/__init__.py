# Extend __path__ so that submodule imports (e.g. research_engine.schema)
# resolve from src/research_engine/ even when pytest inserts tests/ first.
import sys
from pathlib import Path

_src_pkg = str(Path(__file__).parent.parent.parent / "src" / "research_engine")
if _src_pkg not in __path__:  # type: ignore[name-defined]
    __path__.append(_src_pkg)  # type: ignore[name-defined]
