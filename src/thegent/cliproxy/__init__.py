"""CLIProxy adapter - backward compatibility re-export.

All pure functions are now in cliproxy.transforms.
The adapter app requiring ThegentSettings stays in cliproxy_adapter.py
"""

from .transforms import *
from .cliproxy_adapter import create_adapter_app

__all__ = ["create_adapter_app"]
