import re
import sys
from pathlib import Path

# Layer definitions (allowed dependencies) - G-KD-05 CI architecture guardrails
LAYERS = {
    "config": [],
    "exit_codes": [],
    "output_parser": [],
    "contracts": ["config"],
    "models": ["config", "contracts"],
    "execution": ["config", "contracts", "models"],
    "agents": ["config", "contracts", "models", "observability"],
    "operations": ["config"],
    "orchestration_modes": [],
    "planning": [],
    "routing": ["config", "models", "execution"],
    "tools": [],
    "terminal_cli": ["tools", "cli_impl"],
    "cli_impl": [
        "config",
        "contracts",
        "models",
        "execution",
        "agents",
        "output_parser",
        "operations",
        "orchestration_modes",
        "routing",
        "observability",
    ],
    "cli": [
        "config",
        "contracts",
        "models",
        "execution",
        "agents",
        "output_parser",
        "cli_impl",
        "operations",
        "orchestration_modes",
        "exit_codes",
        "routing",
    ],
    "mcp_server": [
        "config",
        "contracts",
        "models",
        "execution",
        "agents",
        "output_parser",
        "operations",
        "orchestration_modes",
        "cli_impl",
    ],
    "main": [
        "config",
        "contracts",
        "models",
        "execution",
        "agents",
        "cli_impl",
        "cli",
        "planning",
        "clode_main",
        "terminal_cli",
    ],
}

SRC_DIR = Path("src/thegent")


def get_imports(file_path):
    imports = []
    with open(file_path, encoding="utf-8") as f:
        for line in f:
            match = re.match(r"^(?:from|import) thegent\.([a-z_]+)", line)
            if match:
                imports.append(match.group(1))
    return list(set(imports))


def check_boundaries() -> int:
    errors = 0

    for layer, allowed in LAYERS.items():
        # Find files in this layer
        if layer in ["cli_impl", "main", "mcp_server", "operations", "orchestration_modes"]:
            files = [SRC_DIR / f"{layer}.py"]
        else:
            layer_dir = SRC_DIR / layer
            files = list(layer_dir.glob("**/*.py")) if layer_dir.is_dir() else [SRC_DIR / f"{layer}.py"]

        for file_path in files:
            if not file_path.exists():
                continue

            imports = get_imports(file_path)
            for imp in imports:
                if imp == layer:
                    continue  # self import OK
                if imp not in allowed:
                    # print violation for easier debugging
                    print(f"VIOLATION: {file_path} imports '{imp}' which is not allowed for layer '{layer}'")
                    errors += 1

    if errors == 0:
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(check_boundaries())
