#!/usr/bin/env python3
"""Prevent accidental git force pushes - User Level Global Hook."""
import sys
import json

def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)
    
    tool_name = data.get("tool_name")
    if tool_name != "Bash":
        sys.exit(0)
    
    command = data.get("tool_input", {}).get("command", "")
    
    if not command:
        sys.exit(0)
    
    # Check for force push patterns
    if "git push" in command and ("--force" in command or "-f" in command):
        output = {
            "decision": "block",
            "reason": (
                "⚠️ Force Push Detected!\n\n"
                "Force pushing can overwrite remote history and cause data loss.\n"
                "This is especially dangerous on shared branches.\n\n"
                "If you're certain you need to force push:\n"
                "1. Verify you're on the correct branch\n"
                "2. Communicate with your team\n"
                "3. Run the command manually outside of droid\n\n"
                "Consider using 'git push --force-with-lease' for safer force pushing."
            )
        }
        print(json.dumps(output))
        sys.exit(0)
    
    # Allow operation
    sys.exit(0)

if __name__ == "__main__":
    main()
