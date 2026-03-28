# Locale and Worklog Consolidation Audit

Generated: 2026-03-28T08:21:36.615Z

| repo | vitepress | config | expected locales | locale dirs | missing | orphan locale dirs | worklog status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| agent-devops-setups | false |  | none | none | none | none | docs/sessions(1) |
| bifrost-extensions | true | bifrost-extensions/docs/.vitepress/config.mts | none | none | none | none | docs/sessions(1) |
| cliproxyapi-plusplus | true | cliproxyapi-plusplus/docs/.vitepress/config.ts | none | none | none | none | absent |
| forgecode | true | forgecode/docs/.vitepress/config.mts | none | none | none | none | WORKLOG.md only |
| heliosApp | true | heliosApp/docs/.vitepress/config.ts | none | none | none | none | WORKLOG+sessions(0) |
| heliosCLI | true | heliosCLI/docs/.vitepress/config.ts | none | none | none | none | docs/sessions(0) |
| phench | true | phench/docs/.vitepress/config.mts | none | none | none | none | WORKLOG+sessions(1) |
| phenotype-gauge | true | phenotype-gauge/docs/.vitepress/config.mts | none | none | none | none | absent |
| phenotype-go-kit | true | phenotype-go-kit/docs/.vitepress/config.mts | none | none | none | none | WORKLOG.md only |
| phenotype-infrakit | true | phenotype-infrakit/docs/.vitepress/config.mts | none | none | none | none | WORKLOG+sessions(1) |
| phenotype-nexus | true | phenotype-nexus/docs/.vitepress/config.mts | root, zh-CN, zh-TW, fa, fa-Latn | fa, fa-Latn, zh-CN, zh-TW | none | none | absent |
| phenotype-shared | true | phenotype-shared/docs/.vitepress/config.mts | none | none | none | none | WORKLOG.md only |
| phenotype-xdd | true | phenotype-xdd/docs/.vitepress/config.mts | root, zh-CN, zh-TW, fa, fa-Latn | fa, fa-Latn, zh-CN, zh-TW | none | none | absent |
| phenotypeActions | true | phenotypeActions/docs/.vitepress/config.mts | none | none | none | none | docs/sessions(1) |
| policy-contract | true | policy-contract/docs/.vitepress/config.mts | none | none | none | none | docs/sessions(0) |
| profiler | true | profiler/docs/.vitepress/config.ts | none | none | none | none | WORKLOG.md only |
| tokenledger-wt | true | tokenledger-wt/docs/.vitepress/config.ts | none | none | none | none | docs/sessions(1) |
| trace | true | trace/docs/.vitepress/config.ts | none | none | none | none | docs/sessions(1) |
| trash-cli | true | trash-cli/docs/.vitepress/config.mts | none | none | none | none | docs/sessions(1) |

## Recent updates

- Added `docs/.vitepress/plugins/image-optimization.ts` and wired it into `docs/.vitepress/config.ts` so markdown `<img>` renderings automatically get `loading="lazy"` and `decoding="async"` when the attributes were missing.
- Introduced `scripts/docs-verify-media.js` plus `package.json` script and Taskfile task to rebuild the dist folder and confirm built HTML includes lazy-loaded images alongside existing `<video controls>` nodes, and added the same verification step to `.github/workflows/docs.yml`.
