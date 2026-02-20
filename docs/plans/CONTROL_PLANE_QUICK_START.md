# Control Plane — Quick Start

The Control Plane is a long-running service that manages configuration, session indexing, and tenant catalogs for `thegent`.

## Why use the Control Plane?

- **Multi-tenant configuration**: Manage settings for different projects/tenants in one place.
- **Centralized Session Index**: Fast discovery of running agents across all owners and scopes.
- **Dynamic Policy Resolution**: Update policies without restarting agents.
- **Observability**: Built-in metrics and OTel tracing.

## Getting Started

### 1. Start the Control Plane

You can start the control plane manually:

```bash
thegent control-plane serve --port 3848
```

Or via `process-compose` (recommended):

```bash
thegent control-plane start
```

### 2. Configure the CLI to use it

Set the `THGENT_CONTROL_PLANE_URL` environment variable:

```bash
export THGENT_CONTROL_PLANE_URL=http://127.0.0.1:3848
```

### 3. Verify the setup

```bash
thegent control-plane status
thegent config show
```

## Multi-Tenant Setup

### 1. Create a tenant config

Tenants are stored in `~/.thegent/tenants/<tenant_id>.yaml`.

```bash
mkdir -p ~/.thegent/tenants
echo "default_timeout: 1800" > ~/.thegent/tenants/acme.yaml
```

### 2. Use the tenant in CLI

```bash
thegent run --tenant acme "Do something"
```

Or show its resolved config:

```bash
thegent config show --tenant acme
```

## Session Management

The Control Plane indexes sessions from all scopes.

```bash
thegent session list
thegent session show <id>
```

## MCP Integration

The control plane is automatically used by the `thegent` MCP server when `THGENT_CONTROL_PLANE_URL` is set. Use the `thegent_config_resolve` tool to get dynamic settings.
