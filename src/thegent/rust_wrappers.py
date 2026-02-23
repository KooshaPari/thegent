"""Thin wrapper entrypoints that delegate harness bins to the Rust shim."""

from __future__ import annotations

import os
import shutil
import sys


def _exec_shim(harness: str) -> None:
    shim = shutil.which("thegent-shims")
    if not shim:
        print(  # noqa: T201 -- intentional error message to stderr
            "thegent-shims not found in PATH; install and link shims first.",
            file=sys.stderr,
        )
        raise SystemExit(127)

    argv = ["thegent-shims", "agent", harness, *sys.argv[1:]]
    os.execv(shim, argv)


def dex() -> None:
    _exec_shim("dex")


def clode() -> None:
    _exec_shim("clode")


def roid() -> None:
    _exec_shim("roid")


def fanta() -> None:
    _exec_shim("fanta")
