// wraps: vitepress-plugin-mermaid ^2.0.17
import { withMermaid } from 'vitepress-plugin-mermaid'

/**
 * Wrap a VitePress config with Mermaid diagram support.
 * Usage: replace `defineConfig({...})` with `withMermaid({...})` in config.ts
 */
export { withMermaid }

export const mermaidConfig = {
  theme: 'dark',
  themeVariables: {
    fontFamily: 'JetBrains Mono, monospace',
    fontSize: '13px',
  },
  flowchart: {
    htmlLabels: true,
    curve: 'basis',
  },
  sequence: {
    showSequenceNumbers: false,
  },
}
