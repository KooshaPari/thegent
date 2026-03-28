/**
 * HTTP Adapter - Infrastructure layer
 *
 * Implements the HTTP port for communicating with the Phenotype API.
 * Following Hexagonal Architecture:
 * - This is an adapter that implements ports defined in domain/application
 */

import { AppError, ok, err, Result } from '../domain/errors';
import type { PhenotypeConfig } from '../domain/config';

/**
 * HTTP Response type.
 */
export interface HttpResponse<T> {
  success: true;
  data: T;
  status: number;
}

export interface HttpErrorResponse {
  success: false;
  error: AppError;
  status: number;
}

/**
 * HTTP Port interface.
 */
export interface HttpAdapter {
  get<T>(path: string, params?: Record<string, string>): Promise<Result<T, AppError>>;
  post<T>(path: string, body: unknown): Promise<Result<T, AppError>>;
  put<T>(path: string, body: unknown): Promise<Result<T, AppError>>;
  delete<T>(path: string): Promise<Result<T, AppError>>;
  close(): Promise<void>;
}

/**
 * HTTP Adapter implementation using fetch.
 */
export class HttpAdapterImpl implements HttpAdapter {
  private readonly config: PhenotypeConfig;

  constructor(config: PhenotypeConfig) {
    this.config = config;
  }

  private getHeaders(): Record<string, string> {
    return {
      'Content-Type': 'application/json',
      'X-API-Key': this.config.apiKey,
      ...this.config.headers,
    };
  }

  private async request<T>(
    method: string,
    path: string,
    options: {
      body?: unknown;
      params?: Record<string, string>;
    } = {}
  ): Promise<Result<T, AppError>> {
    const { body, params } = options;

    // Build URL with query params
    let url = `${this.config.baseUrl}${path}`;
    if (params) {
      const searchParams = new URLSearchParams(params);
      url += `?${searchParams.toString()}`;
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);

    try {
      const response = await fetch(url, {
        method,
        headers: this.getHeaders(),
        body: body ? JSON.stringify(body) : undefined,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        try {
          const errorData = await response.json();
          if (errorData.message) {
            errorMessage = errorData.message;
          }
        } catch {
          // Response body is not JSON
        }

        return err(
          new AppError({
            code: 'HTTP_ERROR' as any,
            message: errorMessage,
            context: { status: response.status, path },
          })
        );
      }

      const data = await response.json();
      return ok(data as T);
    } catch (error) {
      clearTimeout(timeoutId);

      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          return err(
            new AppError({
              code: 'TIMEOUT' as any,
              message: `Request timeout after ${this.config.timeout}ms`,
              context: { path, timeout: this.config.timeout },
            })
          );
        }

        return err(
          new AppError({
            code: 'NETWORK_ERROR' as any,
            message: error.message,
            cause: error,
          })
        );
      }

      return err(
        new AppError({
          code: 'UNKNOWN' as any,
          message: 'Unknown error occurred',
        })
      );
    }
  }

  async get<T>(path: string, params?: Record<string, string>): Promise<Result<T, AppError>> {
    return this.request<T>('GET', path, { params });
  }

  async post<T>(path: string, body: unknown): Promise<Result<T, AppError>> {
    return this.request<T>('POST', path, { body });
  }

  async put<T>(path: string, body: unknown): Promise<Result<T, AppError>> {
    return this.request<T>('PUT', path, { body });
  }

  async delete<T>(path: string): Promise<Result<T, AppError>> {
    return this.request<T>('DELETE', path);
  }

  async close(): Promise<void> {
    // No-op for fetch adapter, but allows swapping implementations
  }
}
