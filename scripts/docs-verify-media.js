#!/usr/bin/env bun
import { promises as fs } from 'node:fs'
import { join } from 'node:path'

const distDir = process.env.DOCS_DIST ?? join('docs', '.vitepress', 'dist')

async function gatherHtmlFiles(dir, files = []) {
  const entries = await fs.readdir(dir, { withFileTypes: true })
  for (const entry of entries) {
    const target = join(dir, entry.name)
    if (entry.isDirectory()) {
      await gatherHtmlFiles(target, files)
    } else if (entry.isFile() && entry.name.endsWith('.html')) {
      files.push(target)
    }
  }
  return files
}

try {
  const htmlFiles = await gatherHtmlFiles(distDir)

  if (!htmlFiles.length) {
    throw new Error(`No HTML files found under ${distDir}. Did the build succeed?`)
  }

  let lazyFound = false
  let decodingFound = false
  let videoFound = false

  for (const file of htmlFiles) {
    const contents = await fs.readFile(file, 'utf8')

    if (!lazyFound && contents.includes('loading="lazy"')) {
      lazyFound = true
    }

    if (!decodingFound && contents.includes('decoding="async"')) {
      decodingFound = true
    }

    if (!videoFound && /<video[^>]*controls/i.test(contents)) {
      videoFound = true
    }

    if (lazyFound && decodingFound && videoFound) {
      break
    }
  }

  if (!lazyFound || !decodingFound) {
    throw new Error(
      'Docsite build does not contain markdown images with both loading="lazy" and decoding="async"; image-optimization plugin may have regressed.'
    )
  }

  if (!videoFound) {
    throw new Error('Docsite build does not include any <video controls> output; verify other media rendering is still present.')
  }

  console.log('Docs media verification passed (lazy images + video controls present).')
} catch (error) {
  console.error(error)
  process.exit(1)
}
