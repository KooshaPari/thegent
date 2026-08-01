# Hello World Story

<StoryHeader
    title="Your First thegent-sharecli Operation"
    :duration="2"
    :gif="'/gifs/thegent-sharecli-hello-world.gif'"
    difficulty="beginner"
/>

## Objective

Get thegent-sharecli running with a basic operation.

## Prerequisites

- Rust/Node/Python installed
- thegent-sharecli package installed

## Implementation

```rust
use thegent-sharecli::Client;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize client
    let client = Client::new().await?;
    
    // Execute operation
    let result = client.hello().await?;
    
    println!("Success: {}", result);
    Ok(())
}
```

## Expected Output

```
Success: Hello from thegent-sharecli!
```

## Next Steps

- [Core Integration](./core-integration)
- Read [API Reference](../reference/api)
