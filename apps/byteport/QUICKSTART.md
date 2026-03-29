# BytePort Quick Start Guide

## 🎯 Get Started in 3 Steps

### Step 1: Setup (One Time)

```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/BytePort
./setup.sh
```

### Step 2: Start BytePort

```bash
./byteport.py --dev
```

### Step 3: Access

- **Frontend**: http://localhost:{assigned-port} or https://byte.kooshapari.com
- **API**: http://localhost:{assigned-port} or https://api.byte.kooshapari.com/api

## 💡 Key Features

### Automatic Port Management
No more port conflicts! The orchestrator assigns random available ports automatically.

### Instant Public URLs
Cloudflare tunnels give you production URLs instantly:
- `byte.kooshapari.com` → Frontend
- `api.byte.kooshapari.com/api` → Backend API

### Live Reload
Change code, see results instantly:
- Backend: Air watches `.go` files
- Frontend: Next.js Fast Refresh

### One Command Control
```bash
./byteport.py          # Start
./byteport.py --stop   # Stop
./byteport.py --status # Check status
```

## 🔧 Configuration

### Environment Variables

**Shared** (`BytePort/.env`):
```bash
DATABASE_URL=host=localhost user=zen password=zen dbname=zen_mcp port=5432 sslmode=disable
JWT_SECRET=your-secret
```

**Backend** (`backend/.env`):
```bash
GIN_MODE=debug
ALLOWED_ORIGINS=http://localhost:*,https://byte.kooshapari.com
```

**Frontend** (`frontend/.env.local`):
```bash
NEXT_PUBLIC_API_URL=https://api.byte.kooshapari.com/api
```

## 📝 Common Tasks

### Development

```bash
# Start with live reload
./byteport.py --dev

# Watch logs in real-time
# (Output shows in terminal)
```

### Production

```bash
# Start all services
./byteport.py

# Runs in background, monitors health
```

### Troubleshooting

```bash
# Stop everything
./byteport.py --stop

# Check what's running
./byteport.py --status

# Manual cleanup if needed
pkill -f byteport
lsof -ti:8080 | xargs kill -9
```

## 📚 More Info

- **Full Documentation**: See [KINFRA_INTEGRATION.md](./KINFRA_INTEGRATION.md)
- **Orchestration Details**: See [ORCHESTRATION.md](./ORCHESTRATION.md)
- **Database Setup**: See [DATABASE_SETUP.md](./DATABASE_SETUP.md)

## ✅ Verification

After setup, verify:

```bash
# Check dependencies
python3 --version  # 3.8+
go version         # 1.19+
node --version     # 18+

# Check database
pg_isready -h localhost -p 5432

# Check cloudflared (optional)
cloudflared version

# Check Air (optional)
air -v
```

## 🆘 Need Help?

```bash
# Show help
./byteport.py --help

# Check service logs
./byteport.py --dev  # Shows live output
```

**That's it!** BytePort handles everything else automatically.
