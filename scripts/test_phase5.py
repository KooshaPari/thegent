import asyncio
import logging
from pathlib import Path

from thegent.config import ThegentSettings
from thegent.planning.auto_launch import AutoLaunchSystem
from thegent.planning.workstream_db import WorkstreamDB

logging.basicConfig(level=logging.INFO)


async def test_xp_award():
    settings = ThegentSettings()
    # Force session_dir to .thegent/sessions for the test
    settings.session_dir = Path(".thegent/sessions")
    db = WorkstreamDB(settings=settings)

    # 1. Setup a mock completed session
    session_id = "test-session-xp-123"
    db.execute_query(
        "INSERT OR REPLACE INTO sessions (session_id, agent, status, lane, workstream_item_id) VALUES (?, ?, ?, ?, ?)",
        (session_id, "test-agent", "running", "critical", "item-xp-1"),
    )

    # 2. Instantiate AutoLaunchSystem and trigger completion
    launcher = AutoLaunchSystem(settings)

    # Ensure reputation table exists (it should be created by WorkstreamDB.__init__ via AutoLaunchSystem)
    # But let's verify it's there for the shell script
    db.execute_query("SELECT COUNT(*) FROM reputation")

    # We need to make sure the hook script is executable
    import os
    import stat

    hook_path = Path("hooks/gardener-xp.sh")
    if hook_path.exists():
        st = os.stat(hook_path)
        os.chmod(hook_path, st.st_mode | stat.S_IEXEC)

    print(f"Triggering completion for {session_id}...")
    # This should trigger _award_xp which calls gardener-xp.sh
    launcher.handle_completion(session_id, 0)

    # Give it a moment for the subprocess to run
    await asyncio.sleep(2)

    # 3. Verify XP in database
    results = db.execute_query("SELECT * FROM reputation WHERE agent_id = 'test-agent'")
    if results:
        agent_data = results[0]
        print(f"Agent XP: {agent_data['xp']}")
        print(f"Agent Level: {agent_data['level']}")
        print(f"Trust Score: {agent_data['trust_score']}")

        if agent_data["xp"] > 0:
            print("SUCCESS: XP awarded and persisted!")
        else:
            print("FAILURE: XP not awarded.")
    else:
        print("FAILURE: Agent not found in reputation table.")


if __name__ == "__main__":
    asyncio.run(test_xp_award())
