/**
 * Domain Errors - Pure domain error types with no external dependencies.
 *
 * Following ADR-001 dependency rule:
 * - domain/ contains ZERO external dependencies
 * - Only standard library types allowed
 */

import { z } from 'zod';

/**
 * Error codes following RFC 5424 syslog conventions.
 */
export enum ErrorCode {
  UNKNOWN = 'UNKNOWN',
  NOT_IMPLEMENTED = 'NOT_IMPLEMENTED',
  INVALID_STATE = 'INVALID_STATE',
  TIMEOUT = 'TIMEOUT',
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  ENTITY_NOT_FOUND = 'ENTITY_NOT_FOUND',
  DUPLICATE_ENTITY = 'DUPLICATE_ENTITY',
  BUSINESS_RULE_VIOLATION = 'BUSINESS_RULE_VIOLATION',
  DATABASE_ERROR = 'DATABASE_ERROR',
  NETWORK_ERROR = 'NETWORK_ERROR',
  AUTHENTICATION_ERROR = 'AUTHENTICATION_ERROR',
  AUTHORIZATION_ERROR = 'AUTHORIZATION_ERROR',
}

/**
 * Error severity levels for monitoring and alerting.
 */
export enum ErrorSeverity {
  DEBUG = 'DEBUG',
  INFO = 'INFO',
  WARNING = 'WARNING',
  ERROR = 'ERROR',
  CRITICAL = 'CRITICAL',
}

/**
 * Base error class for all Phenotype errors.
 *
 * @example
 * ```typescript
 * throw new AppError({
 *   code: ErrorCode.ENTITY_NOT_FOUND,
 *   message: 'User not found',
 *   context: { userId: '123' },
 * });
 * ```
 */
export class AppError extends Error {
  public readonly code: ErrorCode;
  public readonly severity: ErrorSeverity;
  public readonly context: Record<string, unknown>;
  public readonly timestamp: Date;

  constructor(params: {
    code?: ErrorCode;
    message: string;
    context?: Record<string, unknown>;
    severity?: ErrorSeverity;
    cause?: Error;
  }) {
    super(params.message);
    this.name = 'AppError';
    this.code = params.code ?? ErrorCode.UNKNOWN;
    this.severity = params.severity ?? ErrorSeverity.ERROR;
    this.context = params.context ?? {};
    this.timestamp = new Date();
    this.cause = params.cause;

    // Maintains proper stack trace
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, AppError);
    }
  }

  /**
   * Add context to the error.
   */
  withContext(context: Record<string, unknown>): AppError {
    return new AppError({
      code: this.code,
      message: this.message,
      context: { ...this.context, ...context },
      severity: this.severity,
      cause: this.cause,
    });
  }

  /**
   * Convert error to JSON for serialization.
   */
  toJSON(): Record<string, unknown> {
    return {
      name: this.name,
      code: this.code,
      message: this.message,
      context: this.context,
      severity: this.severity,
      timestamp: this.timestamp.toISOString(),
      stack: this.stack,
    };
  }
}

/**
 * Domain-specific errors.
 */
export class EntityNotFoundError extends AppError {
  constructor(entityType: string, entityId: string) {
    super({
      code: ErrorCode.ENTITY_NOT_FOUND,
      message: `${entityType} with id '${entityId}' not found`,
      context: { entityType, entityId },
    });
    this.name = 'EntityNotFoundError';
  }
}

export class ValidationError extends AppError {
  public readonly errors: z.ZodError | null;

  constructor(message: string, errors?: z.ZodError) {
    super({
      code: ErrorCode.VALIDATION_ERROR,
      message,
      context: { validationErrors: errors?.errors },
    });
    this.name = 'ValidationError';
    this.errors = errors ?? null;
  }
}

export class AuthenticationError extends AppError {
  constructor(message = 'Authentication failed') {
    super({
      code: ErrorCode.AUTHENTICATION_ERROR,
      message,
      severity: ErrorSeverity.WARNING,
    });
    this.name = 'AuthenticationError';
  }
}

export class AuthorizationError extends AppError {
  constructor(message = 'Access denied') {
    super({
      code: ErrorCode.AUTHORIZATION_ERROR,
      message,
      severity: ErrorSeverity.WARNING,
    });
    this.name = 'AuthorizationError';
  }
}

/**
 * Result type for functional error handling.
 */
export type Result<T, E extends AppError = AppError> =
  | { success: true; data: T }
  | { success: false; error: E };

/**
 * Helper to create success result.
 */
export function ok<T>(data: T): Result<T, never> {
  return { success: true, data };
}

/**
 * Helper to create error result.
 */
export function err<E extends AppError>(error: E): Result<never, E> {
  return { success: false, error };
}
