# Phenotype SDK for Zig

Hexagonal architecture SDK for the Phenotype configuration platform.

## Structure

```
src/
├── domain/           # Core business logic (no external dependencies)
│   ├── entities.zig  # ConfigEntry, FeatureFlag
│   ├── value_objects.zig
│   └── ports.zig     # Repository interfaces
├── application/      # Use cases
│   ├── use_cases.zig
│   └── dto.zig
└── adapters/         # Infrastructure
    └── outbound/     # HTTP, Memory adapters
```

## Building

```bash
zig build
zig build test
```

## Usage

```zig
const phenotype = @import("phenotype-sdk");

// Create configuration
var use_cases = phenotype.application.ConfigUseCases{
    .repository = my_repo,
    .publisher = phenotype.domain.EventPublisher.noOp(),
    .allocator = allocator,
};

const entry = try use_cases.create(.{
    .key = "database.host",
    .value = "localhost",
    .value_type = .string,
});
```
