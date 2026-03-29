# nexus

Service registry and discovery for microservices.

## Features

- **Registry**: Register/deregister services
- **Discovery**: Find services by name/tags
- **Health Checks**: Automatic health monitoring
- **Load Balancing**: Round-robin, random, consistent hash

## Installation

```toml
[dependencies]
nexus = { git = "https://github.com/KooshaPari/nexus" }
```

## Usage

```rust
use nexus::{Registry, Service};

let registry = Registry::new();
registry.register(Service::new("user-svc", "localhost:8080")).await?;

let services = registry.discover("user-svc").await?;
let endpoint = services.next()?; // Load balanced
```

## License

MIT
