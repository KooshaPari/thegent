import type { Plugin } from 'markdown-it'

/**
 * Cross-project links plugin for VitePress
 *
 * Allows linking to other projects using the syntax: ~project-name:/path/to/page.md
 *
 * Usage in markdown:
 *   ~my-other-project:/docs/getting-started.md
 *
 * This will resolve to the configured base URL for that project.
 */

interface ProjectConfig {
  base: string
  docsDir?: string
}

interface CrossProjectLinksOptions {
  projects: Record<string, string | ProjectConfig>
  defaultDocsDir?: string
}

function resolveProjectUrl(
  project: string,
  path: string,
  options: CrossProjectLinksOptions
): string {
  const projectConfig = options.projects[project]

  if (!projectConfig) {
    console.warn(`Cross-project link: project "${project}" not found`)
    return path
  }

  const base = typeof projectConfig === 'string' ? projectConfig : projectConfig.base
  const docsDir = typeof projectConfig === 'string'
    ? (options.defaultDocsDir || '/docs')
    : (projectConfig.docsDir || '/docs')

  // Normalize the path
  const normalizedPath = path.startsWith('/') ? path : `/${path}`

  return `${base}${docsDir}${normalizedPath}`
}

export const crossProjectLinks: Plugin = (md) => {
  const options = md.options.crossProjectLinks || {}

  // Match ~project:path pattern
  const pattern = /~([a-zA-Z0-9_-]+):(\/[^ \n]+)/g

  md.core.ruler.push('cross_project_links', (state) => {
    for (const token of state.tokens) {
      if (token.type === 'inline') {
        for (const child of token.children || []) {
          if (child.type === 'text' || child.type === 'link_open') {
            const content = child.content || child.attrGet('href') || ''

            if (content.includes('~')) {
              const updated = content.replace(pattern, (_match, project, path) => {
                return resolveProjectUrl(project, path, options)
              })

              if (child.type === 'text') {
                child.content = updated
              } else if (child.type === 'link_open') {
                child.attrSet('href', updated)
              }
            }
          }
        }
      }
    }
  })
}

// Helper function to configure the plugin with project mappings
export function createCrossProjectLinks(
  projects: Record<string, string | ProjectConfig>,
  defaultDocsDir = '/docs'
) {
  return {
    crossProjectLinks: { projects, defaultDocsDir }
  }
}
