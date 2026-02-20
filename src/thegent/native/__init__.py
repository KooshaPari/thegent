"""Native binary wrappers for thegent (BKM-08 et al.)."""

from thegent.native.jsonl_parser import JsonlParser
from thegent.native.watcher_daemon import WatcherDaemon, WatchEvent, WatchSpec, get_watcher_daemon

__all__ = [
    "JsonlParser",
    "WatchEvent",
    "WatchSpec",
    "WatcherDaemon",
    "get_watcher_daemon",
]
