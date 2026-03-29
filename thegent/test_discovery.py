import sys
from pathlib import Path

# Add src to sys.path
sys.path.append(str(Path.cwd() / "src"))

from thegent.orchestration.pruning.smart_prune import SmartPruner

pruner = SmartPruner()
sessions = pruner.discover_sessions()
active = [s for s in sessions if s.get("status") == "running"]
statuses = {s.get("status") for s in sessions}
for s in sessions:
    if s.get("status") == "running":
        pass
