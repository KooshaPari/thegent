import type MarkdownIt from 'markdown-it'
import type { RuleBlock } from 'markdown-it/lib/parser_block'
import { ContentTabs } from '../theme/components/ContentTabs.vue'

/**
 * Parse tab definitions from markdown content
 * 
 * Expected format:
 * ::: tabs
 * ::: tab python
 * ```python
 * print("hello")
 * ```
 * :::
 * ::: tab javascript
 * ```javascript
 * console.log("hello")
 * ```
 * :::
 * :::
 */
function parseTabsContent(content: string): { tabs: Array<{id: string, label: string, content: string}> } {
  const tabs: Array<{id: string, label: string, content: string}> = []
  
  // Split by ::: tab pattern
  const tabRegex = /:::\s*tab\s+(\S+)([\s\S]*?):::/g
  let match
  
  while ((match = tabRegex.exec(content)) !== null) {
    const id = match[1]
    const tabContent = match[2].trim()
    tabs.push({ id, label: id, content: tabContent })
  }
  
  return { tabs }
}

export function contentTabsPlugin(md: MarkdownIt) {
  // Create custom container for tabs
  const tabsContainer: RuleBlock = (state, startLine, endLine, silent) => {
    const start = state.bMarks[startLine] + state.tShift[startLine]
    const max = state.eMarks[endLine]
    const line = state.src.slice(start, max)
    
    // Check for ::: tabs opening
    if (!line.match(/^:::\s*tabs\s*$/)) {
      return false
    }
    
    if (silent) {
      return true
    }
    
    // Find the closing :::
    let closingLine = -1
    let contentStart = startLine + 1
    
    for (let i = startLine + 1; i <= endLine; i++) {
      const lineStart = state.bMarks[i] + state.tShift[i]
      const lineContent = state.src.slice(lineStart, state.eMarks[i])
      
      if (lineContent.match(/^:::\s*$/)) {
        closingLine = i
        break
      }
    }
    
    if (closingLine === -1) {
      return false
    }
    
    // Get the content between opening and closing
    const rawContent = state.src.slice(
      state.bMarks[contentStart], 
      state.bMarks[closingLine]
    )
    
    // Parse tab content
    const { tabs } = parseTabsContent(rawContent)
    
    // Generate a unique ID for this tabs instance
    const tabsId = `tabs-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
    
    // Build the component HTML
    const tabsHtml = []
    tabsHtml.push(`<div class="content-tabs-wrapper" data-tabs-id="${tabsId}">`)
    tabsHtml.push(`<ContentTabs :tabs='${JSON.stringify(tabs)}'>`)
    
    tabs.forEach((tab, index) => {
      const slotName = `tab-${tab.id}`
      tabsHtml.push(`<template #${slotName}>`)
      // Process markdown content for each tab
      const tempState = state.md.parse(tab.content, {})
      tabsHtml.push(state.md.renderer.render(tempState, {}, {}))
      tabsHtml.push(`</template>`)
    })
    
    tabsHtml.push('</ContentTabs>')
    tabsHtml.push('</div>')
    
    // Create token for the opening tag
    const token = state.push('tabs_container_open', 'div', 1)
    token.attrSet('class', 'content-tabs-wrapper')
    token.attrSet('data-tabs-id', tabsId)
    token.map = [startLine, closingLine]
    
    // We need to render the component inline - use a simpler approach
    // Just mark the section with special markers that Vue can pick up
    const markerToken = state.push('tabs_marker', '', 0)
    markerToken.content = JSON.stringify({ tabs, tabsId })
    markerToken.map = [startLine, closingLine]
    
    return true
  }
  
  // Add the plugin
  md.block.ruler.after('fence', 'content_tabs', tabsContainer, {
    alt: ['paragraph', 'reference', 'blockquote', 'list']
  })
  
  // Custom renderer for the marker
  md.renderer.rules.tabs_marker = (tokens, idx, options, env, self) => {
    const token = tokens[idx]
    try {
      const data = JSON.parse(token.content)
      const tabs = data.tabs.map((t: {id: string, label: string}) => ({
        id: t.id,
        label: t.label.charAt(0).toUpperCase() + t.label.slice(1)
      }))
      
      // Generate the Vue component HTML with pre-rendered content
      let html = `<div class="content-tabs-wrapper" data-tabs-id="${data.tabsId}">`
      html += `<div class="content-tabs" data-tabs='${JSON.stringify(tabs)}'>`
      html += `<div class="tab-headers">`
      
      tabs.forEach((tab: {id: string, label: string}, idx: number) => {
        const active = idx === 0 ? 'active' : ''
        html += `<button class="tab-header ${active}" data-tab="${tab.id}">${tab.label}</button>`
      })
      
      html += `</div>`
      html += `<div class="tab-bodies">`
      
      data.tabs.forEach((tab: {id: string, label: string, content: string}, idx: number) => {
        const display = idx === 0 ? 'block' : 'none'
        html += `<div class="tab-body" data-tab="${tab.id}" style="display: ${display}">`
        html += tab.content
        html += `</div>`
      })
      
      html += `</div></div></div>`
      
      return html
    } catch (e) {
      return `<div class="content-tabs-error">Error parsing tabs</div>`
    }
  }
}

// Client-side script to initialize tab behavior
export const tabsClientScript = `
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.content-tabs-wrapper').forEach(wrapper => {
    const headers = wrapper.querySelectorAll('.tab-header')
    const bodies = wrapper.querySelectorAll('.tab-body')
    
    headers.forEach(header => {
      header.addEventListener('click', () => {
        const tabId = header.getAttribute('data-tab')
        
        // Update active state
        headers.forEach(h => h.classList.remove('active'))
        header.classList.add('active')
        
        // Show/hide bodies
        bodies.forEach(body => {
          if (body.getAttribute('data-tab') === tabId) {
            body.style.display = 'block'
          } else {
            body.style.display = 'none'
          }
        })
      })
      
      header.addEventListener('keydown', (e) => {
        const currentIndex = Array.from(headers).indexOf(header)
        
        if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
          e.preventDefault()
          const nextIndex = (currentIndex + 1) % headers.length
          headers[nextIndex].click()
          headers[nextIndex].focus()
        } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
          e.preventDefault()
          const prevIndex = (currentIndex - 1 + headers.length) % headers.length
          headers[prevIndex].click()
          headers[prevIndex].focus()
        } else if (e.key === 'Home') {
          e.preventDefault()
          headers[0].click()
          headers[0].focus()
        } else if (e.key === 'End') {
          e.preventDefault()
          headers[headers.length - 1].click()
          headers[headers.length - 1].focus()
        }
      })
    })
  })
})
`
