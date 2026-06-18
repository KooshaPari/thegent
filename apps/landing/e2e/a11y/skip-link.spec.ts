/**
 * Skip-link keyboard test for the Astro landing docsite.
 *
 * Verifies the AT2 acceptance criteria from at-baseline-spec.json §AT2:
 *   1. The skip-link is the FIRST focusable element on every page.
 *   2. Pressing Tab on a cold page load focuses the skip-link.
 *   3. Activating the skip-link (Enter) moves focus to <main id="main">.
 *   4. <main> is programmatically focusable (has tabindex="-1").
 *   5. The skip-link is visually hidden until focused.
 *
 * The page enumeration reuses the same import.meta.glob pattern as wcag.spec.ts
 * so the test automatically covers new pages.
 */

import { test, expect, type Page } from '@playwright/test';

const BASE_URL = process.env.PLAYWRIGHT_BASE_URL ?? 'http://localhost:4321';

const pageModules = import.meta.glob<true, string, unknown>(
  '../src/pages/**/*.astro',
);
const pagePaths = Object.keys(pageModules)
  .map((p) => p.replace(/^\.\.\/src\/pages/, '').replace(/\.astro$/, ''))
  .filter((p) => !p.includes('['))
  .map((p) => (p === '/index' ? '/' : p));

async function pressTabUntil(
  page: Page,
  predicate: (el: { tag: string; className: string; text: string }) => boolean,
  maxStops = 25,
) {
  for (let i = 0; i < maxStops; i++) {
    await page.keyboard.press('Tab');
    const el = await page.evaluate(() => {
      const a = document.activeElement as HTMLElement | null;
      if (!a) return null;
      return {
        tag: a.tagName,
        className: a.className ?? '',
        text: (a.textContent ?? '').trim().slice(0, 80),
      };
    });
    if (el && predicate(el)) return { stop: i, el };
  }
  return { stop: -1, el: null };
}

test.describe('AT2 — Skip link (Astro landing)', () => {
  for (const route of pagePaths) {
    test(`landing${route}: skip-link is first focusable`, async ({ page }) => {
      await page.goto(`${BASE_URL}${route}`.replace(/\/+$/, '/'), {
        waitUntil: 'domcontentloaded',
      });

      // Move focus to the document so the next Tab starts from the top.
      await page.evaluate(() => {
        (document.activeElement as HTMLElement | null)?.blur();
        document.body.focus();
      });

      // The first Tab should land on the skip-link OR a focusable element
      // with class "skip-link".
      const first = await pressTabUntil(
        page,
        (el) => el.className.includes('skip-link'),
        1,
      );
      expect(
        first.el,
        'first Tab on cold load must focus the skip-link',
      ).not.toBeNull();
      expect(first.el?.text.toLowerCase()).toContain('skip');
    });

    test(`landing${route}: activating skip-link moves focus to <main>`, async ({
      page,
    }) => {
      await page.goto(`${BASE_URL}${route}`.replace(/\/+$/, '/'), {
        waitUntil: 'domcontentloaded',
      });

      // Focus the skip-link directly (faster than Tab cycle).
      await page.locator('a.skip-link').first().focus();
      await page.keyboard.press('Enter');

      const focused = await page.evaluate(() => {
        const a = document.activeElement as HTMLElement | null;
        return { tag: a?.tagName, id: a?.id, tabIndex: a?.tabIndex };
      });
      expect(focused.tag).toBe('MAIN');
      expect(focused.id).toBe('main');
      // tabindex="-1" makes the target programmatically focusable.
      expect(focused.tabIndex).toBe(-1);
    });

    test(`landing${route}: skip-link is visually hidden until focused`, async ({
      page,
    }) => {
      await page.goto(`${BASE_URL}${route}`.replace(/\/+$/, '/'), {
        waitUntil: 'domcontentloaded',
      });
      const link = page.locator('a.skip-link').first();

      // Unfocused: position should be off-screen (left: -10000px).
      const unfocusedBox = await link.boundingBox();
      // boundingBox returns null if the element is fully outside the layout;
      // if it returns a box, it must NOT be visible at the top-left.
      if (unfocusedBox) {
        expect(
          unfocusedBox.x < -1000 || unfocusedBox.y < 0,
          'unfocused skip-link must be off-screen',
        ).toBe(true);
      }

      // Focused: the link becomes fixed at top-left with non-zero size.
      await link.focus();
      const focusedBox = await link.boundingBox();
      expect(focusedBox, 'focused skip-link must have a bounding box').not.toBeNull();
      expect(focusedBox!.x).toBeLessThan(100);
      expect(focusedBox!.y).toBeLessThan(100);
      expect(focusedBox!.width).toBeGreaterThan(40);
    });
  }
});
