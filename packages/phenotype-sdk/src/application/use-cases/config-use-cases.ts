/**
 * Configuration use cases.
 */

import type { ConfigServicePort, MetricsPort } from '../domain/ports/index.js';
import { ConfigEntry } from '../domain/entities/config-entry.js';
import { ConfigDTO, ConfigListDTO } from '../dto/config-dto.js';

/**
 * Use case: Get a configuration value.
 */
export class GetConfigUseCase {
  constructor(
    private readonly configService: ConfigServicePort,
    private readonly metrics: MetricsPort,
  ) {}

  async execute(namespace: string, key: string): Promise<ConfigDTO | null> {
    const start = Date.now();

    try {
      const entry = await this.configService.get(namespace, key);

      if (entry) {
        this.metrics.recordCacheHit();
        this.metrics.recordOperation('get');
        return ConfigDTO.fromEntity(entry);
      } else {
        this.metrics.recordCacheMiss();
        this.metrics.recordOperation('get');
        return null;
      }
    } finally {
      this.metrics.recordLatency('get', Date.now() - start);
    }
  }
}

/**
 * Use case: Set a configuration value.
 */
export class SetConfigUseCase {
  constructor(
    private readonly configService: ConfigServicePort,
    private readonly metrics: MetricsPort,
  ) {}

  async execute(params: {
    namespace: string;
    key: string;
    value: string;
    valueType?: string;
    updatedBy: string;
    description?: string;
  }): Promise<ConfigDTO> {
    const start = Date.now();

    try {
      // Create entry
      const entry = ConfigEntry.create({
        namespace: params.namespace,
        key: params.key,
        value: params.value,
        valueType: params.valueType as 'string' | 'number' | 'boolean' | 'json' | 'base64' | undefined,
        updatedBy: params.updatedBy,
        description: params.description,
      });

      // Validate
      const validation = entry.validate();
      if (!validation.valid) {
        throw new ValidationError(validation.errors);
      }

      // Save
      await this.configService.set(entry);
      this.metrics.recordOperation('set');

      return ConfigDTO.fromEntity(entry);
    } finally {
      this.metrics.recordLatency('set', Date.now() - start);
    }
  }
}

/**
 * Use case: Delete a configuration value.
 */
export class DeleteConfigUseCase {
  constructor(
    private readonly configService: ConfigServicePort,
    private readonly metrics: MetricsPort,
  ) {}

  async execute(namespace: string, key: string): Promise<void> {
    const start = Date.now();

    try {
      await this.configService.delete(namespace, key);
      this.metrics.recordOperation('delete');
    } finally {
      this.metrics.recordLatency('delete', Date.now() - start);
    }
  }
}

/**
 * Use case: List configuration values in a namespace.
 */
export class ListConfigUseCase {
  constructor(
    private readonly configService: ConfigServicePort,
    private readonly metrics: MetricsPort,
  ) {}

  async execute(namespace: string): Promise<ConfigListDTO> {
    const start = Date.now();

    try {
      const entries = await this.configService.list(namespace);
      this.metrics.recordOperation('list');

      return ConfigListDTO.fromEntities(entries);
    } finally {
      this.metrics.recordLatency('list', Date.now() - start);
    }
  }
}

class ValidationError extends Error {
  constructor(public readonly errors: string[]) {
    super(`Validation failed: ${errors.join(', ')}`);
    this.name = 'ValidationError';
  }
}
