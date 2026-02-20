"""Thegent CLI entry point redirect.
Migrated to the apps structure for 2026.
"""

import sys

from thegent.cli.apps.main import app


def main():
    app()


if __name__ == "__main__":
    main()
