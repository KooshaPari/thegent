#!/usr/bin/env python3
"""Verification script for Phase 4: Dependency Resolution.

Tests dependency-aware auto-launching.
"""

import asyncio
import sys
from datetime import UTC, datetime
from pathlib import Path

# Add project root to path
project_root = Path(__path__).parent.parent if "__path__" in globals() else Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from thegent.config import ThegentSettings
from thegent.planning.auto_launch import AutoLaunchSystem
from thegent.planning.workstream_db import WorkstreamDB


async def test_dependencies():
    settings = ThegentSettings()
    db = WorkstreamDB(settings=settings)
    system = AutoLaunchSystem(settings=settings)

    print("Setting up dependency test data...")
    # Item A: No dependencies
    item_a = "item-A"
    db.execute_query(
        """
        INSERT OR REPLACE INTO workstream_items (item_id, title, status, priority)
        VALUES (?, 'Task A', 'pending', 'P1')
        """,
        (item_a,),
    )

    # Debug: check items in DB
    items = db.execute_query("SELECT * FROM workstream_items")
    print(f"Items in DB: {[(i['item_id'], i['status']) for i in items]}")

    # Item B: Depends on A
    item_b = "item-B"
    db.execute_query(
        """
        INSERT OR REPLACE INTO workstream_items (item_id, title, status, priority)
        VALUES (?, 'Task B', 'pending', 'P1')
        """,
        (item_b,),
    )
    db.execute_query(
        "INSERT OR IGNORE INTO dependencies (item_id, depends_on_item_id) VALUES (?, ?)",
        (item_b, item_a),
    )

    print("\nChecking ready items before A is completed...")
    ready = db.get_ready_items()
    ready_ids = [i["item_id"] for i in ready]
    print(f"Ready items: {ready_ids}")

    if item_a in ready_ids and item_b not in ready_ids:
        print("✅ Only Item A is ready (correct)")
    else:
        print(f"❌ Incorrect ready items: {ready_ids}")

    print("\nMarking Item A as completed...")
    db.execute_query(
        "UPDATE workstream_items SET status = 'completed', completed_at = ? WHERE item_id = ?",
        (datetime.now(UTC).isoformat(), item_a),
    )

    print("Checking ready items after A is completed...")
    ready = db.get_ready_items()
    ready_ids = [i["item_id"] for i in ready]
    print(f"Ready items: {ready_ids}")

    if item_b in ready_ids:
        print("✅ Item B is now ready (correct)")
    else:
        print(f"❌ Item B still not ready: {ready_ids}")

    print("\nTesting Smart Batching logic (launch_batch with priorities)...")
    # Add Item C (P0) and Item D (P2)
    db.execute_query(
        "INSERT OR REPLACE INTO workstream_items (item_id, title, status, priority) VALUES ('item-C', 'Task C', 'pending', 'P0')"
    )
    db.execute_query(
        "INSERT OR REPLACE INTO workstream_items (item_id, title, status, priority) VALUES ('item-D', 'Task D', 'pending', 'P2')"
    )

    ready = db.get_ready_items()
    # Check if C is before B and D (P0 < P1 < P2)
    ready_ids = [i["item_id"] for i in ready]
    print(f"Ready items ordered by priority: {ready_ids}")

    if ready_ids[0] == "item-C" and "item-B" in ready_ids and "item-D" in ready_ids:
        print("✅ Priority ordering correct")
    else:
        print(f"❌ Incorrect priority ordering: {ready_ids}")


if __name__ == "__main__":
    asyncio.run(test_dependencies())
