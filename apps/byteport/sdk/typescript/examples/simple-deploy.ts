/**
 * Simple deployment example
 */

import { BytePortClient } from '../src'

async function main() {
  const apiKey = process.env.BYTEPORT_API_KEY
  if (!apiKey) {
    console.error('Error: BYTEPORT_API_KEY environment variable not set')
    process.exit(1)
  }

  const client = new BytePortClient({ apiKey })

  // Deploy Next.js app
  const deployment = await client.deploy({
    name: 'my-nextjs-app',
    type: 'frontend',
    gitUrl: 'https://github.com/user/nextjs-app',
    envVars: {
      API_URL: 'https://api.example.com',
    },
  })

  console.log('✅ Deployment created successfully!')
  console.log(`   ID: ${deployment.id}`)
  console.log(`   Name: ${deployment.name}`)
  console.log(`   Status: ${deployment.status}`)
  console.log(`   URL: ${deployment.url}`)
  console.log(`   Provider: ${deployment.provider}`)
}

main().catch(console.error)
