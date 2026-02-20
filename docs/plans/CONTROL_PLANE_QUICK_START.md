# Control Plane — Quick Start

The Control Plane is a long-running service that manages configuration, session indexing, and tenant catalogs for `thegent`.

## Why use the Control Plane?

- **Multi-tenant configuration**: Manage settings for different projects/tenants in one place.
- **Centralized Session Index**: Fast discovery of running agents across all owners and scopes.
- **Dynamic Policy Resolution**: Update policies without restarting agents.
- **Observability**: Built-in metrics and OTel tracing.

## Getting Started

### 1. Start the Stack (Recommended)

The most intuitive way to start the Control Plane and its associated services (MCP, CLIProxy) is using the unified `up` command:

```bash
thegent up
```

This starts the entire service stack in the background using `process-compose`.

### 2. Manual Control (Optional)

If you only need the Control Plane for specific debugging:

```bash
# Start just the CP stack
thegent cp start

# Or run the CP server in foreground
thegent cp run --port 3848
```

### 3. Verify the setup

```bash
thegent cp status
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
# Run a task with tenant context
thegent run --tenant acme "Summarize our latest plan"

# Or show its resolved config
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
