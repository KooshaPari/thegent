import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from thegent_governance_module import get_governance_package


def test_module_governance_exports_loader() -> None:
    assert callable(get_governance_package)
