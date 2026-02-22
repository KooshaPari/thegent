import os
import sys
from pathlib import Path

sys.path.append(str(Path("src").resolve()))
try:
    import thegent.cli

except ImportError as e:
    pass
except AttributeError:
    import thegent
