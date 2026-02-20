#!/usr/bin/env python3
"""Verification script for Phase 2: Advanced Features.

Tests reputation-based routing and constitutional critique.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from thegent.config import ThegentSettings
from thegent.economy.reputation import ReputationManager
from thegent.governance.constitution import ConstitutionManager
from thegent.planning.auto_launch import AutoLaunchSystem


async def test_advanced_features():
    settings = ThegentSettings()
    system = AutoLaunchSystem(settings=settings)

    print("Testing Constitutional Critique...")
    # This should trigger a safety violation (rm -rf)
    bad_item = {"id": "item-destructive", "prompt": "rm -rf /", "priority": "P1"}

    # We can't easily call launch_batch because it's async and depends on many things,
    # but we can test the constitution manager directly.
    violations = system.constitution_manager.critique_action({"prompt": bad_item["prompt"]})
    if violations:
        print(f"✅ Correctly detected violations: {[v.reason for v in violations]}")
        for v in violations:
            system.db.record_constitutional_violation(bad_item["id"], None, v)
    else:
        print("❌ Failed to detect safety violation")

    print("\nTesting Reputation System...")
    agent_id = "test-agent"
    system.reputation_manager.submit_rating(
        agent_id=agent_id,
        reviewer_id="human",
        task_id="task-1",
        rating=0.1,  # Very low rating
        feedback="Failed miserably",
    )

    score = system.reputation_manager.get_trust_score(agent_id)
    print(f"Agent {agent_id} trust score: {score:.2f}")

    if score < 0.3:
        print("✅ Correctly assigned low trust score")
    else:
        print(f"❌ Trust score too high: {score}")

    # Verify data in DB
    violations_in_db = system.db.execute_query("SELECT * FROM constitutional_violations")
    print(f"\nViolations in DB: {len(violations_in_db)}")

    reputation_in_db = system.db.execute_query("SELECT * FROM reputation_entries")
    print(f"Reputation entries in DB: {len(reputation_in_db)}")


if __name__ == "__main__":
    asyncio.run(test_advanced_features())
