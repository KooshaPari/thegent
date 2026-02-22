import { readFileSync } from 'fs'
import { resolve } from 'path'

export default {
  load() {
    const dataPath = resolve(__dirname, '../data/kb-graph.json')
    try {
      return JSON.parse(readFileSync(dataPath, 'utf-8'))
    } catch {
      return { nodes: [], edges: [] }
    }
  }
}
