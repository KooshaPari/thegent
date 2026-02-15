#!/usr/bin/env python3
"""Verify that docs/contracts/CONTRACT_AUTHORITY.md matches the implementation.

XK3: Contract authority publication (CI doc/impl sync).
"""

import re
import sys
from pathlib import Path

from thegent.contracts.registry import get_registry

DOC_PATH = Path("docs/contracts/CONTRACT_AUTHORITY.md")


def verify_registry_table() -> bool:
    registry = get_registry()
    versions = registry.list_versions()

    if not DOC_PATH.exists():
        return False

    content = DOC_PATH.read_text()

    # Simple check: each registered version must be present in the doc
    missing = []
    for v in versions:
        # Check for presence of contract_id and version in the registry table section
        # Look for | csm | csm-v1 | ... style entries
        pattern = rf"\| {v.contract_id} \| {v.version} \|"
        if not re.search(pattern, content):
            missing.append(f"{v.contract_id}@{v.version}")

    return not missing


def verify_csm_fields() -> bool:
    # Verify that fields in CanonicalStructuredMessage (src/thegent/contracts/csm/v1/__init__.py)
    # match the table in Section 3 of the doc.
    import dataclasses

    from thegent.contracts.csm.v1 import CanonicalStructuredMessage

    fields = [f.name for f in dataclasses.fields(CanonicalStructuredMessage)]

    content = DOC_PATH.read_text()

    # Extract fields from the markdown table in Section 3
    # Look for | field_name | type | ...
    found_fields = re.findall(r"\| ([a-z_]+) \| [a-z\[\], ]+ \|", content)

    missing = [f for f in fields if f not in found_fields and f != "raw_payload"]  # raw_payload usually internal
    return not missing


if __name__ == "__main__":
    ok = True
    if not verify_registry_table():
        ok = False
    if not verify_csm_fields():
        ok = False

    if not ok:
        sys.exit(1)
    sys.exit(0)
