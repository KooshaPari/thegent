/**
 * Root-level WCAG axe sweep.
 *
 * This test boots the VitePress docs (root thegent docsite) and the Astro
 * landing page (apps/landing) against a local dev server, then runs an
 * AxeBuilder scan for each top-level route. It acts as a cross-sub-app gate
 * so a regression in either surface fails the same CI job.
 *
 * Per-route scan strategy:
 *   - The default tag set is the WCAG 2.0 + 2.1 A + AA set from axe-config.ts.
 *   - We assert violations are empty AT THE IMPACT FILTER `critical | serious`
 *     to avoid blocking on lower-severity findings that have product sign-off.
 *   - `moderate` and `minor` violations are surfaced in the test report but
 *     do not fail the test, unless `A11Y_FAIL_ON_MODERATE=1` is set.
 */

import { test, expect, type Page } from '@playwright/test';
import {
  buildAxeBuilder,
  isFailingImpact,
  FAILING_IMPACTS,
} from './axe-config';

interface RouteSpec {
  name: string;
  url: string;
  /** Rule IDs to disable for this specific route (e.g. layout-driven false positives). */
  disableRules?: readonly string[];
}

const DOCS_BASE_URL = process.env.DOCS_BASE_URL ?? 'http://localhost:4321';
const LANDING_BASE_URL = process.env.LANDING_BASE_URL ?? 'http://localhost:4322';

const ROUTES: readonly RouteSpec[] = [
  // VitePress docsite (root thegent)
  { name: 'docs:home', url: `${DOCS_BASE_URL}/` },
  { name: 'docs:guide', url: `${DOCS_BASE_URL}/guide/` },
  { name: 'docs:api', url: `${DOCS_BASE_URL}/api/` },
  // Astro landing (apps/landing)
  { name: 'landing:home', url: `${LANDING_BASE_URL}/` },
  { name: 'landing:qa', url: `${LANDING_BASE_URL}/qa` },
  { name: 'landing:otel', url: `${LANDING_BASE_URL}/otel` },
  { name: 'landing:preview', url: `${LANDING_BASE_URL}/preview/1` },
] as const;

const FAIL_ON_MODERATE = process.env.A11Y_FAIL_ON_MODERATE === '1';

test.describe('AT1 — WCAG axe scan (root thegent + Astro landing)', () => {
  for (const route of ROUTES) {
    test(`${route.name} (${route.url}) has no critical/serious violations`, async ({
      page,
    }: { page: Page }) => {
      await page.goto(route.url, { waitUntil: 'networkidle' });

      // Wait for fonts so color-contrast axe rules run on real glyphs.
      await page.evaluate(() => document.fonts.ready);

      const builder = buildAxeBuilder(page, {
        disableRules: route.disableRules,
      });
      const results = await builder.analyze();

      // Always log the full violation list for the PR report.
      if (results.violations.length > 0) {
        // eslint-disable-next-line no-console
        console.log(
          `[${route.name}] axe violations:\n` +
            results.violations
              .map(
                (v) =>
                  `  - ${v.id} [${v.impact ?? 'unknown'}] ${v.help} ` +
                  `(nodes: ${v.nodes.length})`,
              )
              .join('\n'),
        );
      }

      const failing = results.violations.filter((v) =>
        isFailingImpact(v.impact),
      );

      expect(
        failing,
        `${route.name}: expected no ${FAILING_IMPACTS.join('/')} violations, ` +
          `got ${failing.length}`,
      ).toEqual([]);

      if (FAIL_ON_MODERATE) {
        const moderate = results.violations.filter(
          (v) => v.impact === 'moderate',
        );
        expect(
          moderate,
          `${route.name}: A11Y_FAIL_ON_MODERATE is set; moderate violations fail the build`,
        ).toEqual([]);
      }
    });
  }

  test('after fixing all violations, axe reports zero of any impact', async ({
    page,
  }) => {
    // Sanity sweep: pick a single high-value route and assert absolute zero
    // violations. This test is tagged to opt in only when the suite is in
    // "all clear" mode (set AT1_STRICT=1 in CI).
    test.skip(
      process.env.AT1_STRICT !== '1',
      'Set AT1_STRICT=1 to enable the absolute-zero sweep',
    );

    await page.goto(`${LANDING_BASE_URL}/`, { waitUntil: 'networkidle' });
    const results = await buildAxeBuilder(page).analyze();
    expect(results.violations).toEqual([]);
  });
});
