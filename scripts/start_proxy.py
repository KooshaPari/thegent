#!/usr/bin/env python3
"""Start CLIProxyAPIPlus in foreground without shell wrapping."""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from thegent.agents.cliproxy_manager import _ensure_config, _resolve_binary
from thegent.config import ThegentSettings


def main(argv: list[str]) -> int:
    settings = ThegentSettings()
    config_path = Path(argv[1]).expanduser().resolve() if len(argv) > 1 else _ensure_config(settings)

    binary = _resolve_binary(settings)
    if not Path(binary).exists():
        alt = Path.cwd().parent / "CLIProxyAPIPlus-fork" / "cli-proxy-api-plus"
        if alt.exists():
            binary = str(alt)
            # Ensure config exists before using fork binary (fork looks for config.yaml in its dir)
            fork_config = alt.parent / "config.yaml"
            if not fork_config.exists() and config_path.exists():
                # Copy thegent config to fork location if fork binary is used
                import shutil

                shutil.copy2(config_path, fork_config)

    if not Path(binary).exists() and "/" not in binary:
        found = None
        for segment in os.environ.get("PATH", "").split(":"):
            candidate = Path(segment) / binary
            if candidate.exists():
                found = candidate
                break
        if found is not None:
            binary = str(found)

    args = [binary, "-config", str(config_path)]
    if os.environ.get("THGENT_DEBUG") == "1":
        args.append("-debug")
    try:
        os.execv(binary, args)
    except FileNotFoundError:
        return 1
    except Exception:
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
