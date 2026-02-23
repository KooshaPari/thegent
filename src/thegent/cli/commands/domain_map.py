"""Domain map command implementation.

Advisor-mode guidance for Cloudflare Tunnel + DNS domain mapping.
Apply mode is intentionally disabled until idempotent API execution is implemented.
"""

from __future__ import annotations

import json
import re
from urllib.parse import urlparse


def parse_domain_mapping(domain_input: str) -> dict:
    """Parse a domain mapping input into structured data."""
    parsed = urlparse(domain_input) if "://" in domain_input else urlparse(f"https://{domain_input}")
    return {
        "domain": parsed.netloc or parsed.path,
        "scheme": parsed.scheme or "https",
        "path": parsed.path,
    }


def validate_domain_mapping(mapping: dict) -> list[str]:
    """Validate a domain mapping and return any errors."""
    errors = []
    if not mapping.get("domain"):
        errors.append("Domain is required")
    return errors
