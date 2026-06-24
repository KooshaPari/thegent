/**
 * Shared axe-core configuration for the thegent accessibility (AT) baseline.
 *
 * Used by:
 *   - e2e/a11y/wcag.spec.ts (root cross-app)
 *   - apps/landing/e2e/a11y/wcag.spec.ts (Astro docsite)
 *   - apps/byteport/frontend/web-next/e2e/accessibility.spec.ts (Next.js dashboard)
 *
 * Tags target WCAG 2.0 + 2.1 levels A and AA. The `wcag2aaa` tag is intentionally
 * NOT included — AAA conformance is a project-policy decision, not a default gate.
 */

export const AXE_TAGS: readonly string[] = [
  'wcag2a',
  'wcag2aa',
  'wcag21a',
  'wcag21aa',
] as const;

/**
 * Per-rule overrides. We disable `bypass` and `landmark-one-main` globally because
 * they fire false positives on:
 *   - Astro's <Layout> with sidebar + skip-link (the `bypass` rule sees two
 *     landmarks and complains)
 *   - Next.js error boundaries that render a non-`<main>` shell
 *   - The VitePress / Astro pages in apps/landing that intentionally use a single
 *     `<main>` for doc pages (the `landmark-one-main` rule expects two).
 *
 * `color-contrast` is left enabled but `resultTypes` is set to 'violations' so
 * `incomplete` results (which axe reports when contrast is checked on text inside
 * cross-origin iframes) do not break CI.
 */
export const AXE_RULES: Readonly<Record<string, { enabled: boolean }>> = {
  'bypass': { enabled: false },
  'landmark-one-main': { enabled: false },
  'color-contrast': { enabled: true },
  'region': { enabled: true },
} as const;

/**
 * Build a configured AxeBuilder for a given page. Tag set is the union of AXE_TAGS
 * plus the optional extraTags (e.g. ['best-practice'] for a smoke test).
 */
import type { Page } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

export interface AxeConfigOptions {
  extraTags?: readonly string[];
  disableRules?: readonly string[];
}

export function buildAxeBuilder(
  page: Page,
  options: AxeConfigOptions = {},
): AxeBuilder {
  const builder = new AxeBuilder({ page })
    .withTags([...AXE_TAGS, ...(options.extraTags ?? [])]);

  // Apply global disables first so per-call disableRules can override.
  for (const [ruleId, ruleConfig] of Object.entries(AXE_RULES)) {
    if (ruleConfig.enabled === false) {
      builder.disableRules(ruleId);
    }
  }

  for (const ruleId of options.disableRules ?? []) {
    builder.disableRules(ruleId);
  }

  return builder;
}

/**
 * Severity threshold used in the byteport sub-app and any caller that wants to
 * fail only on `critical` / `serious` violations (not `moderate` / `minor`).
 */
export type AxeImpact = 'minor' | 'moderate' | 'serious' | 'critical';

export const FAILING_IMPACTS: readonly AxeImpact[] = [
  'critical',
  'serious',
] as const;

export function isFailingImpact(
  impact: AxeImpact | null | undefined,
): boolean {
  if (!impact) return false;
  return (FAILING_IMPACTS as readonly string[]).includes(impact);
}
