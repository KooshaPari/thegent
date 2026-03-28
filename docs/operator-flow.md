# Operator Flow

This document describes the day-to-day operations workflow for managing the Phenotype ecosystem.

## Daily Operations

### 1. Start the Server

```bash
# Start the local proxy server
helios run

# Or with custom config
helios run --config ~/.config/helios/config.toml
```

### 2. Manage Providers

```bash
# List all configured providers
helios providers list

# Add a new provider
helios providers add openai --api-key sk-...

# Remove a provider
helios providers remove openai
```

### 3. Monitor Status

```bash
# Check server status
helios status

# View logs
helios logs --tail 100

# Check provider health
helios providers health
```

## Troubleshooting

### Restart Flow

```bash
# Stop the server
helios stop

# Verify no processes running
helios status

# Clear cache if needed
helios cache clear

# Restart
helios run
```

### Auth Issues

```bash
# Refresh authentication
helios auth refresh --provider openai

# Re-authenticate
helios login openai

# Check token validity
helios auth status --provider openai
```
