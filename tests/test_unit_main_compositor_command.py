from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.unit
@pytest.mark.skip(
    reason="Compositor command not yet implemented in main CLI. "
    "Waiting for compositor integration (FR-MAIN-101, FR-MAIN-102)."
)
def test_compositor_top_level_routes_to_handler(mock_cmd: MagicMock) -> None:
    # @trace FR-MAIN-101
    result = runner.invoke(
        app, ["compositor", "--layout", "stacked", "--include-non-claude", "--once", "--refresh", "0.5"]
    )

    assert result.exit_code == 0
    mock_cmd.assert_called_once_with(layout="stacked", include_non_claude=True, once=True, refresh=0.5)


@pytest.mark.unit
@pytest.mark.skip(
    reason="Compositor command not yet implemented in main CLI. "
    "Waiting for compositor integration (FR-MAIN-102)."
)
def test_compositor_observe_subcommand_routes_to_handler(mock_cmd: MagicMock) -> None:
    # @trace FR-MAIN-102
    result = runner.invoke(app, ["observe", "compositor", "--once"])

    assert result.exit_code == 0
    mock_cmd.assert_called_once_with(layout="balanced", include_non_claude=False, once=True, refresh=1.0)
