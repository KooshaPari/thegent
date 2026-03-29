/**
 * Stream logs example
 */

import { BytePortClient } from '../src'

async function main() {
  const apiKey = process.env.BYTEPORT_API_KEY
  if (!apiKey) {
    console.error('Error: BYTEPORT_API_KEY environment variable not set')
    process.exit(1)
  }

  const deploymentId = process.argv[2]
  if (!deploymentId) {
    console.error('Usage: node stream-logs.js <deployment_id>')
    process.exit(1)
  }

  const client = new BytePortClient({ apiKey })

  console.log(`📜 Streaming logs for deployment: ${deploymentId}`)
  console.log('Press Ctrl+C to stop\n')

  try {
    for await (const log of client.streamLogs(deploymentId)) {
      const timestamp = new Date(log.timestamp).toLocaleTimeString()
      console.log(`[${timestamp}] [${log.level}] ${log.message}`)
    }
  } catch (error) {
    console.error('Error streaming logs:', error)
    process.exit(1)
  }
}

main()
