# BytePort TypeScript/JavaScript SDK

Official TypeScript/JavaScript SDK for BytePort - Deploy anything, anywhere with zero cost.

## Installation

```bash
npm install @byteport/sdk
# or
yarn add @byteport/sdk
# or
pnpm add @byteport/sdk
```

## Quick Start

```typescript
import { BytePortClient } from '@byteport/sdk'

const client = new BytePortClient({
  apiKey: process.env.BYTEPORT_API_KEY!
})

// Deploy Next.js app
const deployment = await client.deploy({
  name: 'my-nextjs-app',
  type: 'frontend',
  gitUrl: 'https://github.com/user/nextjs-app',
  envVars: {
    API_URL: 'https://api.example.com'
  }
})

console.log(`✅ Deployed to: ${deployment.url}`)
console.log(`💰 Monthly cost: $${deployment.cost.monthly}`)
```

## Features

- ✅ Full TypeScript support with type safety
- ✅ Streaming logs support
- ✅ Comprehensive error handling
- ✅ Self-hosted deployment support
- ✅ Works in Node.js and modern browsers

## Streaming Logs

```typescript
// Stream logs in real-time
for await (const log of client.streamLogs(deployment.id)) {
  console.log(`[${log.timestamp}] ${log.message}`)
}
```

## Documentation

See [examples/](examples/) for more usage examples.

## License

MIT
