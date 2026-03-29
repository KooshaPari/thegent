import type MarkdownIt from 'markdown-it'

export function imageOptimizationPlugin(md: MarkdownIt) {
  const defaultRenderer =
    md.renderer.rules.image ??
    ((tokens, idx, options, env, self) => self.renderToken(tokens, idx, options, env, self))

  md.renderer.rules.image = (tokens, idx, options, env, self) => {
    const token = tokens[idx]

    if (!token.attrs) {
      token.attrs = []
    }

    if (!token.attrs.find(([name]) => name === 'loading')) {
      token.attrs.push(['loading', 'lazy'])
    }

    if (!token.attrs.find(([name]) => name === 'decoding')) {
      token.attrs.push(['decoding', 'async'])
    }

    return defaultRenderer(tokens, idx, options, env, self)
  }
}
