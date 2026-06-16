/**
 * RTL helper for the Astro landing docsite.
 *
 * Single source of truth for the RTL locale set. Used by:
 *   - BaseLayout.astro to set <html dir>
 *   - i18n.ts to type the Locale union
 *   - the design system to flip icon classes
 *
 * The locale set mirrors OmniRoute-3rd's config/i18n.json.rtl array so
 * scripts that target both repos can share the same set.
 */

export const RTL_LOCALES: readonly string[] = ['ar', 'he', 'fa', 'ur'] as const;

export const SUPPORTED_LOCALES: readonly Locale[] = ['en', 'es'] as const;
export type Locale = 'en' | 'es' | (typeof RTL_LOCALES)[number];

export function isRtl(locale: string | null | undefined): boolean {
  if (!locale) return false;
  return (RTL_LOCALES as readonly string[]).includes(locale);
}

export function dirFor(locale: string | null | undefined): 'ltr' | 'rtl' {
  return isRtl(locale) ? 'rtl' : 'ltr';
}

/**
 * Apply the correct inline-start / inline-end class names for a logical
 * direction. Used by components that need to override the default flex
 * direction in RTL contexts.
 */
export function logicalStartEnd(locale: string | null | undefined): {
  startClass: string;
  endClass: string;
} {
  return isRtl(locale)
    ? { startClass: 'me-2', endClass: 'ms-2' }
    : { startClass: 'ms-2', endClass: 'me-2' };
}
