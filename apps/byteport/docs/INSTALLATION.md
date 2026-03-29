# BytePort Installation Guide

## 📦 Complete Installation Instructions

### Prerequisites

1. **Python 3.10+**
   ```bash
   python3 --version  # Should be 3.10 or higher
   ```

2. **Go 1.19+**
   ```bash
   go version
   ```

3. **Node.js 18+**
   ```bash
   node --version
   ```

4. **PostgreSQL 12+**
   ```bash
   pg_isready -h localhost -p 5432
   ```

5. **Cloudflared** (optional, for tunnels)
   ```bash
   # macOS
   brew install cloudflared

   # Linux
   wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
   sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared
   sudo chmod +x /usr/local/bin/cloudflared

   # Authenticate
   cloudflared tunnel login
   ```

## 🚀 Quick Installation

### Option 1: Automated Setup (Recommended)

```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/BytePort
./setup.sh
```

This automatically installs:
- ✅ Python dependencies from requirements.txt
- ✅ Pheno-SDK tui-kit (editable install)
- ✅ Pheno-SDK process-monitor-sdk (editable install)
- ✅ KInfra verification
- ✅ Go dependencies (backend)
- ✅ Node.js dependencies (frontend)
- ✅ Air for Go live reload

### Option 2: Manual Installation

#### Step 1: Python Dependencies

```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/BytePort

# Core dependencies
pip3 install -r requirements.txt

# Pheno-SDK packages (editable installs)
pip3 install -e /Users/kooshapari/temp-PRODVERCEL/485/kush/pheno-sdk/tui-kit
pip3 install -e /Users/kooshapari/temp-PRODVERCEL/485/kush/pheno-sdk/process-monitor-sdk
```

#### Step 2: Verify KInfra

```bash
# KInfra is imported via sys.path, not pip installed
# Verify it's accessible:
python3 -c "
import sys
sys.path.insert(0, '$HOME/KInfra/libraries/python')
from kinfra.port_registry import PortRegistry
from kinfra.tunnel_sync import TunnelManager
print('✓ KInfra OK')
"
```

#### Step 3: Go Dependencies

```bash
cd backend/api
GOCACHE=$(pwd)/.gocache GOMODCACHE=$(pwd)/.gomodcache GOPROXY=off GONOSUMDB=* go build -mod=mod ./...

# Optional: install Air for live reload
go install github.com/cosmtrek/air@latest
```

#### Step 4: Frontend Dependencies

```bash
cd /Users/kooshapari/temp-PRODVERCEL/Rust/webApp/byte_port/frontend/web-next
npm install
```

## 📋 Dependencies Explained

### Core Python Packages (requirements.txt)

| Package | Version | Purpose |
|---------|---------|---------|
| `psutil` | >=5.9.0 | Process monitoring, port checking |
| `pyyaml` | >=6.0 | Configuration file parsing |
| `python-dotenv` | >=1.0.0 | .env file loading |
| `watchdog` | >=3.0.0 | File watching for live reload |
| `httpx` | >=0.28.0 | HTTP client for health checks |
| `textual` | >=0.45.0 | TUI framework |
| `rich` | >=13.0.0 | Terminal formatting |
| `asyncio-mqtt` | >=0.13.0 | MQTT support (tui-kit) |
| `pydantic` | >=2.0.0 | Data validation |
| `GPUtil` | >=1.4.0 | GPU monitoring (optional) |

### Pheno-SDK Packages (Editable Installs)

**tui-kit** - Terminal UI components
- Location: `/Users/kooshapari/temp-PRODVERCEL/485/kush/pheno-sdk/tui-kit`
- Install: `pip3 install -e {path}`
- Provides:
  - `TunnelStatusWidget` - Tunnel monitoring
  - `ProgressWidget` - Progress bars
  - `StatusDashboard` - Service dashboard
  - `ServerStatusWidget` - Server health

**process-monitor-sdk** - Process lifecycle management
- Location: `/Users/kooshapari/temp-PRODVERCEL/485/kush/pheno-sdk/process-monitor-sdk`
- Install: `pip3 install -e {path}`
- Provides:
  - `PortManager` - Port allocation helpers
  - `ProcessMonitor` - Process lifecycle

### KInfra (Path Import)

**KInfra** - Infrastructure automation
- Location: `~/KInfra/libraries/python`
- Install: **NOT via pip** - imported via `sys.path`
- Provides:
  - `PortRegistry` - Persistent port management
  - `TunnelManager` - Cloudflare tunnel automation

## 🔧 Troubleshooting Installation

### Python Package Conflicts

```bash
# Create fresh virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -e /Users/kooshapari/temp-PRODVERCEL/485/kush/pheno-sdk/tui-kit
pip install -e /Users/kooshapari/temp-PRODVERCEL/485/kush/pheno-sdk/process-monitor-sdk
```

### Pheno-SDK Not Found

```bash
# Verify path
ls /Users/kooshapari/temp-PRODVERCEL/485/kush/pheno-sdk/tui-kit
ls /Users/kooshapari/temp-PRODVERCEL/485/kush/pheno-sdk/process-monitor-sdk

# If missing, check alternative locations
find /Users/kooshapari -name "tui-kit" -type d 2>/dev/null
```

### KInfra Not Found

```bash
# Check KInfra location
ls ~/KInfra/libraries/python/kinfra/

# If symlink broken, find real location
readlink ~/KInfra

# Update path in byteport.py if needed
```

### Textual/Rich Import Errors

```bash
# Reinstall with specific versions
pip3 install textual==0.45.1 rich==13.7.0
```

### Go Dependencies Fail

```bash
cd backend/api

# Clear cache and retry
go clean -modcache
go mod download
go mod tidy

# Verify
go build .
```

## ✅ Verification

After installation, verify everything works:

```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/BytePort

# Test Python imports
python3 -c "
from tui_kit.widgets.progress_widget import ProgressWidget
from process_monitor.components.port_manager import PortManager
import sys
sys.path.insert(0, '$HOME/KInfra/libraries/python')
from kinfra.port_registry import PortRegistry
from kinfra.tunnel_sync import TunnelManager
print('✅ All imports successful')
"

# Test orchestrator
./byteport.py --status

# Test TUI
./byteport_tui.py --help
```

## 📁 Installation Locations

```
System:
├── ~/KInfra/libraries/python/
│   └── kinfra/
│       ├── port_registry.py
│       └── tunnel_sync.py
│
├── /Users/kooshapari/temp-PRODVERCEL/485/kush/pheno-sdk/
│   ├── tui-kit/              # pip install -e
│   │   └── tui_kit/
│   └── process-monitor-sdk/  # pip install -e
│       └── process_monitor/
│
└── /Users/kooshapari/temp-PRODVERCEL/485/BytePort/
    ├── .venv/                # Virtual environment (created by you)
    ├── byteport.py           # Orchestrator
    ├── byteport_tui.py       # TUI orchestrator
    └── requirements.txt      # Dependencies
```

## 🐍 Virtual Environment (Recommended)

```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/BytePort

# Create venv
python3 -m venv .venv

# Activate
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows

# Install everything
./setup.sh

# Use orchestrator
./byteport.py --dev

# Deactivate when done
deactivate
```

## 🔄 Updating Dependencies

```bash
# Update Python packages
pip install --upgrade -r requirements.txt

# Update pheno-sdk (pulls latest from editable install)
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/pheno-sdk/tui-kit
git pull  # if it's a git repo

cd /Users/kooshapari/temp-PRODVERCEL/485/kush/pheno-sdk/process-monitor-sdk
git pull

# Update KInfra
cd ~/KInfra
git pull

# Update Go deps
cd /Users/kooshapari/temp-PRODVERCEL/485/BytePort/backend/api
go get -u ./...
go mod tidy

# Update Node deps
cd /Users/kooshapari/temp-PRODVERCEL/Rust/webApp/byte_port/frontend/web-next
npm update
```

## 🎯 Quick Test

After installation:

```bash
# Test basic orchestrator
./byteport.py --status

# Test TUI mode
./byteport_tui.py --dev

# Should show:
# - Service startup progress
# - Port allocations
# - Tunnel creation
# - Live dashboard
```

## 📚 Next Steps

After successful installation:
1. Read [QUICKSTART.md](./QUICKSTART.md) for usage
2. Configure `.env` files for your environment
3. Run `./byteport.py --dev` to start in development mode
4. Access services at assigned ports or public URLs

## 🆘 Getting Help

If installation fails:
1. Check each prerequisite is installed
2. Verify paths to pheno-sdk and KInfra
3. Try manual installation steps
4. Check error messages for missing dependencies
5. Create fresh virtual environment and retry

---

**Installation Time**: ~5 minutes (with good internet)
**Disk Space**: ~500MB (including node_modules)
