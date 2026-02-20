import sys
from pathlib import Path

# Add src to sys.path
sys.path.append(str(Path.cwd() / "src"))

from thegent.orchestration.pruning.smart_prune import SmartPruner

pruner = SmartPruner()
sessions = pruner.discover_sessions()
print(f"Discovered: {len(sessions)}")
active = [s for s in sessions if s.get("status") == "running"]
print(f"Active: {len(active)}")
statuses = set(s.get("status") for s in sessions)
print(f"Statuses found: {statuses}")
for s in sessions:
    if s.get("status") == "running":
        print(f" - {s['id']} (agent={s['agent']}, pid={s.get('pid')})")
