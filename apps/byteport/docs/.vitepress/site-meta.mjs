export function createSiteMeta({ base = '/' } = {}) {
  return {
    base,
    title: 'Documentation',
    description: 'Documentation',
    themeConfig: {
      nav: [
        { text: 'Home', link: base || '/' },
      ],
    },
  }
}
