/**
 * Phenotype Client - Application layer
 *
 * Main client for interacting with the Phenotype API.
 * Following Hexagonal Architecture:
 * - Uses ports (interfaces) for infrastructure
 * - No direct dependency on HTTP implementation
 */

import { AppError, EntityNotFoundError, ok, err, Result } from '../domain/errors';
import type { PhenotypeConfig } from '../domain/config';
import { validateConfig } from '../domain/config';
import { HttpAdapter, HttpAdapterImpl } from '../adapters/http-adapter';

/**
 * Phenotype Client interface (Port).
 */
export interface PhenotypeClient {
  /** Execute a query */
  query<T>(sql: string, params?: unknown[]): Promise<Result<T[], AppError>>;
  /** Execute a mutation */
  mutate<T>(sql: string, params?: unknown[]): Promise<Result<T, AppError>>;
  /** Get service health */
  health(): Promise<Result<{ status: string }, AppError>>;
  /** Close the client */
  close(): Promise<void>;
}

/**
 * Phenotype Client implementation.
 */
export class PhenotypeClientImpl implements PhenotypeClient {
  private readonly config: PhenotypeConfig;
  private readonly http: HttpAdapter;

  constructor(config: PhenotypeConfig, http?: HttpAdapter) {
    this.config = validateConfig(config);
    this.http = http ?? new HttpAdapterImpl(this.config);
  }

  /**
   * Execute a query against the Phenotype API.
   */
  async query<T>(sql: string, params?: unknown[]): Promise<Result<T[], AppError>> {
    try {
      const response = await this.http.post<{ data: T[] }>('/query', {
        sql,
        params,
      });

      if (response.success) {
        return ok(response.data.data);
      }

      return err(response.error);
    } catch (error) {
      return err(
        new AppError({
          code: 'NETWORK_ERROR' as any,
          message: `Query failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
          cause: error instanceof Error ? error : undefined,
        })
      );
    }
  }

  /**
   * Execute a mutation against the Phenotype API.
   */
  async mutate<T>(sql: string, params?: unknown[]): Promise<Result<T, AppError>> {
    try {
      const response = await this.http.post<{ data: T }>('/mutate', {
        sql,
        params,
      });

      if (response.success) {
        return ok(response.data.data);
      }

      return err(response.error);
    } catch (error) {
      return err(
        new AppError({
          code: 'NETWORK_ERROR' as any,
          message: `Mutation failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
          cause: error instanceof Error ? error : undefined,
        })
      );
    }
  }

  /**
   * Check service health.
   */
  async health(): Promise<Result<{ status: string }, AppError>> {
    try {
      const response = await this.http.get<{ status: string }>('/health');

      if (response.success) {
        return ok(response.data);
      }

      return err(response.error);
    } catch (error) {
      return err(
        new AppError({
          message: `Health check failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
          cause: error instanceof Error ? error : undefined,
        })
      );
    }
  }

  /**
   * Close the client and release resources.
   */
  async close(): Promise<void> {
    await this.http.close();
  }
}

/**
 * Factory function to create a Phenotype client.
 *
 * @example
 * ```typescript
 * import { createClient } from '@phenotype/sdk';
 *
 * const client = createClient({
 *   apiKey: process.env.PHENOTYPE_API_KEY!,
 *   baseUrl: 'https://api.phenotype.io',
 * });
 *
 * const result = await client.query('SELECT * FROM users');
 * if (result.success) {
 *   console.log(result.data);
 * }
 *
 * await client.close();
 * ```
 */
export function createClient(config: PhenotypeConfig): PhenotypeClient {
  return new PhenotypeClientImpl(config);
}
