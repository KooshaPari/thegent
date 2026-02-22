import sys
from pathlib import Path
sys.path.append(str(Path("thegent/src").absolute()))

try:
    from thegent.main import app
    print("Import success")
except Exception as e:
    print(f"Import failed: {e}")
    import traceback
    traceback.print_exc()
