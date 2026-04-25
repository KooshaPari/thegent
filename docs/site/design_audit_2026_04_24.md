# Design Audit: thegent/docs/site
**Date:** 2026-04-24 | **Auditor:** Claude (Haiku 4.5) | **Status:** No fixes applied

---

## Audit Health Score

| # | Dimension | Score | Key Finding |
|---|-----------|-------|-------------|
| 1 | Accessibility | 3 | VitePress default semantic HTML + ARIA decent, but color contrast borderline on code blocks |
| 2 | Performance | 3 | Good: lazy loading built-in, no layout thrash detected; minor: inline scripts not deferred |
| 3 | Responsive Design | 4 | Excellent: VitePress default responsive, mobile-friendly sidebar, fluid containers |
| 4 | Theming | 2 | Light/dark mode toggle present but default VitePress theme; minimal customization |
| 5 | Anti-Patterns | 3 | Mostly clean; minimal decorative elements, functional focus dominates |
| **Total** | | **15/20** | **Good (address weak dimensions)** |

---

## Anti-Patterns Verdict

**Minimal AI slop:**
- No decorative gradients, blur effects, or glowing accents
- Functional design: focus on content clarity over visual novelty
- Default VitePress aesthetic is generic but intentional

**Verdict:** Not AI-generated. Standard VitePress documentation aesthetic — safe, accessible, but lacks visual personality.

---

## Executive Summary

- **Audit Health Score:** 15/20 (Good — address weak dimensions)
- **Critical Issues:** P0 (0) | P1 (2) | P2 (3) | P3 (2)
- **Top Issues:**
  1. Theming is default VitePress — no Phenotype brand colors integrated
  2. Code block contrast could be higher in dark mode
  3. Typography scale underutilizes hierarchy (monospace for code is good, but body font lacks personality)
- **Recommended Path:** Colorize (brand colors) → normalize (design tokens) → polish (typeset)

---

## Detailed Findings by Severity

### P1 Major

**[P1] No Phenotype brand color integration**
- **Category:** Theming
- **Location:** .vitepress/config.ts, custom CSS
- **Impact:** Site uses generic VitePress blues/grays. Doesn't reflect Phenotype org identity or thegent collection colors.
- **Recommendation:** Override VitePress theme colors with collection accent (thegent specific) or org neutrals. See brand_playbook.md for palette.
- **Suggested command:** `/colorize` (to apply Phenotype brand colors)

**[P1] Code block contrast in dark mode**
- **Category:** Accessibility
- **Location:** Code blocks throughout documentation
- **Impact:** Syntax highlighting colors (likely default Prism theme) may not meet WCAG AA contrast (4.5:1) for comments or strings in dark mode.
- **Recommendation:** Test code block colors with contrast checker; apply custom Prism theme if needed.
- **Suggested command:** `/normalize` (to verify/fix contrast)

### P2 Minor

**[P2] Typography lacks distinctive personality**
- **Category:** Typography
- **Location:** .vitepress/config.ts, custom CSS
- **Impact:** Body font is system-ui (safe, generic). Documentation sites like this benefit from a custom typeface (e.g., Inter, Merriweather for serif docs).
- **Recommendation:** Add custom font (either web font or system fallback chains) to intro sections; keep monospace for code.
- **Suggested command:** `/typeset` (to improve typography hierarchy)

**[P2] Sidebar navigation lacks visual hierarchy**
- **Category:** Layout / Spacing
- **Location:** .vitepress sidebar config
- **Impact:** All items feel equal weight. No visual distinction between sections, subsections, or active items beyond color.
- **Recommendation:** Use bolder font weight, increased spacing, or subtle background tints to create hierarchy.
- **Suggested command:** `/arrange` (to improve spacing and visual rhythm)

**[P2] Search box styling is minimal**
- **Category:** Interaction
- **Location:** VitePress default search
- **Impact:** Local search uses default styling. Border and focus states are subtle; could be more discoverable.
- **Recommendation:** Increase border visibility, add icon, improve focus ring.
- **Suggested command:** `/polish` (to enhance search box feedback)

### P3 Polish

**[P3] Edit link visibility**
- **Category:** Interaction
- **Location:** .vitepress config (editLink)
- **Impact:** Edit link appears at bottom of pages in small text. Not prominent, but good for docs.
- **Recommendation:** Consider adding at top-right or in a floating action. Current placement is fine; low priority.
- **Suggested command:** N/A (already functional)

**[P3] Last updated timestamp**
- **Category:** Content / Metadata
- **Location:** Footer
- **Impact:** Shows when docs were last modified. Useful for readers but could be styled more prominently.
- **Recommendation:** Current styling is adequate; low priority unless prominence is needed.
- **Suggested command:** N/A

---

## Patterns & Systemic Issues

### VitePress Default Theme Not Customized
**Systemic Issue:** Site relies entirely on VitePress defaults for colors, fonts, spacing.
- **Pattern:** No custom CSS overrides detected; config is minimal
- **Impact:** Site blends into thousands of other VitePress docs; no Phenotype identity
- **Recommendation:** Create `custom.css` in `.vitepress` directory with Phenotype brand colors and typography

### No Distinctive Visual Branding
**Systemic Issue:** Could be any technical documentation site.
- **Pattern:** Blue/gray palette, system font, standard layout
- **Impact:** Misses opportunity to reinforce thegent + Phenotype ecosystem identity
- **Recommendation:** See `/colorize` and `/typeset` paths

---

## Positive Findings

✓ **Excellent semantic HTML structure** — VitePress defaults to proper heading hierarchy (h1 > h2 > h3), proper lists, proper code blocks.

✓ **Mobile responsive by default** — Sidebar collapses, content reflows, touch-friendly on all viewports.

✓ **Good documentation organization** — Clear section structure (Guide, Operations, Reference, API) makes navigation intuitive.

✓ **Code blocks are properly formatted** — Monospace typography, syntax highlighting, line numbers available. Good UX for technical docs.

✓ **Local search is fast** — Using Algolia alternative (local provider); no external dependencies.

---

## Recommended Actions

1. **[P1] `/colorize`** — Apply Phenotype brand colors to VitePress theme (accent colors from collections.json)
2. **[P1] `/normalize`** — Test and fix code block contrast in dark mode; ensure WCAG AA on syntax colors
3. **[P2] `/typeset`** — Introduce distinctive font for headings or intro sections (replace system-ui for visual identity)
4. **[P2] `/arrange`** — Enhance sidebar hierarchy with better spacing and visual weight variation
5. **[P2] `/polish`** — Improve search box focus states and visual prominence
6. **Final step:** `/audit` to verify score improvement

---

## Notes

- **VitePress version:** Check `package.json` for version; ensure latest for best defaults
- **Custom CSS location:** `.vitepress/theme/custom.css` or `.vitepress/theme/index.ts`
- **Brand colors:** Reference `/repos/docs/marketing/brand_playbook.md` for official Phenotype palette
- **No performance blockers detected** — focus is on aesthetic alignment with org brand

