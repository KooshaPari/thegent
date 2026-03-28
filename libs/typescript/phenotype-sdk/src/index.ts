/**
 * Phenotype TypeScript SDK
 *
 * A comprehensive SDK following:
 * - Hexagonal Architecture (Ports & Adapters)
 * - Clean Architecture principles
 * - SOLID principles
 * - xDD methodologies (TDD, BDD, DDD)
 *
 * @example
 * ```typescript
 * import { createClient, PhenotypeConfig } from '@phenotype/sdk';
 *
 * const config: PhenotypeConfig = {
 *   apiKey: process.env.PHENOTYPE_API_KEY,
 *   baseUrl: 'https://api.phenotype.io',
 * };
 *
 * const client = createClient(config);
 *
 * const result = await client.query('SELECT * FROM users');
 * console.log(result.data);
 * ```
 */

// Domain Layer - Pure domain types
export * from './domain/errors';
export * from './domain/config';

// Application Layer - Use cases
export * from './application/client';

// Adapters Layer - Infrastructure
export * from './adapters/http-adapter';

// Main entry point
export { createClient } from './application/client';
export type { PhenotypeClient, PhenotypeConfig } from './application/client';
