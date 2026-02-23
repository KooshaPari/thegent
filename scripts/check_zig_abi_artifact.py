#!/usr/bin/env python3
"""Check a Zig ABI artifact for required exported symbols and error envelope conformance."""

from __future__ import annotations

import argparse
import orjson as json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from validate_zig_abi_contract import ContractValidationError, load_contract, validate_contract_data

DEFAULT_CONTRACT_PATH = Path("contracts/runtime/zig_abi_contract_v1.json")
SYMBOL_NAME_PATTERN = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)$")


def _extract_required_symbols(contract: dict[str, Any]) -> list[str]:
    symbols = contract["abi"]["symbols"]
    required = [symbol["name"] for symbol in symbols if symbol.get("stability") == "required"]
    if not required:
        raise ContractValidationError("contract does not define any required symbols")
    return required


def _normalize_symbol_lines(lines: list[str]) -> set[str]:
    symbols: set[str] = set()
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        if " " not in line and "\t" not in line:
            symbols.add(line)
            continue

        match = SYMBOL_NAME_PATTERN.search(line)
        if match:
            symbols.add(match.group(1))

    return symbols


def _tool_candidates(symbol_tool: str, artifact_path: Path) -> list[list[str]]:
    if symbol_tool == "nm":
        return [["nm", "-g", "--defined-only", str(artifact_path)], ["nm", "-gU", str(artifact_path)]]
    if symbol_tool == "readelf":
        return [["readelf", "--dyn-syms", "--wide", str(artifact_path)]]
    if symbol_tool == "objdump":
        return [["objdump", "-T", str(artifact_path)]]

    return [
        ["nm", "-g", "--defined-only", str(artifact_path)],
        ["nm", "-gU", str(artifact_path)],
        ["readelf", "--dyn-syms", "--wide", str(artifact_path)],
        ["objdump", "-T", str(artifact_path)],
    ]


def _load_symbols_from_artifact(artifact_path: Path, symbol_tool: str) -> set[str]:
    if not artifact_path.exists():
        raise FileNotFoundError(f"artifact path does not exist: {artifact_path}")

    failures: list[str] = []
    for command in _tool_candidates(symbol_tool, artifact_path):
        binary = command[0]
        if shutil.which(binary) is None:
            failures.append(f"{binary}: tool not found")
            continue

        completed = subprocess.run(command, capture_output=True, text=True, check=False)
        if completed.returncode != 0:
            stderr = (completed.stderr or "").strip()
            failures.append(f"{' '.join(command)}: exited {completed.returncode} ({stderr})")
            continue

        symbols = _normalize_symbol_lines(completed.stdout.splitlines())
        if symbols:
            return symbols

        failures.append(f"{' '.join(command)}: no symbols parsed")

    joined_failures = " | ".join(failures) if failures else "no symbol tool attempts were made"
    raise RuntimeError(f"unable to read exported symbols from artifact: {joined_failures}")


def _load_symbols_from_file(symbols_file: Path) -> set[str]:
    if not symbols_file.exists():
        raise FileNotFoundError(f"symbols file does not exist: {symbols_file}")
    return _normalize_symbol_lines(symbols_file.read_text(encoding="utf-8").splitlines())


def _validate_error_envelope(envelope_path: Path, contract: dict[str, Any]) -> None:
    if not envelope_path.exists():
        raise FileNotFoundError(f"error envelope file does not exist: {envelope_path}")

    try:
        envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"error envelope JSON is invalid: {exc}") from exc

    if not isinstance(envelope, dict):
        raise ValueError("error envelope JSON must be an object")

    required_fields = contract["error_contract"]["error_envelope"]["required_fields"]
    missing = [field for field in required_fields if field not in envelope]
    if missing:
        raise ValueError(f"error envelope missing required fields: {', '.join(missing)}")

    code = envelope.get("code")
    if code not in contract["error_contract"]["codes"]:
        raise ValueError(f"error envelope code is not contract-approved: {code}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Zig ABI contract checks against a built artifact or fixture symbols file."
    )
    parser.add_argument(
        "--contract",
        default=str(DEFAULT_CONTRACT_PATH),
        help="Path to Zig ABI contract JSON.",
    )
    parser.add_argument(
        "--artifact",
        help="Path to built Zig dynamic library or wasm artifact.",
    )
    parser.add_argument(
        "--symbols-file",
        help="Optional newline-delimited exported symbol fixture file (dry-run path).",
    )
    parser.add_argument(
        "--symbol-tool",
        choices=["auto", "nm", "readelf", "objdump"],
        default="auto",
        help="Symbol inspection backend when using --artifact.",
    )
    parser.add_argument(
        "--error-envelope-json",
        help="Optional JSON file to validate against contract error envelope rules.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not args.artifact and not args.symbols_file:
        print(
            "ARTIFACT_CHECK_ERROR: provide one of --artifact or --symbols-file",
            file=sys.stderr,
        )
        return 2

    contract_path = Path(args.contract)
    try:
        contract = load_contract(contract_path)
        validate_contract_data(contract)
    except ContractValidationError as exc:
        print(f"ARTIFACT_CHECK_ERROR: invalid contract: {exc}", file=sys.stderr)
        return 2

    required_symbols = _extract_required_symbols(contract)

    try:
        if args.symbols_file:
            exported_symbols = _load_symbols_from_file(Path(args.symbols_file))
            inspected_source = f"symbols fixture {args.symbols_file}"
        else:
            exported_symbols = _load_symbols_from_artifact(Path(args.artifact), args.symbol_tool)
            inspected_source = f"artifact {args.artifact}"
    except (FileNotFoundError, RuntimeError) as exc:
        print(f"ARTIFACT_CHECK_ERROR: {exc}", file=sys.stderr)
        return 3

    missing_symbols = [symbol for symbol in required_symbols if symbol not in exported_symbols]
    if missing_symbols:
        print(
            "ARTIFACT_CHECK_ERROR: missing required symbols: " + ", ".join(missing_symbols),
            file=sys.stderr,
        )
        return 4

    if args.error_envelope_json:
        try:
            _validate_error_envelope(Path(args.error_envelope_json), contract)
        except (FileNotFoundError, ValueError) as exc:
            print(f"ARTIFACT_CHECK_ERROR: {exc}", file=sys.stderr)
            return 5

    print(
        "zig abi artifact contract checks passed "
        f"({inspected_source}; required_symbols={len(required_symbols)}; "
        f"exported_symbols={len(exported_symbols)})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
