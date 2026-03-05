import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from thegent_control_plane_module import get_control_plane_package


def test_module_control_plane_exports_loader() -> None:
    assert callable(get_control_plane_package)
