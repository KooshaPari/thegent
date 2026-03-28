/**
 * Domain layer - Pure business logic with no external dependencies.
 *
 * This layer contains:
 * - Entities: Core business objects
 * - Value Objects: Immutable types
 * - Ports: Interface definitions
 */

// Re-exports
export { ConfigEntry, ConfigNamespace } from './entities/config-entry.js';
export { FeatureFlag, FlagState } from './entities/feature-flag.js';
export { ValueType } from './value-objects/value-type.js';
export { ConfigServicePort, MetricsPort } from './ports/index.js';
