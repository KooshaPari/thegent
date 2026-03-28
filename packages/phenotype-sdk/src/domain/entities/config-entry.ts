/**
 * Configuration entry entity.
 *
 * Represents a key-value configuration pair with metadata.
 */

import { ValueType } from '../value-objects/value-type.js';

/**
 * Configuration entry representing a single config value.
 */
export class ConfigEntry {
  public readonly id: string;
  public readonly namespace: string;
  public readonly key: string;
  public value: string;
  public readonly valueType: ValueType;
  public readonly createdAt: Date;
  public updatedAt: Date;
  public updatedBy: string;
  public description?: string;

  private constructor(params: {
    id: string;
    namespace: string;
    key: string;
    value: string;
    valueType: ValueType;
    createdAt: Date;
    updatedAt: Date;
    updatedBy: string;
    description?: string;
  }) {
    this.id = params.id;
    this.namespace = params.namespace;
    this.key = params.key;
    this.value = params.value;
    this.valueType = params.valueType;
    this.createdAt = params.createdAt;
    this.updatedAt = params.updatedAt;
    this.updatedBy = params.updatedBy;
    this.description = params.description;
  }

  /**
   * Create a new config entry.
   */
  static create(params: {
    namespace: string;
    key: string;
    value: string;
    valueType?: ValueType;
    updatedBy: string;
    description?: string;
  }): ConfigEntry {
    const now = new Date();
    return new ConfigEntry({
      id: generateId(),
      namespace: params.namespace,
      key: params.key,
      value: params.value,
      valueType: params.valueType ?? 'string',
      createdAt: now,
      updatedAt: now,
      updatedBy: params.updatedBy,
      description: params.description,
    });
  }

  /**
   * Update the config value.
   */
  update(value: string, updatedBy: string): void {
    this.value = value;
    this.updatedAt = new Date();
    this.updatedBy = updatedBy;
  }

  /**
   * Validate the config entry.
   */
  validate(): ValidationResult {
    const errors: string[] = [];

    if (!this.key || this.key.trim() === '') {
      errors.push('key is required');
    }

    if (this.key && !/^[a-zA-Z][a-zA-Z0-9_.-]*$/.test(this.key)) {
      errors.push('key must start with a letter and contain only alphanumeric, underscore, dot, or hyphen');
    }

    if (!this.valueType || !['string', 'number', 'boolean', 'json', 'base64'].includes(this.valueType)) {
      errors.push('invalid value type');
    }

    if (this.valueType === 'number' && isNaN(Number(this.value))) {
      errors.push('value must be a valid number');
    }

    if (this.valueType === 'boolean' && !['true', 'false', '0', '1'].includes(this.value.toLowerCase())) {
      errors.push('value must be a boolean (true/false/0/1)');
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }

  /**
   * Convert to plain object for serialization.
   */
  toJSON(): ConfigEntryJSON {
    return {
      id: this.id,
      namespace: this.namespace,
      key: this.key,
      value: this.value,
      value_type: this.valueType,
      created_at: this.createdAt.toISOString(),
      updated_at: this.updatedAt.toISOString(),
      updated_by: this.updatedBy,
      description: this.description,
    };
  }
}

export interface ConfigEntryJSON {
  id: string;
  namespace: string;
  key: string;
  value: string;
  value_type: string;
  created_at: string;
  updated_at: string;
  updated_by: string;
  description?: string;
}

export interface ValidationResult {
  valid: boolean;
  errors: string[];
}

/**
 * Configuration namespace grouping.
 */
export class ConfigNamespace {
  public readonly name: string;
  private entries: Map<string, ConfigEntry> = new Map();

  constructor(name: string) {
    this.name = name;
  }

  addEntry(entry: ConfigEntry): void {
    if (entry.namespace !== this.name) {
      throw new Error(`Entry namespace "${entry.namespace}" does not match namespace "${this.name}"`);
    }
    this.entries.set(entry.key, entry);
  }

  getEntry(key: string): ConfigEntry | undefined {
    return this.entries.get(key);
  }

  removeEntry(key: string): boolean {
    return this.entries.delete(key);
  }

  listEntries(): ConfigEntry[] {
    return Array.from(this.entries.values());
  }

  get size(): number {
    return this.entries.size;
  }
}

/**
 * Generate a unique ID for config entries.
 */
function generateId(): string {
  const timestamp = Date.now();
  const random = Math.random().toString(36).substring(2, 10);
  return `cfg_${timestamp}_${random}`;
}
