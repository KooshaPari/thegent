import os
import sys

sys.path.append(os.path.abspath("src"))
try:
    import thegent.cli

except ImportError as e:
    pass
except AttributeError:
    import thegent

