# README

Source: docs/demos/README.md

---

# Demo Scripts for VitePress Documentation

This directory contains demo scripts that are automatically converted to GIFs for the VitePress documentation.

## Structure

- `cli/` - VHS tape files (`.tape`) for terminal recordings
- `web/` - Playwright test scripts (`.ts`) for browser recordings

## Usage

Run the generation script:

```
./scripts/generate-demo-gifs.sh
```

Generated GIFs will be placed in `docs/public/assets/demos/` and can be referenced in documentation using the `<DemoGif>` component:

```

```

## VHS Tape Format

Create `.tape` files in `cli/` directory:

```
Output cli-demo.gif
Set FontSize 14
Set Width 1200
Set Height 600
Set Theme "Catppuccin Mocha"

Type "thegent run codex 'Hello world'"
Sleep 500ms
Enter
Sleep 2s
```

## Playwright Scripts

Create `.ts` files in `web/` directory:

```
import { test } from '@playwright/test'

test('demo', async ({ page }) => {
  await page.goto('https://example.com')
  // ... record interactions
})
```

---
