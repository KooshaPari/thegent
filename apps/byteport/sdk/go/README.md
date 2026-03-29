# BytePort Go SDK

Official Go SDK for BytePort - Deploy anything, anywhere with zero cost.

## Installation

```bash
go get github.com/byteport/sdk-go
```

## Quick Start

```go
package main

import (
    "context"
    "fmt"
    "log"

    "github.com/byteport/sdk-go/byteport"
)

func main() {
    // Create client
    client := byteport.NewClient("bp_sk_your_api_key")

    // Deploy Next.js app
    deployment, err := client.Deploy(context.Background(), &byteport.DeployRequest{
        Name:   "my-nextjs-app",
        Type:   "frontend",
        GitURL: "https://github.com/user/nextjs-app",
        EnvVars: map[string]string{
            "API_URL": "https://api.example.com",
        },
    })

    if err != nil {
        log.Fatal(err)
    }

    fmt.Printf("✅ Deployed to: %s\n", deployment.URL)
    fmt.Printf("💰 Monthly cost: $%.2f\n", deployment.Cost.Monthly)
}
```

## Features

- ✅ Full API coverage
- ✅ Type-safe request/response models
- ✅ Context support for cancellation
- ✅ Streaming logs support
- ✅ Comprehensive error handling
- ✅ Self-hosted deployment support

## Documentation

See [examples/](examples/) for more usage examples.

## License

MIT
