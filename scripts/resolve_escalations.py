from pathlib import Path

from thegent.config import ThegentSettings
from thegent.execution import EscalationQueue

settings = ThegentSettings()
# Ensure we use the correct session_dir from git status info if needed,
# but ThegentSettings should pick it up.
# From git status: Workspace Path: /Users/kooshapari/temp-PRODVERCEL/485/kush/thegent
# .thegent/sessions is in the root.
root = Path("/Users/kooshapari/temp-PRODVERCEL/485/kush/thegent")
session_dir = root / ".thegent" / "sessions"

eq = EscalationQueue(session_dir)
pending = eq.list_pending()
print(f"Found {len(pending)} pending escalations.")

for item in pending:
    run_id = item["run_id"]
    print(f"Resolving {run_id}...")
    eq.resolve(run_id, resolution="resolved")

print("Done.")
