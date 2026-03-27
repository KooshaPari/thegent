# Clikit

A neutral Go CLI framework for building CLI applications.

## Purpose

This package is the extracted CLI core library from Phenotype. It provides a modular command architecture, dependency injection container, configuration handling, and command runner patterns.

## Architecture

- `cli` package for application wiring
- `commands` package for command definitions
- `di` package for dependency injection
- `config` for configuration resolution
- `output` for pretty output/table/progress

## Build

```bash
go test ./...
```

## Coding standards

- Follow Go idioms and effective Go
- Keep packages small and cohesive
- Use explicit interfaces for injectability

## Promotion

This library is intended as the neutral reusable core for CLI tools.
