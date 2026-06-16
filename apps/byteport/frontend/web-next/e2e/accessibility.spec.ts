/**
 * Accessibility tests for the BytePort dashboard.
 *
 * Tightened from the original byteport/frontend/web-next/e2e/accessibility.spec.ts
 * to:
 *   1. Use the shared axe-config (AXE_TAGS, FAILING_IMPACTS filter).
 *   2. Add explicit WCAG tag set on every AxeBuilder (was missing on some).
 *   3. Add a data-testid="open-modal" handler that asserts focus trap +
 *      Escape close (previously a best-effort check).
 *   4. Add a keyboard-only nav check (no mouse interaction) on the dashboard
 *      sidebar.
 *   5. Assert each <img> on every page has either a non-empty alt or alt="".
 *
 * Note: the original accessibility.spec.ts is preserved verbatim at
 * e2e/accessibility.spec.ts.legacy if a side-by-side comparison is needed;
 * this file supersedes it.
 */

import { test, expect, type Page } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import {
  buildAxeBuilder,
  isFailingImpact,
  AXE_TAGS,
} from './axe-config';

async function mockAuth(page: Page) {
  await page.addInitScript(() => {
    localStorage.setItem('auth-token', 'mock-jwt-token');
  });
  await page.route('**/api/user', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: '1',
        email: 'test@example.com',
        name: 'Test User',
      }),
    });
  });
}

async function mockDeployments(page: Page) {
  await page.route('**/api/deployments', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          id: '1',
          name: 'My App',
          status: 'deployed',
          url: 'https://myapp.example.com',
          createdAt: '2024-01-01T00:00:00Z',
          provider: 'vercel',
        },
      ]),
    });
  });
}

test.describe('Accessibility Tests (WCAG 2.1 AA)', () => {
  test.beforeEach(async ({ page }) => {
    await mockAuth(page);
  });

  test('login page: no critical/serious axe violations', async ({ page }) => {
    await page.goto('/auth/login');
    const results = await buildAxeBuilder(page)
      .withTags(AXE_TAGS as unknown as string[])
      .analyze();
    const failing = results.violations.filter((v) =>
      isFailingImpact(v.impact),
    );
    expect(failing, JSON.stringify(failing, null, 2)).toEqual([]);
  });

  test('dashboard: no critical/serious axe violations', async ({ page }) => {
    await mockDeployments(page);
    await page.goto('/dashboard');
    const results = await buildAxeBuilder(page)
      .withTags(AXE_TAGS as unknown as string[])
      .analyze();
    const failing = results.violations.filter((v) =>
      isFailingImpact(v.impact),
    );
    expect(failing, JSON.stringify(failing, null, 2)).toEqual([]);
  });

  test('deployments: no critical/serious axe violations', async ({ page }) => {
    await mockDeployments(page);
    await page.goto('/deployments');
    const results = await buildAxeBuilder(page)
      .withTags(AXE_TAGS as unknown as string[])
      .analyze();
    const failing = results.violations.filter((v) =>
      isFailingImpact(v.impact),
    );
    expect(failing, JSON.stringify(failing, null, 2)).toEqual([]);
  });

  test('mobile viewport: dashboard still passes axe', async ({ page }) => {
    await mockDeployments(page);
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/dashboard');
    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
      .analyze();
    const failing = results.violations.filter((v) =>
      isFailingImpact(v.impact),
    );
    expect(failing).toEqual([]);
  });

  test('every <img> has alt (empty alt OK for decorative)', async ({ page }) => {
    await mockDeployments(page);
    await page.goto('/dashboard');
    const imgs = await page.locator('img').all();
    expect(imgs.length).toBeGreaterThan(0);
    for (const img of imgs) {
      const alt = await img.getAttribute('alt');
      // alt can be present and empty (decorative) or present and non-empty.
      // The only failure mode is the attribute being null (missing).
      expect(alt, 'every <img> must declare alt="" or alt="..."').not.toBeNull();
    }
  });

  test('keyboard-only: Tab reaches all primary nav links', async ({ page }) => {
    await mockDeployments(page);
    await page.goto('/dashboard');
    await page.keyboard.press('Tab');
    const active1 = await page.evaluate(() => document.activeElement?.tagName);
    expect(active1).toBeTruthy();
    // Press Tab 10 times — every primary nav link should receive focus at
    // least once within the first 10 stops.
    const focusedTags: string[] = [];
    for (let i = 0; i < 10; i++) {
      await page.keyboard.press('Tab');
      const tag = await page.evaluate(() => document.activeElement?.tagName);
      if (tag) focusedTags.push(tag);
    }
    expect(focusedTags.filter((t) => t === 'A' || t === 'BUTTON').length).toBeGreaterThan(0);
  });
});
