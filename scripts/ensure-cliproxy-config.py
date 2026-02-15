#!/usr/bin/env python3
"""Ensure CLIProxyAPIPlus config exists. Run before starting proxy in process-compose.
Uses direct Python modules (no shell wrapping)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from thegent.agents.cliproxy_manager import _ensure_config
from thegent.config import ThegentSettings


def main() -> int:
    try:
        settings = ThegentSettings()
        _ensure_config(settings)
        return 0
    except Exception:
        return 1


if __name__ == "__main__":
    sys.exit(main())
