import json
import os

filepath = "/Users/kooshapari/.cursor/projects/Users-kooshapari-CodeProjects-Phenotype-repos/terminals/534710.txt"

with open(filepath, 'r') as f:
    content = f.read()

# Find the start of the JSON output
# The JSON starts after the metadata block and before the exit_code block.
# Metadata ends at the line with '---' (after started_at)

try:
    json_start = content.find('{', content.find('command:'))
    json_end = content.rfind('}', 0, content.find('---', json_start)) + 1
    json_str = content[json_start:json_end]
    data = json.loads(json_str)
    
    ready_nums = [pr["number"] for pr in data.get("ready", [])]
    failing_nums = [pr["number"] for pr in data.get("failing", [])]
    
    print(f"READY: {ready_nums}")
    print(f"FAILING: {failing_nums}")
    
except Exception as e:
    print(f"Error parsing JSON: {e}")
