# Domain Mapping Guide (Porkbun + Cloudflare Tunnel)

## Purpose

This guide defines the first implementation contract for:

- `thegent domain map --mode advisor`

The command is advisor-first by design. It validates input assumptions and emits exact operational steps and commands to map a user domain to a local service through Cloudflare Tunnel.

## Command Contract

```bash
thegent domain map <domain> \
  --target http://localhost:3847 \
  --mode advisor \
  --registrar porkbun \
  --dns-provider cloudflare \
  --tunnel-name thegent \
  --format rich
```

Parameters:

- `<domain>`: Fully qualified domain or subdomain.
- `--target`: Local upstream URL for tunnel ingress.
- `--mode`: `advisor` or `apply`.
- `--registrar`: Registrar label used in generated plan.
- `--dns-provider`: DNS provider label used in generated plan.
- `--tunnel-name`: Cloudflare tunnel name.
- `--format`: `rich`, `json`, or `md`.

## Advisor Mode Behavior

Advisor mode:

1. Validates domain shape and target URL.
   - Domain must be a valid FQDN (`example.com`, `app.example.com`).
   - Target must be an absolute URL (`http://localhost:3847`).
2. Emits deterministic steps:
   - registrar nameserver handoff to Cloudflare
   - tunnel creation and auth
   - ingress mapping from hostname to local target
   - DNS CNAME mapping to tunnel endpoint
   - readiness and verification checks
3. Emits command snippets for operator execution.

`--mode apply` intentionally exits non-zero until API-token based idempotent execution is implemented.

## Example

```bash
thegent domain map app.example.com --target http://localhost:3847 --format md
```

Outputs:

- Step-by-step checklist
- Recommended `cloudflared` commands
- Readiness checks for later automation
- Structured metadata in JSON mode: `registrar`, `dns_provider`, `assumptions`
