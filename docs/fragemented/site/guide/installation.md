# Installation

## Requirements

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.12+ | Required |
| Rust | stable | Required for native extensions |
| Bun | latest | Needed for docsite dev/build |

## Install Methods

### Bootstrap Script (recommended)

```bash
# macOS / Linux
curl -fsSL https://raw.githubusercontent.com/kooshapari/thegent/main/scripts/bootstrap.sh | sh -s -- install

# Windows (PowerShell)
irm https://raw.githubusercontent.com/kooshapari/thegent/main/scripts/install.ps1 | iex
```

### pip

```bash
pip install thegent
```

### From Source

```bash
git clone https://github.com/kooshapari/thegent
cd thegent
pip install -e .
thegent install -t all
thegent install-shims
thegent setup --hooks
```

## Shell Integration

```bash
# zsh
echo 'eval "$(thegent shell-init zsh)"' >> ~/.zshrc
source ~/.zshrc
```

## Verify

```bash
thegent doctor
thegent run "installation smoke test" free
```

If verification fails, continue with [Operations Troubleshooting](/operations/troubleshooting).
