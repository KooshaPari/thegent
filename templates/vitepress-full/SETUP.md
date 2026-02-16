# VitePress Docsite Template

A complete, drop-in VitePress template for creating beautiful documentation sites.

## Quick Setup (30 seconds)

1. Copy this template to your project:
   ```bash
   cp -r /path/to/templates/vitepress-full myproject/docs/.vitepress
   ```

2. Update placeholders in config.ts.template:
   - `{{PROJECT_NAME}}` -> "myproject"
   - `{{PROJECT_DESCRIPTION}}` -> "My project description"

3. Install and build:
   ```bash
   cd myproject
   pnpm install
   pnpm docs:build
   ```

4. Open `docs-dist/index.html` in browser!

## Adding to Existing Project

1. Copy `.vitepress/` folder to your `docs/` directory:
   ```bash
   cp -r vitepress-full/* your-project/docs/.vitepress/
   ```

2. Rename template files:
   ```bash
   mv config.ts.template config.ts
   mv package.json.template package.json
   ```

3. Update placeholders in config.ts

4. Install dependencies:
   ```bash
   pnpm install
   ```

5. Build the docs:
   ```bash
   pnpm docs:build
   ```

## Commands

| Command | Description |
|---------|-------------|
| `pnpm docs:dev` | Development server with hot reload |
| `pnpm docs:build` | Build to docs-dist/ |
| `pnpm docs:preview` | Preview built site |

## Template Structure

```
vitepress-full/
├── config.ts.template         # VitePress config (rename to config.ts)
├── package.json.template     # Package.json (rename to package.json)
├── theme/
│   ├── index.ts              # Theme entry point
│   ├── custom.css           # Custom styles
│   └── components/
│       └── Callout.vue       # Callout component
├── plugins/
│   └── cross-project-links.ts # Cross-project link plugin
├── scripts/
│   └── build-docs.sh        # Multi-version build script
├── hooks/
│   └── docs-build.sh        # Pre-commit hook
└── docs/
    └── index.md             # Homepage template
```

## Features Included

- **Local full-text search** - Built-in search functionality
- **Dark/light mode** - Automatic theme switching
- **Callout components** - Tip, warning, danger, note boxes
- **Cross-project links** - Link to other projects with `~project:/path`
- **Pre-commit hook** - Auto-build on git commits
- **Multi-version build** - Build multiple versions simultaneously

## Using Callout Components

Use the `<Callout>` component in your markdown:

```markdown
<Callout type="tip" title="Pro Tip">
  This is a helpful tip!
</Callout>

<Callout type="warning" title="Warning">
  Be careful with this operation.
</Callout>

<Callout type="danger" title="Danger">
  This action cannot be undone!
</Callout>

<Callout type="note" title="Note">
  Additional information.
</Callout>
```

## Cross-Project Links

Link to other documentation projects using the `~project:path` syntax:

```markdown
See the [API docs](~api:/reference/endpoints) for details.
```

Configure project URLs in your config.ts:

```typescript
import { defineConfig } from 'vitepress'
import { crossProjectLinks, createCrossProjectLinks } from './plugins/cross-project-links'

export default defineConfig({
  // ... other config
  markdown: {
    config: (md) => {
      md.use(crossProjectLinks, createCrossProjectLinks({
        api: 'https://docs.yourcompany.com/api',
        frontend: 'https://docs.yourcompany.com/frontend'
      }, '/docs'))
    }
  }
})
```

## Customizing Theme

Edit `theme/custom.css` to change colors:

```css
:root {
  --vp-c-brand-1: #your-brand-color;
  --vp-c-brand-2: #your-secondary-color;
}
```

## Multi-Version Builds

1. Create a `.versions` file:
   ```
   v1.0.0
   v2.0.0
   latest
   ```

2. Run the build script:
   ```bash
   bash scripts/build-docs.sh
   ```

3. Output will be in `docs-dist/v1.0.0/`, `docs-dist/v2.0.0/`, etc.

## Pre-Commit Hook

Install the pre-commit hook to auto-build docs on commit:

```bash
bash hooks/docs-build.sh --install
```

This will modify your `.git/hooks/pre-commit` to build docs automatically.

## Troubleshooting

### Build fails with "command not found"

Make sure to run `pnpm install` first to install vitepress.

### Search not working

Ensure `search: { provider: 'local' }` is set in your themeConfig.

### Custom components not rendering

Make sure the component is registered in `theme/index.ts`.

## License

MIT
