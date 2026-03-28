/**
 * Configuration Types - Domain configuration without external dependencies.
 *
 * Following Hexagonal Architecture:
 * - domain/ contains pure types with no framework dependencies
 */

import { z } from 'zod';

/**
 * Configuration schema validated with Zod.
 */
export const PhenotypeConfigSchema = z.object({
  /** API key for authentication */
  apiKey: z.string().min(1, 'API key is required'),
  /** Base URL for the API */
  baseUrl: z.string().url('Invalid base URL').default('https://api.phenotype.io'),
  /** Request timeout in milliseconds */
  timeout: z.number().positive().default(30000),
  /** Number of retries for failed requests */
  retries: z.number().int().min(0).max(5).default(3),
  /** Enable debug mode */
  debug: z.boolean().default(false),
  /** Custom headers to include with every request */
  headers: z.record(z.string()).optional(),
  /** Log level */
  logLevel: z.enum(['debug', 'info', 'warn', 'error']).default('info'),
});

/**
 * Phenotype SDK configuration type.
 */
export type PhenotypeConfig = z.infer<typeof PhenotypeConfigSchema>;

/**
 * Default configuration values.
 */
export const DEFAULT_CONFIG: PhenotypeConfig = {
  apiKey: '',
  baseUrl: 'https://api.phenotype.io',
  timeout: 30000,
  retries: 3,
  debug: false,
  logLevel: 'info',
};

/**
 * Validate configuration.
 *
 * @param config - Configuration to validate
 * @returns Validated configuration
 * @throws ValidationError if validation fails
 */
export function validateConfig(config: unknown): PhenotypeConfig {
  return PhenotypeConfigSchema.parse(config);
}
