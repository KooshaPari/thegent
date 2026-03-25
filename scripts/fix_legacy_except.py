import re
import sys
from pathlib import Path

def fix_except_syntax(file_path):
    path = Path(file_path)
    if not path.exists():
        print(f"File not found: {file_path}")
        return

    content = path.read_text()
    # Match 'except E1, E2, E3:' or 'except E1, E2:'
    # Pattern looks for 'except ' followed by names separated by commas, ending with ':'
    # We ensure there's at least one comma and it's not already parenthesized.
    
    # This regex looks for 'except ' followed by one or more names (with dots), 
    # then a comma, then more names/commas, and finally a colon.
    # It avoids matching if there's already an opening parenthesis.
    pattern = r'except ([A-Za-z0-9_\.]+(?:,\s*[A-Za-z0-9_\.]+)+):'
    
    new_content, count = re.subn(pattern, r'except (\1):', content)
    
    if count > 0:
        path.write_text(new_content)
        print(f"Fixed {count} instances in {file_path}")
    else:
        # Try a more flexible pattern if the first one missed some
        pattern2 = r'except\s+([A-Za-z0-9_\.]+(?:\s*,\s*[A-Za-z0-9_\.]+)+)\s*:'
        new_content, count = re.subn(pattern2, r'except (\1):', content)
        if count > 0:
            path.write_text(new_content)
            print(f"Fixed {count} instances in {file_path} (flexible pattern)")

if __name__ == "__main__":
    for arg in sys.argv[1:]:
        fix_except_syntax(arg)
