# 🚀 BytePort - START HERE

## Quick Fix & Start

### 1. Reset to Clean State

```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/BytePort
./quick_fix.sh
```

### 2. Run Setup (First Time Only)

```bash
./setup.sh
```

### 3. Start BytePort

```bash
./byteport.py --dev
```

This shows all output so you can see what's happening!

## 🎯 What You'll See

```
============================================================
🎯 BytePort Orchestrator Starting...
============================================================
🧹 Cleaning up existing processes...
🚀 Starting service: backend
   Assigned port: 8080
   ✓ Process started (PID: XXXXX)
   [Backend startup logs will appear here]
   ✓ Service ready on port 8080
   ✓ Tunnel: http://localhost:8080/api/v1

🚀 Starting service: frontend
   Assigned port: 3000  ← Different port!
   ✓ Process started (PID: XXXXX)
   [Frontend startup logs will appear here]
   ✓ Service ready on port 3000
   ✓ Tunnel: http://localhost:3000
```

## 🔧 If Issues Occur

### Port Conflict
Both services get same port? Run:
```bash
./quick_fix.sh
./byteport.py --dev
```

### Service Won't Start
See error in the output (dev mode shows everything).

Common fixes:
```bash
# Database issue?
pg_isready -h localhost -p 5432

# Go dependencies?
cd backend/api && GOCACHE=$(pwd)/.gocache GOMODCACHE=$(pwd)/.gomodcache GOPROXY=off GONOSUMDB=* go build -mod=mod ./...

# Frontend dependencies?
cd /Users/kooshapari/temp-PRODVERCEL/Rust/webApp/byte_port/frontend/web-next && npm install
```

### Tunnel "Unsupported Protocol"
Service isn't running yet. Check:
```bash
# Is backend actually listening?
lsof -i :8000

# Test manually
cd backend/api
PORT=8080 GOCACHE=$(pwd)/.gocache GOMODCACHE=$(pwd)/.gomodcache go run .
```

## 📚 Documentation

- **INSTALLATION.md** - Complete installation guide
- **QUICKSTART.md** - 3-step quick start
- **FIXES_AND_SOLUTIONS.md** - Troubleshooting
- **KINFRA_INTEGRATION.md** - Architecture details

## ✅ What Was Fixed

1. ✅ Port allocation now excludes already-assigned ports
2. ✅ Dev mode shows all stdout/stderr
3. ✅ Process monitor warning fixed
4. ✅ Pheno-SDK TUI components integrated
5. ✅ KInfra properly configured
6. ✅ Zen PostgreSQL integration working

## 🎯 Expected Result

After running `./byteport.py --dev`:
- Backend on http://localhost:8000 → http://localhost:8080/api/v1
- Frontend on http://localhost:8001 → http://localhost:3000
- All output visible in terminal
- Auto-restart on changes (dev mode)

---

**TL;DR**: Run `./quick_fix.sh` then `./byteport.py --dev`
