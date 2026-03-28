# TypeScript Coding Standards

## Overview

This document defines coding standards for TypeScript projects in the Phenotype ecosystem.

## Related xDD Methodologies

| Method | Application |
|--------|-------------|
| TDD | Write tests before implementation |
| Property-based Testing | Use fast-check for core logic |
| Contract Testing | Use ts-auto-mock for interfaces |
| BDD | Use jest-cucumber or cucumber-js |

## Project Structure

```
src/
├── domain/
│   ├── entities/
│   ├── value-objects/
│   ├── services/
│   ├── aggregates/
│   ├── events/
│   └── errors.ts
├── ports/
│   ├── input/
│   │   ├── use-cases.ts
│   │   ├── commands.ts
│   │   └── queries.ts
│   └── output/
│       ├── repositories.ts
│       └── publishers.ts
├── adapters/
│   ├── primary/
│   │   ├── http/
│   │   │   ├── controllers/
│   │   │   └── routes.ts
│   │   └── cli/
│   └── secondary/
│       ├── postgres/
│       ├── redis/
│       └── http/
├── application/
│   └── services/
└── index.ts

tests/
├── unit/
├── integration/
└── e2e/
```

## Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| File | kebab-case | `user-repository.ts` |
| Directory | kebab-case | `user-repository/` |
| Class | PascalCase | `UserRepository` |
| Interface | PascalCase or I prefix | `UserRepository` or `IUserRepository` |
| Type | PascalCase | `UserDTO` |
| Enum | PascalCase | `UserStatus` |
| Function | camelCase | `getUserById` |
| Variable | camelCase | `userId` |
| Constant | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| React Component | PascalCase | `UserCard.tsx` |
| React Hook | camelCase, use prefix | `useUser` |

## Code Style

### ESLint Configuration

```json
{
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:import/recommended",
    "prettier"
  ],
  "plugins": ["@typescript-eslint", "import", "unused-imports"],
  "rules": {
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/explicit-function-return-type": "warn",
    "@typescript-eslint/no-explicit-any": "error",
    "import/no-unresolved": "error",
    "unused-imports/no-unused-imports": "error"
  }
}
```

### TypeScript Rules

```typescript
// Avoid any - use unknown instead
// BAD
function processData(data: any): any {
  return data;
}

// GOOD
function processData<T>(data: T): T {
  return data;
}

// Better - use specific types
interface UserData {
  id: string;
  email: string;
}

function processUser(data: UserData): UserData {
  return data;
}
```

### Error Handling

```typescript
// Custom error classes
export class DomainError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly details?: Record<string, unknown>
  ) {
    super(message);
    this.name = 'DomainError';
  }
}

export class NotFoundError extends DomainError {
  constructor(resource: string, id: string) {
    super(
      `${resource} not found: ${id}`,
      'NOT_FOUND',
      { resource, id }
    );
  }
}

// Result pattern
export type Result<T, E = Error> =
  | { success: true; data: T }
  | { success: false; error: E };

async function getUser(id: string): Promise<Result<User, DomainError>> {
  try {
    const user = await repository.findById(id);
    if (!user) {
      return { success: false, error: new NotFoundError('User', id) };
    }
    return { success: true, data: user };
  } catch (error) {
    return { success: false, error: error as DomainError };
  }
}
```

## TypeScript Configuration

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "resolveJsonModule": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

## Testing

### Jest Configuration

```json
{
  "preset": "ts-jest",
  "testEnvironment": "node",
  "roots": ["<rootDir>/src", "<rootDir>/tests"],
  "testMatch": ["**/*.test.ts"],
  "collectCoverageFrom": [
    "src/**/*.ts",
    "!src/**/*.d.ts",
    "!src/**/*.interface.ts"
  ],
  "coverageThreshold": {
    "global": {
      "branches": 80,
      "functions": 80,
      "lines": 80,
      "statements": 80
    }
  }
}
```

### Unit Tests

```typescript
// src/domain/user.test.ts
import { describe, it, expect } from 'vitest';
import { User, UserErrors } from './user';

describe('User', () => {
  describe('create', () => {
    it('should create a valid user', () => {
      // Given
      const email = 'test@example.com';
      const name = 'Test User';

      // When
      const result = User.create({ email, name });

      // Then
      expect(result.isOk()).toBe(true);
      expect(result.unwrap().email.value).toBe(email);
    });

    it('should reject invalid email', () => {
      // Given
      const invalidEmail = 'not-an-email';

      // When
      const result = User.create({ email: invalidEmail, name: 'Test' });

      // Then
      expect(result.isErr()).toBe(true);
      expect(result.unwrapErr()).toBeInstanceOf(UserErrors.InvalidEmail);
    });
  });
});
```

### Property-Based Tests (fast-check)

```typescript
import fc from 'fast-check';

// Email validation property test
fc.assert(
  fc.property(
    fc.emailAddress(),
    (email) => {
      const result = Email.create(email);
      return result.isOk();
    }
  )
);
```

## Documentation

### JSDoc

```typescript
/**
 * Creates a new user account.
 *
 * @param email - The user's email address
 * @param name - The user's display name
 * @returns A Result containing the created User or a DomainError
 *
 * @example
 * ```typescript
 * const result = User.create({
 *   email: 'test@example.com',
 *   name: 'Test User'
 * });
 *
 * if (result.isOk()) {
 *   console.log('Created user:', result.value.id);
 * }
 * ```
 *
 * @throws {UserErrors.InvalidEmail} If the email format is invalid
 * @throws {UserErrors.EmptyName} If the name is empty
 */
export function create(
  email: string,
  name: string
): Result<User, DomainError> {
  // implementation
}
```

## Dependencies

### Dependency Rules

| Layer | Allowed Dependencies |
|-------|---------------------|
| Domain | TypeScript built-ins, zod (for schemas) |
| Ports | Domain, TypeScript built-ins |
| Adapters | Ports, external libraries |
| Application | Ports, Domain |

### Package.json Structure

```json
{
  "name": "@lib/hexagonal-ts",
  "version": "1.0.0",
  "type": "module",
  "main": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": "./dist/index.js",
    "./adapters/*": "./dist/adapters/*/index.js",
    "./ports/*": "./dist/ports/*/index.js"
  },
  "files": ["dist", "src"]
}
```

---

*Maintained by: Architecture Guild*
