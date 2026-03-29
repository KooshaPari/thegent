# BytePort Python SDK

Official Python SDK for BytePort - Deploy anything, anywhere with zero cost.

## Installation

```bash
pip install byteport
```

## Quick Start

```python
from byteport import BytePortClient

# Create client
client = BytePortClient(api_key="bp_sk_your_api_key")

# Deploy Next.js app
deployment = client.deploy({
    "name": "my-nextjs-app",
    "type": "frontend",
    "git_url": "https://github.com/user/nextjs-app",
    "env_vars": {
        "API_URL": "https://api.example.com"
    }
})

print(f"✅ Deployed to: {deployment.url}")
print(f"💰 Monthly cost: ${deployment.cost.monthly}")
```

## Features

- ✅ Full API coverage with type safety
- ✅ Synchronous and asynchronous clients
- ✅ Pydantic models for validation
- ✅ Streaming logs support
- ✅ Comprehensive error handling
- ✅ Self-hosted deployment support

## Async Usage

```python
import asyncio
from byteport import AsyncBytePortClient

async def main():
    client = AsyncBytePortClient(api_key="bp_sk_...")

    deployment = await client.deploy({
        "name": "my-app",
        "type": "frontend"
    })

    # Stream logs
    async for log in client.stream_logs(deployment.id):
        print(f"[{log.timestamp}] {log.message}")

asyncio.run(main())
```

## Documentation

See [examples/](examples/) for more usage examples.

## License

MIT
