/**
 * Data Transfer Objects for configuration.
 */

import { ConfigEntry } from '../domain/entities/config-entry.js';

/**
 * DTO for a single configuration entry.
 */
export interface ConfigDTO {
  id: string;
  namespace: string;
  key: string;
  value: string;
  valueType: string;
  createdAt: string;
  updatedAt: string;
  updatedBy: string;
  description?: string;
}

export namespace ConfigDTO {
  export function fromEntity(entry: ConfigEntry): ConfigDTO {
    return {
      id: entry.id,
      namespace: entry.namespace,
      key: entry.key,
      value: entry.value,
      valueType: entry.valueType,
      createdAt: entry.createdAt.toISOString(),
      updatedAt: entry.updatedAt.toISOString(),
      updatedBy: entry.updatedBy,
      description: entry.description,
    };
  }

  export function toEntity(dto: ConfigDTO): ConfigEntry {
    return ConfigEntry.create({
      namespace: dto.namespace,
      key: dto.key,
      value: dto.value,
      valueType: dto.valueType as 'string' | 'number' | 'boolean' | 'json' | 'base64' | undefined,
      updatedBy: dto.updatedBy,
      description: dto.description,
    });
  }
}

/**
 * DTO for a list of configuration entries.
 */
export interface ConfigListDTO {
  namespace: string;
  entries: ConfigDTO[];
  count: number;
}

export namespace ConfigListDTO {
  export function fromEntities(entries: ConfigEntry[]): ConfigListDTO {
    return {
      namespace: entries[0]?.namespace ?? '',
      entries: entries.map(ConfigDTO.fromEntity),
      count: entries.length,
    };
  }
}
