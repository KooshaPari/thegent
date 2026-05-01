# hooks/lib

Shared shell library for thegent git hooks.

## Contents

- `common.sh` - Common shell functions for git hooks
- `spiral-config.sh` - Configuration management for hooks

## Usage

Source these files from your git hook scripts:

```bash
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/common.sh"
```
