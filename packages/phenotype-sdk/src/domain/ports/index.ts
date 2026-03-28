/**
 * Port interfaces - contracts that adapters must implement.
 *
 * Ports define the boundaries of the domain without depending on
 * external systems.
 */

import type { ConfigEntry, ValidationResult } from '../entities/config-entry.js';

/**
 * Port for configuration service operations.
 */
export interface ConfigServicePort {
  /**
   * Get a configuration entry by namespace and key.
   */
  get(namespace: string, key: string): Promise<ConfigEntry | null>;

  /**
   * Set a configuration entry.
   */
  set(entry: ConfigEntry): Promise<void>;

  /**
   * Delete a configuration entry.
   */
  delete(namespace: string, key: string): Promise<void>;

  /**
   * List all entries in a namespace.
   */
  list(namespace: string): Promise<ConfigEntry[]>;

  /**
   * Validate an entry without saving.
   */
  validate(entry: ConfigEntry): Promise<ValidationResult>;
}

/**
 * Port for metrics collection.
 */
export interface MetricsPort {
  /**
   * Record a cache hit.
   */
  recordCacheHit(): void;

  /**
   * Record a cache miss.
   */
  recordCacheMiss(): void;

  /**
   * Record a config operation.
   */
  recordOperation(operation: 'get' | 'set' | 'delete' | 'list'): void;

  /**
   * Record operation latency.
   */
  recordLatency(operation: string, durationMs: number): void;
}

/**
 * No-op metrics implementation for when metrics aren't needed.
 */
export class NoOpMetrics implements MetricsPort {
  recordCacheHit(): void {
    // No-op
  }

  recordCacheMiss(): void {
    // No-op
  }

  recordOperation(_operation: 'get' | 'set' | 'delete' | 'list'): void {
    // No-op
  }

  recordLatency(_operation: string, _durationMs: number): void {
    // No-op
  }
}
