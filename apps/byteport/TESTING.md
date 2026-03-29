# BytePort Testing Guide

This document provides comprehensive information about testing in the BytePort project, including backend Go tests, frontend React/Next.js tests, and E2E tests with Playwright.

## Table of Contents

- [Overview](#overview)
- [Test Architecture](#test-architecture)
- [Backend Tests (Go)](#backend-tests-go)
- [Frontend Tests (React/Next.js)](#frontend-tests-reactnextjs)
- [E2E Tests (Playwright)](#e2e-tests-playwright)
- [Running Tests](#running-tests)
- [CI/CD Integration](#cicd-integration)
- [Best Practices](#best-practices)

## Overview

BytePort uses a comprehensive testing strategy that covers:

- **Backend Tests**: Go tests with testify/suite, in-memory repositories, and SQLite for testing
- **Frontend Tests**: Vitest with Testing Library, MSW for API mocking
- **E2E Tests**: Playwright for complete user journey testing
- **CI/CD**: GitHub Actions workflows for automated testing

### Test Coverage Goals

- Backend: >80% code coverage
- Frontend: >70% code coverage
- E2E: Critical user journeys and integration flows

## Test Architecture

```
BytePort/
├── backend/api/
│   ├── handlers/
│   │   ├── deployment_handler.go
│   │   └── deployment_handler_test.go
│   ├── models/
│   │   ├── deployment.go
│   │   └── models_test.go
│   ├── repositories/
│   │   └── repositories_test.go
│   └── testhelpers/
│       ├── db_helpers.go
│       ├── router_helpers.go
│       └── in_memory_repos.go
├── frontend/web-next/
│   ├── __tests__/
│   │   ├── components/
│   │   ├── hooks/
│   │   └── stores/
│   ├── e2e/
│   │   ├── auth/
│   │   ├── dashboard/
│   │   └── deployment/
│   ├── test/
│   │   ├── mocks/
│   │   ├── msw/
│   │   └── utils/
│   ├── vitest.config.mts
│   └── playwright.config.ts
└── scripts/
    └── test_runner.py
```

## Backend Tests (Go)

### Structure

Backend tests follow idiomatic Go testing patterns with testify/suite for test organization:

```go
type DeploymentHandlerTestSuite struct {
    suite.Suite
    router     *gin.Engine
    deployRepo *testhelpers.InMemoryDeploymentRepository
}

func (suite *DeploymentHandlerTestSuite) SetupTest() {
    // Fresh state for each test
    suite.deployRepo = testhelpers.NewInMemoryDeploymentRepository()
    suite.router = testhelpers.SetupTestRouter()
}

func TestDeploymentHandlerTestSuite(t *testing.T) {
    suite.Run(t, new(DeploymentHandlerTestSuite))
}
```

### Running Backend Tests

```bash
# From project root
cd backend/api

# Run all tests
go test ./...

# Run with verbose output
go test -v ./...

# Run with coverage
go test -v -race -coverprofile=coverage.out ./...

# View coverage report
go tool cover -html=coverage.out

# Run specific test suite
go test -v -run TestDeploymentHandlerTestSuite

# Run specific test
go test -v -run TestDeploymentHandlerTestSuite/TestCreateDeployment
```

### Test Helpers

The `testhelpers/` directory provides:

- **In-memory repositories**: Fast, isolated test doubles
- **Database helpers**: SQLite in-memory database setup
- **Router helpers**: Gin router configuration for tests
- **HTTP helpers**: Request/response utilities

### Key Patterns

1. **Test Suites**: Group related tests with `testify/suite`
2. **In-Memory Repos**: Use fast in-memory implementations for unit tests
3. **SQLite Testing**: Use SQLite in-memory DB for integration tests
4. **Table-Driven Tests**: Use where appropriate for testing multiple scenarios
5. **Assertions**: Use testify assertions for clear, readable tests

## Frontend Tests (React/Next.js)

### Structure

Frontend tests use Vitest with Testing Library and MSW for API mocking:

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { DeploymentCard } from '@/components/DeploymentCard';

describe('DeploymentCard', () => {
  it('renders deployment information', () => {
    const deployment = createMockDeployment();
    render(<DeploymentCard deployment={deployment} />);
    expect(screen.getByText(deployment.name)).toBeInTheDocument();
  });
});
```

### Running Frontend Tests

```bash
# From project root
cd frontend/web-next

# Run tests in watch mode (default)
pnpm test

# Run tests once
pnpm test:run

# Run with coverage
pnpm test:coverage

# Run with UI
pnpm test:ui

# Run specific test file
pnpm test deployment

# Update snapshots
pnpm test -u
```

### Test Utilities

The `test/` directory provides:

- **MSW Handlers**: Mock API responses in `test/msw/handlers.ts`
- **Test Utilities**: Factory functions for creating test data
- **Mocks**: Zustand store mocks, module mocks

### MSW Setup

MSW (Mock Service Worker) intercepts API calls in tests:

```typescript
// test/msw/handlers.ts
import { http, HttpResponse } from 'msw';

export const handlers = [
  http.get('/api/v1/deployments', () => {
    return HttpResponse.json({
      deployments: [createMockDeployment()],
    });
  }),
];
```

### Key Patterns

1. **Component Tests**: Test UI rendering and user interactions
2. **Hook Tests**: Test custom hooks with `renderHook`
3. **Store Tests**: Test Zustand stores with mocked middleware
4. **MSW Mocking**: Mock API calls consistently across tests
5. **Factory Functions**: Create test data with sensible defaults

## E2E Tests (Playwright)

### Structure

E2E tests use Playwright with Page Object Models:

```typescript
// e2e/pages/DashboardPage.ts
export class DashboardPage extends BasePage {
  async goto() {
    await this.page.goto('/dashboard');
    await this.waitForLoad();
  }

  async getDeploymentCards() {
    return await this.page.locator('[data-testid="deployment-card"]').all();
  }
}

// e2e/dashboard/overview.spec.ts
test('displays deployments on dashboard', async ({ page }) => {
  const dashboard = new DashboardPage(page);
  await dashboard.goto();
  const cards = await dashboard.getDeploymentCards();
  expect(cards.length).toBeGreaterThan(0);
});
```

### Running E2E Tests

```bash
# From project root
cd frontend/web-next

# Run all E2E tests
pnpm test:e2e

# Run in UI mode
pnpm test:e2e:ui

# Run in headed mode (see browser)
pnpm test:e2e:headed

# Run in debug mode
pnpm test:e2e:debug

# Run specific test file
pnpm test:e2e auth

# Run on specific browser
pnpm test:e2e --project=chromium
pnpm test:e2e --project=firefox
pnpm test:e2e --project=webkit
```

### Page Object Models

Located in `e2e/pages/`, Page Objects encapsulate page interactions:

- **BasePage**: Common functionality (navigation, waiting)
- **DashboardPage**: Dashboard interactions
- **DeploymentPage**: Deployment management
- **LoginPage**: Authentication flows

### Authentication

Authentication state is managed via storage state:

```typescript
// playwright.config.ts
export default defineConfig({
  use: {
    storageState: 'e2e/.auth/user.json',
  },
});

// e2e/auth.setup.ts - runs before tests
test('authenticate', async ({ page }) => {
  await page.goto('/login');
  // Perform login...
  await page.context().storageState({ path: 'e2e/.auth/user.json' });
});
```

### Key Patterns

1. **Page Object Models**: Encapsulate page interactions
2. **Storage State**: Persist authentication across tests
3. **Flexible Selectors**: Use data-testid, text, and role selectors
4. **Conditional Checks**: Handle dynamic UI states
5. **API Testing**: Use Playwright's request API for integration tests

## Running Tests

### Using the Test Runner Script

A unified Python test runner is available for running all tests:

```bash
# Run all tests
./scripts/test_runner.py --all

# Run specific test suites
./scripts/test_runner.py --backend
./scripts/test_runner.py --frontend
./scripts/test_runner.py --e2e

# Run with coverage
./scripts/test_runner.py --all --coverage

# Run in watch mode
./scripts/test_runner.py --frontend --watch

# Combine flags
./scripts/test_runner.py --backend --frontend --coverage
```

### Via BytePort Orchestrator

Tests can also be run via the main orchestrator:

```bash
# Run all tests
./byteport.py --test

# Run unit tests only
./byteport.py --test-unit

# Run E2E tests only
./byteport.py --test-e2e
```

### Individual Test Commands

#### Backend
```bash
cd backend/api && go test -v ./...
```

#### Frontend Unit Tests
```bash
cd frontend/web-next && pnpm test:run
```

#### E2E Tests
```bash
cd frontend/web-next && pnpm test:e2e
```

## CI/CD Integration

### GitHub Actions Workflows

BytePort uses two main workflows:

#### 1. Test Suite (`test.yml`)

Runs on push to main/develop and on pull requests:

- **Backend Tests**: Go tests with PostgreSQL service
- **Frontend Tests**: Vitest tests with coverage
- **E2E Tests**: Playwright tests with Chromium
- **Lint**: ESLint and golangci-lint
- **Test Summary**: Aggregates results

```yaml
# Triggered on:
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
  workflow_dispatch:
```

#### 2. PR Checks (`pr-checks.yml`)

Optimized for fast feedback on pull requests:

- **Changed File Detection**: Only runs relevant tests
- **Quick Lint**: Fast ESLint and TypeScript checks
- **PR Comments**: Posts test results and coverage to PR

```yaml
# Features:
- Detects changed backend/frontend files
- Runs only necessary tests
- Comments results on PR
- Faster feedback loop
```

### Viewing CI Results

1. **GitHub Actions Tab**: View all workflow runs
2. **PR Checks**: See results directly in PR
3. **Codecov**: View coverage reports (if configured)
4. **Artifacts**: Download test reports and logs

### Local CI Simulation

Test CI workflows locally before pushing:

```bash
# Install act (GitHub Actions local runner)
brew install act

# Run workflow locally
act -j backend-tests
act -j frontend-tests
act -j e2e-tests
```

## Best Practices

### General

1. **Write Tests First**: Follow TDD when possible
2. **Test Behavior**: Focus on what, not how
3. **Isolate Tests**: Each test should be independent
4. **Clear Names**: Use descriptive test names
5. **Arrange-Act-Assert**: Structure tests clearly

### Backend

1. **Use Test Suites**: Group related tests with testify/suite
2. **In-Memory First**: Use in-memory repos for unit tests
3. **Test Database State**: Verify DB changes in integration tests
4. **Mock External Services**: Don't call real APIs
5. **Test Error Cases**: Cover edge cases and failures

### Frontend

1. **Test User Behavior**: Simulate real user interactions
2. **Use Testing Library Queries**: Prefer accessible queries
3. **Mock API Calls**: Use MSW consistently
4. **Avoid Implementation Details**: Don't test internal state
5. **Test Accessibility**: Use accessible queries and roles

### E2E

1. **Test Critical Flows**: Focus on business-critical journeys
2. **Use Page Objects**: Keep tests maintainable
3. **Handle Async**: Wait for elements properly
4. **Flexible Selectors**: Use data-testid or accessible roles
5. **Clean State**: Reset state between tests

### Performance

1. **Parallel Execution**: Run independent tests in parallel
2. **Smart Caching**: Cache dependencies in CI
3. **Selective Testing**: Only run affected tests in CI
4. **Fast Feedback**: Prioritize quick smoke tests
5. **Profile Slow Tests**: Optimize or split long-running tests

## Troubleshooting

### Backend Tests Failing

```bash
# Check Go version
go version

# Clean cache
go clean -cache -testcache

# Verify dependencies
go mod verify

# Run with verbose output
go test -v ./...
```

### Frontend Tests Failing

```bash
# Clear node modules
rm -rf node_modules pnpm-lock.yaml
pnpm install

# Update snapshots
pnpm test -u

# Check for module resolution issues
pnpm test -- --no-coverage
```

### E2E Tests Failing

```bash
# Reinstall Playwright browsers
pnpm playwright install --with-deps

# Run in headed mode to see what's happening
pnpm test:e2e:headed

# Check screenshots and traces
ls -la frontend/web-next/test-results/

# Verify app is running
./byteport.py --local
```

### CI Tests Failing

1. **Check workflow logs**: View detailed output in GitHub Actions
2. **Reproduce locally**: Run the same commands as CI
3. **Check environment**: Verify env vars and secrets
4. **Test artifacts**: Download and inspect test reports

## Additional Resources

- [Go Testing Documentation](https://go.dev/doc/tutorial/add-a-test)
- [Testify Documentation](https://github.com/stretchr/testify)
- [Vitest Documentation](https://vitest.dev/)
- [Testing Library Documentation](https://testing-library.com/)
- [MSW Documentation](https://mswjs.io/)
- [Playwright Documentation](https://playwright.dev/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

## Contributing

When adding new features:

1. Write tests for new functionality
2. Ensure all tests pass locally
3. Update this documentation if needed
4. Verify CI passes before merging

## Support

For testing questions or issues:

1. Check this documentation
2. Review existing tests for examples
3. Check CI logs for errors
4. Ask in team chat or open an issue
