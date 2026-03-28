# domain_map API Reference

> **Source**: `src/thegent/cli/commands/domain_map.py`

Domain map command implementation.

Advisor-mode guidance for Cloudflare Tunnel + DNS domain mapping.
Apply mode is intentionally disabled until idempotent API execution is implemented.

---

## domain_map_cmd

```python
domain_map_cmd(domain: str, target: str, mode: str, registrar: str, dns_provider: str, tunnel_name: str, format: str)
```

Guide domain mapping setup (advisor mode) for Cloudflare Tunnel + DNS.

---

## parse_domain_mapping

```python
parse_domain_mapping(domain_input: str)
```

Parse a domain mapping input into structured data.

---

## validate_domain_mapping

```python
validate_domain_mapping(mapping: dict)
```

Validate a domain mapping and return any errors.

---

