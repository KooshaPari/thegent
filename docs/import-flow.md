# Import Flow

This document describes how to import and set up packages from the Phenotype ecosystem.

## Go Packages

### Import via go.mod

```go
import (
    "github.com/kooshapari/phenotype-go-kit/pkg/llmproxy"
    "github.com/kooshapari/phenotype-go-kit/pkg/auth"
)
```

### Install

```bash
go get github.com/kooshapari/phenotype-go-kit/pkg/llmproxy@latest
```

## NPM Packages

### Install

```bash
npm install @phenotype/sdk
# or
bun add @phenotype/sdk
```

### Import

```typescript
import { HeliosClient } from '@phenotype/sdk';
```

## Python Packages

### Install

```bash
pip install phenotype-sdk
# or
uv pip install phenotype-sdk
```

### Import

```python
from phenotype import HeliosClient
```

## Configuration

### Go Config

```go
cfg := &llmproxy.Config{
    Port: 8080,
    Providers: []string{"openai", "anthropic"},
}
```

### Environment Variables

```bash
export HELIOS_PORT=8080
export HELIOS_LOG_LEVEL=debug
export HELIOS_CONFIG_PATH=~/.config/helios/config.toml
```
