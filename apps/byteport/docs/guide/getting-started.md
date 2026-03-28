# Getting Started

## Prerequisites

- Go 1.23+
- Node.js 22+ and pnpm
- PostgreSQL 16+
- A WorkOS account (free tier sufficient)

## Quick Start

```bash
# Clone the repository
git clone https://github.com/KooshaPari/byteport.git
cd byteport

# Start dev stack
python byteport.py --dev

# Access dashboard
open http://localhost:8001
```

## Environment Setup

Copy the example env file and fill in values:

```bash
cp backend/.env.example backend/.env
```

Required variables:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `WORKOS_API_KEY` | WorkOS API key |
| `WORKOS_CLIENT_ID` | WorkOS client ID |
| `ENCRYPTION_KEY` | 32-byte AES key for credential encryption |
| `PORT` | Backend port (default: 8080) |

## First Deployment

1. Sign in at `http://localhost:8001`
2. Go to **Settings > Credentials** and add your Vercel token
3. Go to **Projects** and create a new project with a Git URL
4. Click **Deploy** and select Vercel as your provider
5. Watch the live build logs and get your deployment URL

## Architecture Overview

See the [Architecture guide](./architecture.md) for a full system diagram.
