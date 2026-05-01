# shell/zsh-thegent-integration/lib

Zsh integration library for thegent shell integration.

## Contents

- `async.zsh` - Async/zsh deferred execution utilities
- `completions.zsh` - Shell completion definitions
- `functions.zsh` - Core thegent shell functions
- `index.zsh` - Barrel export that sources all other .zsh files

## Usage

This library is auto-loaded by thegent's zsh integration.
Source `index.zsh` to load all library components:

```zsh
source /path/to/lib/index.zsh
```
