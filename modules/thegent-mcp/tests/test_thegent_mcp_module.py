import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from thegent_mcp_module import get_mcp_app


def test_module_mcp_exports_loader() -> None:
    assert callable(get_mcp_app)
