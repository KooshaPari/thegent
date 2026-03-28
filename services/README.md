# Services

Microservices and backend services for the Phenotype ecosystem.

## Overview

This directory contains standalone microservice implementations that can be deployed independently.

## Directory Structure

```
services/
└── [service-name]/
    ├── src/            # Service source code
    ├── Dockerfile      # Container definition
    ├── docker-compose.yml
    └── README.md
```

## Services

| Service | Description | Status |
|---------|-------------|--------|
| (placeholder) | TBD | - |

## Adding a New Service

1. Create directory: `services/<service-name>/`
2. Add source code in `src/`
3. Add `Dockerfile` for containerization
4. Add `docker-compose.yml` for local development
5. Add `README.md` with service documentation

## Service Template

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

CMD ["python", "-m", "service"]
```

## Development

```bash
# Local development
docker-compose up

# Run tests
docker-compose run --rm service pytest

# Build image
docker build -t phenotype/service-name:latest .
```

## References

- [ADR-0005: Top-Level Directory Structure](../governance/adrs/0005-top-level-directory-structure.md)
- [ADR-0003: Hexagonal Architecture Standard](../governance/adrs/0003-hexagonal-architecture-standard.md)
