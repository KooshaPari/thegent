"""Fanta CLI: Antigma-backed interactive harness entrypoint."""

from __future__ import annotations

from thegent.anen_main import app as app

# Expose fanta as a first-class harness entrypoint while reusing
# the full Antigma command surface implemented in anen_main.
app.info.help = "Antigma-backed interactive harness (fanta)."


if __name__ == "__main__":
    app()
