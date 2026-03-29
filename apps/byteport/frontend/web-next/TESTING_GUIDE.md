# 🧪 Comprehensive Frontend Testing Guide

## 📋 Overview

This guide covers the comprehensive testing strategy for the BytePort frontend application, including unit tests, E2E tests, performance testing, accessibility testing, and visual regression testing.

## 🚀 Quick Start

### Run All Tests
```bash
pnpm test:all
```

### Run Specific Test Types
```bash
# Unit tests (currently disabled due to React 19 compatibility)
pnpm test:unit

# E2E tests
pnpm test:e2e

# Performance tests
pnpm test:performance

# Accessibility tests
pnpm test:accessibility

# Visual regression tests
pnpm test:visual

# CI/CD pipeline
pnpm test:ci
```

## 🏗️ Testing Architecture

### 1. Unit Testing (Vitest + Testing Library)
- **Status**: ⚠️ Currently disabled due to React 19 compatibility issues
- **Framework**: Vitest with React Testing Library
- **Coverage**: All components, hooks, utilities, and business logic
- **Mocking**: MSW for API calls, vi.mock for modules

### 2. E2E Testing (Playwright)
- **Status**: ✅ Active
- **Framework**: Playwright with TypeScript
- **Browsers**: Chrome, Firefox, Safari, Mobile Chrome, Mobile Safari
- **Coverage**: Critical user journeys and workflows

### 3. Performance Testing (Lighthouse CI)
- **Status**: ✅ Active
- **Framework**: Lighthouse CI with custom thresholds
- **Metrics**: Core Web Vitals, Performance, Accessibility, SEO
- **Thresholds**: Performance > 90, Accessibility > 95, SEO > 85

### 4. Accessibility Testing (axe-core)
- **Status**: ✅ Active
- **Framework**: @axe-core/playwright
- **Standards**: WCAG 2.1 AA compliance
- **Coverage**: All components and pages

### 5. Visual Regression Testing (Playwright)
- **Status**: ✅ Active
- **Framework**: Playwright with screenshot comparison
- **Coverage**: All UI components and page layouts
- **Responsive**: Multiple viewport sizes

## 📁 Test Structure

```
frontend/web-next/
├── __tests__/                    # Unit tests (currently disabled)
│   ├── components/               # Component tests
│   ├── hooks/                    # Custom hook tests
│   ├── lib/                      # Utility function tests
│   └── context/                  # Context provider tests
├── e2e/                         # E2E tests
│   ├── auth.spec.ts             # Authentication flows
│   ├── dashboard.spec.ts        # Dashboard interactions
│   ├── deployments.spec.ts      # Deployment workflows
│   ├── accessibility.spec.ts    # Accessibility tests
│   └── visual-regression.spec.ts # Visual regression tests
├── performance/                 # Performance tests
│   └── lighthouse-ci.js         # Lighthouse CI configuration
├── scripts/                     # Test utilities
│   └── test-runner.js           # Comprehensive test runner
└── test-utils/                  # Shared testing utilities
    └── test-setup.tsx           # Test setup and mocks
```

## 🧪 Test Categories

### Unit Tests
- **Components**: Rendering, props, events, state changes
- **Hooks**: State management, side effects, error handling
- **Utilities**: Pure functions, data transformations
- **Context**: State providers, consumers, updates

### E2E Tests
- **Authentication**: Login, logout, session management
- **Deployments**: Create, monitor, manage deployments
- **Dashboard**: Navigation, data display, interactions
- **Settings**: Configuration, preferences, account management

### Performance Tests
- **Core Web Vitals**: LCP, FID, CLS, FCP, TTFB
- **Lighthouse**: Performance, Accessibility, Best Practices, SEO
- **Load Testing**: API response times, concurrent users
- **Bundle Analysis**: JavaScript bundle size, tree shaking

### Accessibility Tests
- **Keyboard Navigation**: Tab order, focus management
- **Screen Reader**: ARIA labels, semantic HTML
- **Color Contrast**: WCAG AA compliance
- **Form Validation**: Error messages, field associations

### Visual Regression Tests
- **Component States**: Default, hover, focus, disabled
- **Responsive Design**: Mobile, tablet, desktop
- **Theme Variations**: Light, dark mode
- **Data States**: Loading, empty, error, success

## 🛠️ Writing Tests

### E2E Test Example
```typescript
import { test, expect } from '@playwright/test'

test.describe('Authentication Flow', () => {
  test('should login successfully', async ({ page }) => {
    await page.goto('/auth/login')
    
    await page.fill('input[type="email"]', 'test@example.com')
    await page.fill('input[type="password"]', 'password123')
    await page.click('button[type="submit"]')
    
    await expect(page).toHaveURL('/dashboard')
    await expect(page.locator('h1')).toContainText('Dashboard')
  })
})
```

### Accessibility Test Example
```typescript
import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

test('should not have accessibility violations', async ({ page }) => {
  await page.goto('/dashboard')
  
  const accessibilityScanResults = await new AxeBuilder({ page }).analyze()
  
  expect(accessibilityScanResults.violations).toEqual([])
})
```

### Visual Regression Test Example
```typescript
import { test, expect } from '@playwright/test'

test('dashboard page visual regression', async ({ page }) => {
  await page.goto('/dashboard')
  await page.waitForLoadState('networkidle')
  
  await expect(page).toHaveScreenshot('dashboard-page.png', {
    fullPage: true,
    threshold: 0.2
  })
})
```

## 📊 Coverage Targets

### Unit Tests
- **Statements**: 100% (when enabled)
- **Branches**: 100% (when enabled)
- **Functions**: 100% (when enabled)
- **Lines**: 100% (when enabled)

### E2E Tests
- **Critical Paths**: 100%
- **User Journeys**: 100%
- **Error Scenarios**: 90%

### Performance
- **Lighthouse Performance**: > 90
- **Core Web Vitals**: All green
- **Bundle Size**: < 500KB gzipped

### Accessibility
- **WCAG 2.1 AA**: 100% compliance
- **Keyboard Navigation**: 100%
- **Screen Reader**: 100%

## 🚀 CI/CD Integration

### GitHub Actions Workflow
The comprehensive testing workflow runs on every push and pull request:

1. **Unit Tests**: Vitest with coverage reporting
2. **E2E Tests**: Playwright across multiple browsers
3. **Performance Tests**: Lighthouse CI with thresholds
4. **Accessibility Tests**: axe-core compliance checking
5. **Visual Regression Tests**: Screenshot comparison
6. **Security Scan**: Trivy vulnerability scanning
7. **Dependency Audit**: Package security audit

### Test Reports
- **Coverage Reports**: HTML coverage reports in `coverage/`
- **E2E Reports**: Playwright HTML reports in `playwright-report/`
- **Performance Reports**: Lighthouse CI reports in `test-results/`
- **Comprehensive Report**: Combined test results in `test-results/`

## 🔧 Configuration

### Vitest Configuration
```typescript
// vitest.config.mts
export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./vitest.setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      thresholds: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80
        }
      }
    }
  }
})
```

### Playwright Configuration
```typescript
// playwright.config.ts
export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: process.env.CI ? 'github' : 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure'
  }
})
```

### Lighthouse CI Configuration
```json
// lighthouserc.json
{
  "ci": {
    "collect": {
      "numberOfRuns": 3,
      "startServerCommand": "pnpm start",
      "url": ["http://localhost:3000"]
    },
    "assert": {
      "preset": "lighthouse:recommended",
      "assertions": {
        "categories:performance": ["error", {"minScore": 0.90}],
        "categories:accessibility": ["error", {"minScore": 0.95}]
      }
    }
  }
}
```

## 📈 Monitoring and Reporting

### Coverage Reports
- **Unit Tests**: HTML coverage reports
- **E2E Tests**: Playwright HTML reports
- **Performance**: Lighthouse CI reports
- **Accessibility**: axe-core reports

### Quality Gates
- **Unit Coverage**: Must be 100% (when enabled)
- **E2E Tests**: Must pass all critical paths
- **Performance**: Must meet thresholds
- **Accessibility**: Must be WCAG compliant

## 🐛 Debugging Tests

### E2E Test Debugging
```bash
# Run tests in headed mode
pnpm test:e2e:headed

# Run tests in debug mode
pnpm test:e2e:debug

# Run specific test file
pnpm test:e2e auth.spec.ts

# Run tests with UI
pnpm test:e2e:ui
```

### Performance Test Debugging
```bash
# Run performance tests with detailed output
node performance/lighthouse-ci.js

# Run Lighthouse on specific URL
npx lighthouse http://localhost:3000 --output html --output-path ./lighthouse-report.html
```

### Visual Regression Debugging
```bash
# Update visual regression baselines
pnpm test:visual --update-snapshots

# Run specific visual test
pnpm test:visual --grep "dashboard"
```

## 📚 Best Practices

### E2E Testing
- Test user journeys, not technical details
- Use data-testid for reliable selectors
- Keep tests independent and isolated
- Use page object model for maintainability

### Performance Testing
- Test on realistic data and conditions
- Monitor trends over time
- Set appropriate thresholds
- Test on different devices and networks

### Accessibility Testing
- Test with keyboard navigation
- Use screen reader testing
- Validate color contrast
- Test with different user abilities

### Visual Regression Testing
- Test all component states
- Include responsive variations
- Test theme changes
- Update baselines when UI changes intentionally

## 🎯 Success Metrics

### Coverage Metrics
- Unit test coverage: 100% (when enabled)
- E2E test coverage: 100% of critical paths
- Performance score: > 90
- Accessibility score: > 95

### Quality Metrics
- Zero critical bugs in production
- < 2 second page load times
- 100% WCAG 2.1 AA compliance
- Zero accessibility violations

### Developer Experience
- Fast test execution (< 5 minutes)
- Clear error messages and debugging
- Easy test maintenance and updates
- Comprehensive documentation

## 🚀 Getting Started

1. **Install Dependencies**
   ```bash
   pnpm install
   ```

2. **Run All Tests**
   ```bash
   pnpm test:all
   ```

3. **Run Specific Tests**
   ```bash
   pnpm test:e2e
   pnpm test:performance
   pnpm test:accessibility
   pnpm test:visual
   ```

4. **View Test Reports**
   - E2E: `playwright-report/index.html`
   - Performance: `test-results/lighthouse-results.html`
   - Comprehensive: `test-results/comprehensive-test-report.html`

## 📚 Resources

- [Vitest Documentation](https://vitest.dev/)
- [Playwright Documentation](https://playwright.dev/)
- [Testing Library Documentation](https://testing-library.com/)
- [Lighthouse CI Documentation](https://github.com/GoogleChrome/lighthouse-ci)
- [axe-core Documentation](https://github.com/dequelabs/axe-core)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

---

This comprehensive testing strategy ensures the BytePort frontend application maintains high quality, performance, and accessibility standards while providing excellent developer experience and user satisfaction.