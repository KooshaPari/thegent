#!/usr/bin/env python3
"""strip_ansi.py — strip ANSI escape codes from stdin and write to stdout.

Used by ``scripts/check_init_invariants.sh`` to robustly handle Rich's
output even when ``NO_COLOR`` is ignored (e.g., tty detection in CI).
"""
from __future__ import annotations

import re
import sys


def main() -> int:
    data = sys.stdin.read()
    # CSI sequences (`ESC [` followed by params + a final byte).
    plain = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", data)
    # Plain CSI without semicolons (cursor movement, line clear).
    plain = re.sub(r"\x1b\[\d*[A-Z]", "", plain)
    # Private CSI (`ESC [ ? ...`) used for box-drawing by Rich.
    plain = re.sub(r"\x1b\[\?[0-9;]*[A-Za-z]", "", plain)
    sys.stdout.write(plain)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
