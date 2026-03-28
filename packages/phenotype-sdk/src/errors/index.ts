/**
 * Unified error types for Phenotype SDK.
 */

/**
 * Base error class for Phenotype errors.
 */
export class PhenotypeError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly details?: Record<string, unknown>,
  ) {
    super(message);
    this.name = 'PhenotypeError';
  }
}

/**
 * Validation error.
 */
export class ValidationError extends PhenotypeError {
  constructor(
    message: string,
    public readonly errors: string[],
  ) {
    super(message, 'VALIDATION_ERROR', { errors });
    this.name = 'ValidationError';
  }
}

/**
 * Not found error.
 */
export class NotFoundError extends PhenotypeError {
  constructor(
    resource: string,
    id: string,
  ) {
    super(`${resource} not found: ${id}`, 'NOT_FOUND', { resource, id });
    this.name = 'NotFoundError';
  }
}

/**
 * Conflict error.
 */
export class ConflictError extends PhenotypeError {
  constructor(message: string) {
    super(message, 'CONFLICT');
    this.name = 'ConflictError';
  }
}

/**
 * Network/connection error.
 */
export class ConnectionError extends PhenotypeError {
  constructor(message: string, public readonly originalError?: Error) {
    super(message, 'CONNECTION_ERROR', { originalError: originalError?.message });
    this.name = 'ConnectionError';
  }
}

/**
 * Authentication error.
 */
export class AuthenticationError extends PhenotypeError {
  constructor(message: string) {
    super(message, 'AUTHENTICATION_ERROR');
    this.name = 'AuthenticationError';
  }
}
