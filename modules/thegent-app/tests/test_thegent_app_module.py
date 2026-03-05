import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from thegent_app import get_cli_app


def test_module_app_exports_cli_loader() -> None:
    assert callable(get_cli_app)
