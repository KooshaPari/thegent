"""
Compatibility wrapper for :mod:`config.python.settings`.

The canonical settings implementation still lives under ``config/python``
to preserve the existing directory layout. This module re-exports the
public API so imports such as ``from config.settings import get_settings``
continue to work now that ``config`` is a regular Python package.
"""

from __future__ import annotations

from .python.settings import *  # noqa: F403
