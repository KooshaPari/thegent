/**
 * i18n helper for the Astro landing docsite.
 *
 * Loads the per-locale JSON dictionary from src/i18n/{locale}.json and exposes
 * a `t(key)` function. Works in both Astro frontmatter (server) and <script>
 * client code (via the globalThis bridge below).
 *
 * Design notes:
 *   - Single-source-of-truth: the locale JSONs live in src/i18n/, mirroring
 *     OmniRoute-3rd's src/i18n/messages/ convention.
 *   - Missing keys fall back to the English base locale, then to the key
 *     literal (so the UI never crashes and the missing key is visible).
 *   - The `useTranslations` factory is bound to a specific locale so Astro
 *     frontmatter can call `const t = useTranslations(locale); t("nav.home")`
 *     without re-deriving the locale on every call.
 */

import en from '../i18n/en.json';
import es from '../i18n/es.json';
import type { Locale } from './rtl';

export type { Locale } from './rtl';

export const LOCALES: readonly Locale[] = ['en', 'es'] as const;
export const DEFAULT_LOCALE: Locale = 'en';

const DICTIONARIES: Record<Locale, Record<string, unknown>> = {
  en: en as Record<string, unknown>,
  es: es as Record<string, unknown>,
};

/**
 * Look up a nested key like "a11y.skipToContent" in a dictionary.
 * Returns the key itself if not found (or the fallback if provided).
 */
function lookup(dict: Record<string, unknown>, key: string): string | undefined {
  const segments = key.split('.');
  let current: unknown = dict;
  for (const segment of segments) {
    if (current && typeof current === 'object' && segment in (current as Record<string, unknown>)) {
      current = (current as Record<string, unknown>)[segment];
    } else {
      return undefined;
    }
  }
  return typeof current === 'string' ? current : undefined;
}

export type TranslationKey =
  | 'site.title'
  | 'site.description'
  | 'site.tagline'
  | 'nav.home'
  | 'nav.guide'
  | 'nav.api'
  | 'nav.qa'
  | 'nav.blog'
  | 'nav.changelog'
  | 'a11y.skipToContent'
  | 'a11y.localeSwitcher'
  | 'a11y.openMenu'
  | 'a11y.closeMenu'
  | 'a11y.externalLink'
  | 'a11y.codeBlock'
  | 'a11y.loading'
  | 'a11y.errorBoundary'
  | 'home.hero.title'
  | 'home.hero.subtitle'
  | 'home.hero.cta.primary'
  | 'home.hero.cta.secondary'
  | 'home.features.title'
  | 'guide.title'
  | 'guide.intro'
  | 'api.title'
  | 'api.intro'
  | 'api.search'
  | 'qa.title'
  | 'qa.status'
  | 'footer.rights'
  | 'errors.notFound'
  | 'errors.serverError'
  | 'errors.tryAgain'
  | string; // allow free-form keys from non-Astro callers

export interface Translator {
  (key: TranslationKey, fallback?: string): string;
}

export function useTranslations(locale: Locale): Translator {
  const dict = DICTIONARIES[locale] ?? DICTIONARIES[DEFAULT_LOCALE];
  const base = DICTIONARIES[DEFAULT_LOCALE];
  return (key: TranslationKey, fallback?: string): string => {
    const value = lookup(dict, key) ?? lookup(base, key) ?? fallback ?? key;
    return value;
  };
}

/**
 * Validate that two locale dictionaries have the same key set. Returns a
 * report consumed by check-i18n-keys.mjs.
 */
export function diffLocales(a: Locale, b: Locale): {
  onlyInA: string[];
  onlyInB: string[];
} {
  const keysA = new Set(Object.keys(DICTIONARIES[a] ?? {}));
  const keysB = new Set(Object.keys(DICTIONARIES[b] ?? {}));
  return {
    onlyInA: [...keysA].filter((k) => !keysB.has(k)),
    onlyInB: [...keysB].filter((k) => !keysA.has(k)),
  };
}

/**
 * Bridge for client-side scripts. The Astro frontmatter calls
 * `attachTranslatorToWindow(locale)` in a top-level <script> tag so that
 * inline client scripts can call `window.__thegentT("nav.home")`.
 */
export function attachTranslatorToWindow(locale: Locale): void {
  if (typeof globalThis === 'undefined') return;
  const t = useTranslations(locale);
  (globalThis as unknown as { __thegentT?: Translator }).__thegentT = t;
}
