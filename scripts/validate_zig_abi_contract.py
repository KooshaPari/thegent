#!/usr/bin/env python3
"""Validate the Zig ABI runtime contract envelope and symbol declarations."""

from __future__ import annotations

import argparse
import orjson as json
import sys
from pathlib import Path
from typing import Any

DEFAULT_CONTRACT_PATH = Path("contracts/runtime/zig_abi_contract_v1.json")
REQUIRED_READINESS_TESTS = {
    "abi_symbol_presence",
    "ffi_roundtrip_smoke",
    "error_envelope_conformance",
    "memory_free_safety",
    "wasm_target_build",
}


class ContractValidationError(ValueError):
    """Raised when the contract JSON does not satisfy required constraints."""


def _expect_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractValidationError(f"{label} must be an object")
    return value


def _expect_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractValidationError(f"{label} must be a non-empty string")
    return value


def _expect_string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ContractValidationError(f"{label} must be a non-empty array")
    out: list[str] = []
    for idx, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            raise ContractValidationError(f"{label}[{idx}] must be a non-empty string")
        out.append(item)
    return out


def load_contract(contract_path: Path) -> dict[str, Any]:
    if not contract_path.exists():
        raise ContractValidationError(f"contract file does not exist: {contract_path}")

    try:
        data = json.loads(contract_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ContractValidationError(f"invalid JSON in contract: {exc}") from exc

    return _expect_mapping(data, "contract")


def validate_contract_data(contract: dict[str, Any]) -> None:
    _expect_string(contract.get("contract_id"), "contract.contract_id")
    _expect_string(contract.get("version"), "contract.version")

    abi = _expect_mapping(contract.get("abi"), "contract.abi")
    _expect_string(abi.get("calling_convention"), "contract.abi.calling_convention")

    symbols = abi.get("symbols")
    if not isinstance(symbols, list) or not symbols:
        raise ContractValidationError("contract.abi.symbols must be a non-empty array")

    required_symbol_names: list[str] = []
    for idx, symbol in enumerate(symbols):
        symbol_obj = _expect_mapping(symbol, f"contract.abi.symbols[{idx}]")
        name = _expect_string(symbol_obj.get("name"), f"contract.abi.symbols[{idx}].name")
        _expect_string(symbol_obj.get("kind"), f"contract.abi.symbols[{idx}].kind")
        _expect_string(symbol_obj.get("signature"), f"contract.abi.symbols[{idx}].signature")
        stability = _expect_string(symbol_obj.get("stability"), f"contract.abi.symbols[{idx}].stability")
        if stability == "required":
            required_symbol_names.append(name)

    if not required_symbol_names:
        raise ContractValidationError("contract.abi.symbols must include at least one required symbol")

    wire_protocol = _expect_mapping(contract.get("wire_protocol"), "contract.wire_protocol")
    request_encoding = _expect_string(
        wire_protocol.get("request_encoding"),
        "contract.wire_protocol.request_encoding",
    )
    response_encoding = _expect_string(
        wire_protocol.get("response_encoding"),
        "contract.wire_protocol.response_encoding",
    )
    if request_encoding != "utf-8-json" or response_encoding != "utf-8-json":
        raise ContractValidationError(
            "contract.wire_protocol.request_encoding and response_encoding must both be 'utf-8-json'"
        )

    error_contract = _expect_mapping(contract.get("error_contract"), "contract.error_contract")
    error_envelope = _expect_mapping(
        error_contract.get("error_envelope"),
        "contract.error_contract.error_envelope",
    )
    required_fields = _expect_string_list(
        error_envelope.get("required_fields"),
        "contract.error_contract.error_envelope.required_fields",
    )
    missing_required_fields = {"code", "message", "stage"} - set(required_fields)
    if missing_required_fields:
        raise ContractValidationError(
            "contract.error_contract.error_envelope.required_fields missing required keys: "
            + ", ".join(sorted(missing_required_fields))
        )

    optional_fields = error_envelope.get("optional_fields")
    if optional_fields is not None:
        _expect_string_list(optional_fields, "contract.error_contract.error_envelope.optional_fields")

    _expect_string_list(error_contract.get("codes"), "contract.error_contract.codes")

    validation = _expect_mapping(contract.get("validation"), "contract.validation")
    required_tests = _expect_string_list(validation.get("required_tests"), "contract.validation.required_tests")
    if len(set(required_tests)) != len(required_tests):
        raise ContractValidationError("contract.validation.required_tests must not contain duplicates")

    missing_readiness_tests = sorted(REQUIRED_READINESS_TESTS - set(required_tests))
    if missing_readiness_tests:
        raise ContractValidationError(
            "contract.validation.required_tests missing readiness gates: " + ", ".join(missing_readiness_tests)
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate contracts/runtime/zig_abi_contract_v1.json shape and envelope rules."
    )
    parser.add_argument(
        "--contract",
        default=str(DEFAULT_CONTRACT_PATH),
        help="Path to Zig ABI contract JSON.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    contract_path = Path(args.contract)

    try:
        contract = load_contract(contract_path)
        validate_contract_data(contract)
    except ContractValidationError as exc:
        print(f"CONTRACT_VALIDATION_ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"zig abi contract validation passed: {contract_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
