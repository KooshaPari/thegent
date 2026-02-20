import sys
import os
from pathlib import Path

# Add src to sys.path
sys.path.append(os.path.abspath("src"))

from thegent.main import app
import inspect

def check_group(group):
    for command in group.registered_commands:
        func = command.callback
        try:
            inspect.signature(func)
        except NameError as e:
            print(f"Error in command {command.name}: {e}")
            # Try to find which name is missing
            try:
                inspect.get_annotations(func)
            except NameError as e2:
                print(f"  Annotations error: {e2}")
    
    for sub_group in group.registered_groups:
        check_group(sub_group.typer_instance)

print("Checking app commands...")
try:
    check_group(app)
except Exception as e:
    print(f"Fatal error during check: {e}")
    import traceback
    traceback.print_exc()
