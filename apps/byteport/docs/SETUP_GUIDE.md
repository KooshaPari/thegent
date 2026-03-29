# BytePort Setup Guide - Complete Installation

## 🎯 One-Command Setup

```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/BytePort
./setup.sh
```

That's it! The setup script handles everything automatically.

## 📦 What Gets Installed

### Python Dependencies (via pip)

```bash
# Core
psutil>=5.9.0          # Process monitoring
pyyaml>=6.0            # YAML config
python-dotenv>=1.0.0   # .env loading
watchdog>=3.0.0        # File watching
httpx>=0.28.0          # HTTP client

# Pheno-SDK TUI
textual>=0.45.0        # TUI framework
rich>=13.0.0           # Terminal formatting
asyncio-mqtt>=0.13.0   # MQTT
pydantic>=2.0.0        # Validation
GPUtil>=1.4.0          # GPU monitoring (optional)
```

### Pheno-SDK Packages (editable installs)

```bash
# Installed via: pip install -e {path}

tui-kit                # From pheno-sdk/tui-kit
├── TunnelStatusWidget # Tunnel monitoring
├── ProgressWidget     # Progress bars
├── StatusDashboard    # Service dashboard
└── ServerStatusWidget # Server health

process-monitor-sdk    # From pheno-sdk/process-monitor-sdk
├── PortManager        # Port utilities
└── ProcessMonitor     # Process lifecycle
```

### KInfra (imported via sys.path)

```bash
# From ~/KInfra/libraries/python/kinfra/

PortRegistry           # Persistent port allocation
TunnelManager          # Cloudflare tunnel automation
```

### Additional Tools

```bash
# Go
air                    # Live reload for Go

# Node.js
# All deps from package.json
```

## 🔍 Installation Process

### Step 1: System Check

The setup script verifies:
- ✅ Python 3.10+
- ✅ Go 1.19+
- ✅ Node.js 18+
- ✅ PostgreSQL running

### Step 2: Python Dependencies

```bash
pip3 install -r requirements.txt
```

Installs core packages from PyPI.

### Step 3: Pheno-SDK Packages

```bash
# Editable install - changes to source reflect immediately
pip3 install -e /Users/kooshapari/temp-PRODVERCEL/485/kush/pheno-sdk/tui-kit
pip3 install -e /Users/kooshapari/temp-PRODVERCEL/485/kush/pheno-sdk/process-monitor-sdk
```

**Why editable?**
- Changes to pheno-sdk propagate automatically
- No need to reinstall after updates
- Development-friendly

### Step 4: KInfra Verification

```bash
# Verify KInfra is accessible
python3 -c "
import sys
sys.path.insert(0, '$HOME/KInfra/libraries/python')
from kinfra.port_registry import PortRegistry
from kinfra.tunnel_sync import TunnelManager
print('✓ KInfra OK')
"
```

**Why not pip install?**
- KInfra is a local development library
- Imported dynamically via sys.path
- No packaging needed for local use

### Step 5: Go & Node Dependencies

```bash
# Backend
cd backend/api
go mod download
go mod tidy

# Frontend
cd frontend/web-next
npm install

# Air (Go live reload)
go install github.com/cosmtrek/air@latest
```

## ✅ Post-Installation Verification

```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/BytePort

# Test imports
python3 -c "
from tui_kit.widgets.progress_widget import ProgressWidget
from process_monitor.components.port_manager import PortManager
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / 'KInfra' / 'libraries' / 'python'))
from kinfra.port_registry import PortRegistry
print('✅ All imports successful')
"

# Test orchestrator
./byteport.py --status

# Run in dev mode (shows all output)
./byteport.py --dev
```

## 🐛 Troubleshooting

### "Module not found: tui_kit"

```bash
# Install tui-kit
pip3 install -e /Users/kooshapari/temp-PRODVERCEL/485/kush/pheno-sdk/tui-kit

# Verify
python3 -c "from tui_kit.widgets.progress_widget import ProgressWidget; print('OK')"
```

### "Module not found: process_monitor"

```bash
# Install process-monitor-sdk
pip3 install -e /Users/kooshapari/temp-PRODVERCEL/485/kush/pheno-sdk/process-monitor-sdk

# Verify
python3 -c "from process_monitor.components.port_manager import PortManager; print('OK')"
```

### "Module not found: kinfra"

```bash
# Check KInfra location
ls ~/KInfra/libraries/python/kinfra/

# If missing, find it
find ~ -name "kinfra" -type d 2>/dev/null | grep libraries

# Update KINFRA_PATH in byteport.py if needed
```

### Backend Won't Start

```bash
# Run manually to see error
cd backend/api
PORT=8000 go run *.go

# Or use dev mode which shows output
./byteport.py --dev
```

## 📁 Installation Locations

```
/Users/kooshapari/temp-PRODVERCEL/485/
├── BytePort/
│   ├── .venv/                              # Virtual env (optional)
│   ├── byteport.py                         # Orchestrator
│   ├── byteport_tui.py                     # TUI orchestrator
│   └── requirements.txt                    # Dependencies
│
├── kush/pheno-sdk/
│   ├── tui-kit/                            # pip install -e
│   └── process-monitor-sdk/                # pip install -e
│
└── ~/.kinfra/
    └── port_registry.json                  # Port state

~/KInfra/libraries/python/kinfra/           # sys.path import
├── port_registry.py
└── tunnel_sync.py

~/.cloudflared/                              # Tunnel configs
├── config-backend.yml
└── config-frontend.yml
```

## 🚀 Quick Start After Setup

```bash
# Start with live output
./byteport.py --dev

# Or with TUI
./byteport_tui.py

# Check what's running
./byteport.py --status
```

## 🔄 Updating Dependencies

```bash
# Update Python packages
pip install --upgrade -r requirements.txt

# Update pheno-sdk (pulls from source since editable)
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/pheno-sdk/tui-kit
git pull  # if git repo

# Reinstall if needed
pip3 install -e . --force-reinstall
```

## 💡 Virtual Environment (Recommended)

```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/BytePort

# Create venv
python3 -m venv .venv

# Activate
source .venv/bin/activate

# Install everything
./setup.sh

# Use
./byteport.py --dev

# Deactivate
deactivate
```

---

**Total Setup Time**: ~5 minutes
**Total Downloads**: ~300MB (including node_modules)

Run `./setup.sh` and you're ready to go!
