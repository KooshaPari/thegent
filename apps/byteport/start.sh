#!/bin/bash
# BytePort Simple Launcher
# Quick production start without extra dependencies

set -e

BYTEPORT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BYTEPORT_ROOT"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo ""
    echo "================================================"
    echo -e "${BLUE}$1${NC}"
    echo "================================================"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC}  $1"
}

# Parse arguments
MODE="production"
PORT_API=8080
PORT_FRONTEND=3000

while [[ $# -gt 0 ]]; do
    case $1 in
        --dev)
            MODE="development"
            shift
            ;;
        --local)
            MODE="local"
            shift
            ;;
        --api-port)
            PORT_API="$2"
            shift 2
            ;;
        --frontend-port)
            PORT_FRONTEND="$2"
            shift 2
            ;;
        --help)
            echo "BytePort Simple Launcher"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --dev               Run in development mode"
            echo "  --local             Run in local mode (localhost only)"
            echo "  --api-port PORT     API port (default: 8080)"
            echo "  --frontend-port PORT Frontend port (default: 3000)"
            echo "  --help              Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                  # Production mode"
            echo "  $0 --dev            # Development mode"
            echo "  $0 --local          # Local development"
            echo ""
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

print_header "BytePort Launcher - $MODE Mode"

# Check prerequisites
echo ""
echo "Checking prerequisites..."

if ! command -v go &> /dev/null; then
    print_error "Go not found. Please install Go 1.19+"
    exit 1
fi
print_success "Go $(go version | awk '{print $3}')"

if ! command -v node &> /dev/null; then
    print_error "Node.js not found. Please install Node.js 18+"
    exit 1
fi
print_success "Node.js $(node --version)"

if command -v pnpm &> /dev/null; then
    print_success "pnpm $(pnpm --version)"
    USE_PNPM=true
else
    print_warning "pnpm not found, using npm"
    USE_PNPM=false
fi

# Setup environment
print_header "Setting up environment"

# API environment
export PORT=$PORT_API
export GOCACHE="$BYTEPORT_ROOT/backend/api/.gocache"
export GOMODCACHE="$BYTEPORT_ROOT/backend/api/.gomodcache"

# Create cache directories
mkdir -p "$GOCACHE" "$GOMODCACHE"

# Frontend environment
export NEXT_PUBLIC_API_URL="http://localhost:$PORT_API"
if [ "$MODE" = "local" ]; then
    export NEXT_PUBLIC_USE_LOCAL="true"
fi

print_success "Environment configured"

# Cleanup function
cleanup() {
    echo ""
    print_header "Shutting down services"

    if [ ! -z "$API_PID" ]; then
        kill $API_PID 2>/dev/null || true
        print_success "API stopped"
    fi

    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        print_success "Frontend stopped"
    fi

    echo ""
    echo "Goodbye!"
}

trap cleanup EXIT INT TERM

# Start API
print_header "Starting API Server"

cd "$BYTEPORT_ROOT/backend/api"
if [ "$MODE" = "development" ]; then
    if command -v air &> /dev/null; then
        print_success "Starting with Air (live reload)"
        air > "$BYTEPORT_ROOT/api.log" 2>&1 &
    else
        print_warning "Air not found, using go run"
        go run . > "$BYTEPORT_ROOT/api.log" 2>&1 &
    fi
else
    go run . > "$BYTEPORT_ROOT/api.log" 2>&1 &
fi

API_PID=$!
print_success "API started (PID: $API_PID, Port: $PORT_API)"

# Wait for API to be ready
echo "Waiting for API to be ready..."
for i in {1..30}; do
    if curl -s "http://localhost:$PORT_API/api/v1/health" > /dev/null 2>&1; then
        print_success "API is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "API failed to start. Check api.log for details"
        exit 1
    fi
    sleep 1
done

# Start Frontend
print_header "Starting Frontend"

cd "$BYTEPORT_ROOT/frontend/web-next"

if [ "$USE_PNPM" = true ]; then
    if [ "$MODE" = "local" ]; then
        pnpm dev:local > "$BYTEPORT_ROOT/frontend.log" 2>&1 &
    elif [ "$MODE" = "development" ]; then
        pnpm dev > "$BYTEPORT_ROOT/frontend.log" 2>&1 &
    else
        # Build and start in production mode
        if [ ! -d ".next" ]; then
            print_success "Building frontend..."
            pnpm build
        fi
        pnpm start > "$BYTEPORT_ROOT/frontend.log" 2>&1 &
    fi
else
    if [ "$MODE" = "production" ] && [ ! -d ".next" ]; then
        print_success "Building frontend..."
        npm run build
    fi
    npm run ${MODE} > "$BYTEPORT_ROOT/frontend.log" 2>&1 &
fi

FRONTEND_PID=$!
print_success "Frontend started (PID: $FRONTEND_PID, Port: $PORT_FRONTEND)"

# Print status
print_header "Services Running"

echo ""
echo "API Server:"
echo "  URL:  http://localhost:$PORT_API"
echo "  Logs: tail -f $BYTEPORT_ROOT/api.log"
echo ""
echo "Frontend:"
echo "  URL:  http://localhost:$PORT_FRONTEND"
echo "  Logs: tail -f $BYTEPORT_ROOT/frontend.log"
echo ""
echo "================================================"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for processes
wait
