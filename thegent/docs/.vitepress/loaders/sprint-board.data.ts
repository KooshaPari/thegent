import { readFileSync } from 'fs'
import { resolve } from 'path'

export default {
  load() {
    const dataPath = resolve(__dirname, '../data/sprint-board.json')
    try {
      return JSON.parse(readFileSync(dataPath, 'utf-8'))
    } catch {
      return []
    }
  }
}
