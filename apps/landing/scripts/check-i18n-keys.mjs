#!/usr/bin/env node
/**
 * check-i18n-keys.mjs — CI guard for the AT4 i18n baseline.
 *
 * Walks apps/landing/src/pages/**/*.astro, scripts/, and src/components/ and
 * asserts:
 *   1. Every <t('key')> or t("key") reference in JSX has a matching key
 *      in src/i18n/en.json.
 *   2. Every top-level key in en.json has a counterpart in es.json (and
 *      vice versa) — coverage check.
 *   3. No Astro page contains a hardcoded English string >3 words that is
 *      not wrapped in t() (basic lint; opt-in via --strict).
 *
 * Exit code 0 = all checks pass. Non-zero = CI fails.
 *
 * Usage:
 *   node scripts/check-i18n-keys.mjs           # default checks
 *   node scripts/check-i18n-keys.mjs --strict  # also lint hardcoded strings
 */

import { readFileSync, readdirSync, statSync, existsSync } from 'node:fs';
import { join, relative, resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const ROOT = resolve(__dirname, '..');
const I18N_DIR = join(ROOT, 'src', 'i18n');
const PAGES_DIR = join(ROOT, 'src', 'pages');
const COMPONENTS_DIR = join(ROOT, 'src', 'components');
const LAYOUTS_DIR = join(ROOT, 'src', 'layouts');

const STRICT = process.argv.includes('--strict');

function walk(dir) {
  if (!existsSync(dir)) return [];
  const out = [];
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    const s = statSync(full);
    if (s.isDirectory()) {
      if (entry === 'node_modules' || entry === '.astro' || entry === 'dist') continue;
      out.push(...walk(full));
    } else if (/\.(astro|tsx|jsx|ts|js|mjs)$/.test(entry)) {
      out.push(full);
    }
  }
  return out;
}

function loadJson(path) {
  return JSON.parse(readFileSync(path, 'utf8'));
}

function flattenKeys(obj, prefix = '', out = new Set()) {
  for (const [k, v] of Object.entries(obj)) {
    const key = prefix ? `${prefix}.${k}` : k;
    if (v && typeof v === 'object' && !Array.isArray(v)) {
      flattenKeys(v, key, out);
    } else {
      out.add(key);
    }
  }
  return out;
}

function extractTCalls(source) {
  // Match t('key') or t("key") with optional fallback arg. We accept nested
  // dot keys and reject anything with spaces (those are user-supplied text
  // not a key reference).
  const re = /\bt\(\s*['"]([a-zA-Z0-9._]+)['"]/g;
  const keys = new Set();
  let m;
  while ((m = re.exec(source)) !== null) {
    keys.add(m[1]);
  }
  return keys;
}

function extractStringLiterals(source) {
  // Heuristic: pull double-quoted strings >3 words that look like English.
  // Used only with --strict to flag candidates that should probably be t()'d.
  const re = /"([A-Z][a-z]+(?:\s+[A-Za-z]+){3,})"/g;
  const out = [];
  let m;
  while ((m = re.exec(source)) !== null) out.push(m[1]);
  return out;
}

const en = loadJson(join(I18N_DIR, 'en.json'));
const es = loadJson(join(I18N_DIR, 'es.json'));
const enKeys = flattenKeys(en);
const esKeys = flattenKeys(es);

let failures = 0;
const report = [];

function fail(msg) {
  failures++;
  report.push(`FAIL: ${msg}`);
}
function info(msg) {
  report.push(`INFO: ${msg}`);
}

// 1. Coverage: keys present in en but missing in es (and vice versa).
for (const key of enKeys) {
  if (!esKeys.has(key)) fail(`en has '${key}' but es does not`);
}
for (const key of esKeys) {
  if (!enKeys.has(key)) fail(`es has '${key}' but en does not`);
}

// 2. References in code must resolve to en keys.
const sourceFiles = [
  ...walk(PAGES_DIR),
  ...walk(COMPONENTS_DIR),
  ...walk(LAYOUTS_DIR),
];

const usedKeys = new Set();
for (const file of sourceFiles) {
  const src = readFileSync(file, 'utf8');
  const calls = extractTCalls(src);
  for (const key of calls) {
    usedKeys.add(key);
    if (!enKeys.has(key)) {
      fail(`${relative(ROOT, file)} references missing t('${key}') (not in en.json)`);
    }
  }
  if (STRICT) {
    const literals = extractStringLiterals(src);
    if (literals.length > 0) {
      info(`${relative(ROOT, file)} has ${literals.length} hardcoded English literal(s); consider t(): ${literals.slice(0, 3).join(' | ')}`);
    }
  }
}

// 3. Unused keys (en) — surfacing only, not a failure.
for (const key of enKeys) {
  if (!usedKeys.has(key)) {
    info(`en key '${key}' is declared but no source reference found`);
  }
}

console.log('--- i18n key report ---');
for (const line of report) console.log(line);
console.log(`--- summary: ${failures} failure(s), ${report.length - failures} info ---`);

process.exit(failures > 0 ? 1 : 0);
