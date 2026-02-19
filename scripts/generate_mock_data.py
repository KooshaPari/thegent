#!/usr/bin/env python3
"""Mock data generator for workstream dashboard testing.

Populates the workstream database with mock data to test the TUI.
"""

import random
import sys
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from thegent.config import ThegentSettings
from thegent.planning.workstream_db import WorkstreamDB

def generate_mock_data():
    settings = ThegentSettings()
    db = WorkstreamDB(settings=settings)
    
    print(f"Generating mock data in {db.db_path}...")
    
    # 1. Mock Workstream Items
    sources = ["manual", "gardening", "agileplus", "escalation"]
    priorities = ["P0", "P1", "P2", "P3"]
    statuses = ["pending", "claimed", "completed", "running"]
    
    item_ids = []
    for i in range(50):
        item_id = f"mock-item-{i:03d}"
        status = random.choice(statuses)
        priority = random.choice(priorities)
        source = random.choice(sources)
        
        # Use execute_query for direct insert since we don't have a simple method for items yet
        db.execute_query(f"""
            INSERT OR REPLACE INTO workstream_items (item_id, title, source, priority, status, created_at)
            VALUES ('{item_id}', 'Mock task {i}', '{source}', '{priority}', '{status}', '{datetime.now(UTC).isoformat()}')
        """)
        item_ids.append(item_id)
    
    # 2. Mock Sessions
    agents = ["gpt-5-mini", "claude-haiku-4.5", "gemini-3-flash", "codex"]
    lanes = ["critical", "standard", "recovery", "background"]
    
    for i in range(20):
        session_id = f"mock-session-{uuid.uuid4().hex[:8]}"
        agent = random.choice(agents)
        status = "running" if i < 5 else "exited"
        item_id = random.choice(item_ids)
        lane = random.choice(lanes)
        started_at = (datetime.now(UTC) - timedelta(minutes=random.randint(1, 60))).isoformat()
        
        db.execute_query(f"""
            INSERT OR REPLACE INTO sessions 
            (session_id, agent, prompt, status, started_at, workstream_item_id, lane, model, owner_tag)
            VALUES ('{session_id}', '{agent}', 'Mock prompt for {item_id}', '{status}', '{started_at}', '{item_id}', '{lane}', '{agent}', 'test-user')
        """)
        
        if status == "exited":
            exit_code = random.choice([0, 0, 0, 1]) # 75% success
            db.mark_session_complete(session_id, exit_code)
            
            # Record some costs
            cost = random.uniform(0.001, 0.05)
            tokens = random.randint(100, 5000)
            db.record_cost(session_id, cost, tokens_total=tokens, model=agent)
    
    # 3. Mock some historical costs
    for i in range(7):
        date = (datetime.now(UTC) - timedelta(days=i)).date().isoformat()
        for _ in range(5):
            db.record_cost(f"hist-{uuid.uuid4().hex[:4]}", random.uniform(0.1, 2.0), model="gpt-5-mini")
            # Update the date manually since record_cost uses current date
            db.execute_query(f"UPDATE cost_tracking SET date = '{date}' WHERE session_id LIKE 'hist-%'")

    print("✅ Mock data generated successfully.")
    print("Run 'thegent workstream dashboard' to see the results.")

if __name__ == "__main__":
    generate_mock_data()
