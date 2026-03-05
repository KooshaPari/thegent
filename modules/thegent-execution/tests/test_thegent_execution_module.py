import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from thegent_execution_module import get_execution_package


def test_module_execution_exports_loader() -> None:
    assert callable(get_execution_package)
