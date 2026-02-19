import DefaultTheme from 'vitepress/theme'
import Layout from './Layout.vue'
import Callout from './components/Callout.vue'
import DemoGif from './components/DemoGif.vue'
import CodePlayground from './components/CodePlayground.vue'
import ContentTabs from './components/ContentTabs.vue'
import NavTabs from './components/NavTabs.vue'
import StickyHeader from './components/StickyHeader.vue'
import StickySidebar from './components/StickySidebar.vue'
import ToastContainer from './components/ToastContainer.vue'
import LoadingSpinner from './components/LoadingSpinner.vue'
import BackToTop from './components/BackToTop.vue'
import Breadcrumb from './components/Breadcrumb.vue'
import Tooltip from './components/Tooltip.vue'
import CodeAnnotation from './components/CodeAnnotation.vue'
import OpenAPI from './components/OpenAPI.vue'
import './custom.css'

// Client-side script for tabs behavior
const tabsClientScript = `
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.content-tabs-wrapper').forEach(wrapper => {
    const headers = wrapper.querySelectorAll('.tab-header')
    const bodies = wrapper.querySelectorAll('.tab-body')
    
    if (headers.length === 0) return
    
    headers.forEach(header => {
      header.addEventListener('click', () => {
        const tabId = header.getAttribute('data-tab')
        
        headers.forEach(h => h.classList.remove('active'))
        header.classList.add('active')
        
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

export default {
  extends: DefaultTheme,
  Layout,
  enhanceApp({ app }) {
    app.component('Callout', Callout)
    app.component('DemoGif', DemoGif)
    app.component('CodePlayground', CodePlayground)
    app.component('ContentTabs', ContentTabs)
    app.component('NavTabs', NavTabs)
    app.component('StickyHeader', StickyHeader)
    app.component('StickySidebar', StickySidebar)
    app.component('ToastContainer', ToastContainer)
    app.component('LoadingSpinner', LoadingSpinner)
    app.component('BackToTop', BackToTop)
    app.component('Breadcrumb', Breadcrumb)
    app.component('Tooltip', Tooltip)
    app.component('CodeAnnotation', CodeAnnotation)
    app.component('OpenAPI', OpenAPI)
  },
  scripts: [
    {
      src: 'data:text/javascript,' + encodeURIComponent(tabsClientScript),
      type: 'text/javascript',
    }
  ]
}
