export function createSiteMeta({ base = '/' } = {}) {
  return {
    base,
    title: 'Phenotype Workspace',
    description: 'Phenotype workspace documentation hub',
    themeConfig: {
      nav: [
        { text: 'Home', link: base || '/' },
        { text: 'AGENTS', link: '/AGENTS' },
        { text: 'Projects', link: '/projects' },
      ],
    },
  }
}
