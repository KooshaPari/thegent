/**
 * Core SDK for Phenotype ecosystem.
 *
 * This package provides the foundation for all Phenotype TypeScript/Node packages,
 * following Hexagonal Architecture principles.
 *
 * @module @phenotype/sdk
 */

// Domain layer - pure business logic
export * from './domain/index.js';

// Application layer - use cases
export * from './application/index.js';

// Error types
export * from './errors/index.js';
