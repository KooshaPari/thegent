import sys
import os
print(f"PYTHONPATH: {os.environ.get('PYTHONPATH')}")
print(f"sys.path: {sys.path}")
try:
    import thegent
    print(f"Imported thegent from {thegent.__file__}")
except ImportError as e:
    print(f"Failed to import thegent: {e}")

try:
    from thegent import crew
    print(f"Imported thegent.crew from {crew.__file__}")
except ImportError as e:
    print(f"Failed to import thegent.crew: {e}")
