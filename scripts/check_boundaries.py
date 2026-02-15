import os
import sys
import re
from pathlib import Path

# Layer definitions (allowed dependencies) - G-KD-05 CI architecture guardrails
LAYERS = {
    "config": [],
    "exit_codes": [],
    "output_parser": [],
    "contracts": ["config"],
    "models": ["config", "contracts"],
    "execution": ["config", "contracts", "models"],
    "agents": ["config", "contracts", "models"],
    "operations": ["config"],
    "orchestration_modes": [],
    "planning": [],
    "cli_impl": ["config", "contracts", "models", "execution", "agents", "output_parser", "operations", "orchestration_modes"],
    "cli": ["config", "contracts", "models", "execution", "agents", "output_parser", "cli_impl", "operations", "orchestration_modes", "exit_codes"],
    "mcp_server": ["config", "contracts", "models", "execution", "agents", "output_parser", "operations", "orchestration_modes", "cli_impl"],
    "main": ["config", "contracts", "models", "execution", "agents", "cli_impl", "cli", "planning"],
}

SRC_DIR = Path("src/thegent")

def get_imports(file_path):
    imports = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            match = re.match(r"^(?:from|import) thegent\.([a-z_]+)", line)
            if match:
                imports.append(match.group(1))
    return list(set(imports))

def check_boundaries():
    errors = 0
    print("Checking architectural boundaries...")
    
    for layer, allowed in LAYERS.items():
        # Find files in this layer
        if layer in ["cli_impl", "main", "mcp_server", "operations", "orchestration_modes"]:
            files = [SRC_DIR / f"{layer}.py"]
        else:
            layer_dir = SRC_DIR / layer
            if layer_dir.is_dir():
                files = list(layer_dir.glob("**/*.py"))
            else:
                files = [SRC_DIR / f"{layer}.py"]
                
        for file_path in files:
            if not file_path.exists():
                continue
            
            imports = get_imports(file_path)
            for imp in imports:
                if imp == layer: continue # self import OK
                if imp not in allowed:
                    print(f"[ERROR] Layer '{layer}' (file: {file_path}) imports illegal layer '{imp}'")
                    errors += 1
    
    if errors == 0:
        print("[SUCCESS] No boundary violations found.")
        return 0
    else:
        print(f"[FAIL] Found {errors} boundary violations.")
        return 1

if __name__ == "__main__":
    sys.exit(check_boundaries())
