// Auto-generated VitePress data loader for audit log
// Run: uv run docs export to refresh
import { readFileSync } from 'fs'
import { resolve } from 'path'

export default {
  load() {
    const dataPath = resolve(__dirname, '../data/audit-log.json')
    try {
      return JSON.parse(readFileSync(dataPath, 'utf-8'))
    } catch {
      return []
    }
  }
}
