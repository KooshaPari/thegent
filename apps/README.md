# Apps

End-user applications and CLIs for the Phenotype ecosystem.

## Overview

This directory contains:
- Desktop applications
- Web applications
- Command-line interfaces (CLIs)
- Mobile apps (if applicable)

## Directory Structure

```
apps/
├── web/                # Web applications
├── desktop/            # Desktop applications
├── cli/                # Command-line tools
└── mobile/              # Mobile applications
```

## Web Applications

```
apps/web/
├── frontend/           # Frontend applications
└── dashboard/           # Admin dashboards
```

## Desktop Applications

```
apps/desktop/
├── electron/           # Electron-based apps
├── tauri/              # Tauri-based apps
└── native/              # Platform-native apps
```

## CLI Applications

```
apps/cli/
└── [cli-name]/
    ├── src/
    ├── Cargo.toml      # For Rust CLIs
    ├── package.json    # For Node CLIs
    └── README.md
```

## Development

```bash
# Build CLI
cargo build --release

# Build web app
cd apps/web && npm install && npm run build

# Run desktop app
cd apps/desktop && npm run dev
```

## References

- [ADR-0005: Top-Level Directory Structure](../governance/adrs/0005-top-level-directory-structure.md)
