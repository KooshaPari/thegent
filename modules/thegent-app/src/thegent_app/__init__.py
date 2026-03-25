"""Application composition module boundary for thegent."""


def get_cli_app():
    """Return the Typer CLI app from the canonical CLI package."""
    from thegent_cli.apps.main import app

    return app


__all__ = ["get_cli_app"]
