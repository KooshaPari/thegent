#!/usr/bin/env python3
"""Test script for auto-launch system.

Verifies that all components initialize correctly.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from thegent.config import ThegentSettings
from thegent.orchestration.session_watcher import SessionEventWatcher
from thegent.planning.auto_launch import AutoLaunchSystem
from thegent.planning.workstream_db import WorkstreamDB


def test_database():
    """Test database initialization."""
    print("Testing WorkstreamDB...")
    settings = ThegentSettings()
    db = WorkstreamDB(settings=settings)
    stats = db.get_statistics()
    print(f"✅ Database initialized: {db.db_path}")
    print(f"   Running: {stats['running']}, Completed: {stats['completed']}")
    return True


def test_event_watcher():
    """Test event watcher initialization."""
    print("\nTesting SessionEventWatcher...")
    settings = ThegentSettings()
    watcher = SessionEventWatcher(settings.session_dir)
    print(f"✅ Event watcher initialized: {settings.session_dir}")
    return True


def test_auto_launch_system():
    """Test auto-launch system initialization."""
    print("\nTesting AutoLaunchSystem...")
    try:
        system = AutoLaunchSystem()
        print("✅ Auto-launch system initialized")
        print(f"   Database: {system.db.db_path}")
        print(f"   Event watcher: {system.event_watcher.session_dir}")
        return True
    except Exception as e:
        print(f"❌ Auto-launch system failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Auto-Launch System Test Suite")
    print("=" * 60)

    results = []
    results.append(("Database", test_database()))
    results.append(("Event Watcher", test_event_watcher()))
    results.append(("Auto-Launch System", test_auto_launch_system()))

    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name}: {status}")

    all_passed = all(r[1] for r in results)
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
