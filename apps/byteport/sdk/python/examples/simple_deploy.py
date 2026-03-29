"""Simple deployment example"""

import os
from byteport import BytePortClient

def main():
    # Get API key from environment
    api_key = os.getenv("BYTEPORT_API_KEY")
    if not api_key:
        print("Error: BYTEPORT_API_KEY environment variable not set")
        return

    # Create client
    client = BytePortClient(api_key=api_key)

    # Deploy Next.js app
    deployment = client.deploy({
        "name": "my-nextjs-app",
        "type": "frontend",
        "git_url": "https://github.com/user/nextjs-app",
        "env_vars": {
            "API_URL": "https://api.example.com"
        }
    })

    print(f"✅ Deployment created successfully!")
    print(f"   ID: {deployment.id}")
    print(f"   Name: {deployment.name}")
    print(f"   Status: {deployment.status}")
    print(f"   URL: {deployment.url}")
    print(f"   Provider: {deployment.provider}")

    # Close client
    client.close()

if __name__ == "__main__":
    main()
