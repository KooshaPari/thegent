"""Async deployment example"""

import os
import asyncio
from byteport import AsyncBytePortClient

async def main():
    api_key = os.getenv("BYTEPORT_API_KEY")
    if not api_key:
        print("Error: BYTEPORT_API_KEY environment variable not set")
        return

    async with AsyncBytePortClient(api_key=api_key) as client:
        # Deploy app
        deployment = await client.deploy({
            "name": "my-async-app",
            "type": "frontend",
            "git_url": "https://github.com/user/nextjs-app"
        })

        print(f"✅ Deployed: {deployment.url}")

        # Stream logs
        print("\n📜 Streaming logs:")
        async for log in client.stream_logs(deployment.id):
            print(f"[{log.timestamp}] [{log.level}] {log.message}")

if __name__ == "__main__":
    asyncio.run(main())
