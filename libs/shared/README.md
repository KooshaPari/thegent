# Phenotype Shared Libraries

This directory contains shared libraries extracted from across the ecosystem.

## Structure

```
shared/
├── hexagonal/   # Shared hexagonal architecture primitives
├── logging/    # Shared logging configuration
├── metrics/    # Shared metrics collection
├── config/     # Shared configuration management
├── events/     # Shared event handling
├── cli/        # Shared CLI utilities
└── telemetry/  # Shared telemetry/tracing
```

## Versioning

All shared libraries follow **SemVer** with automated releases via CI.

## Usage

Each library is independently versioned and can be imported standalone.
