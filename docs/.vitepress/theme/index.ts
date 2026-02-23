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
import DocStatusBadge from './components/DocStatusBadge.vue'
import AuditTimeline from './components/AuditTimeline.vue'
import KBGraph from './components/KBGraph.vue'
import { tabsClientScript } from '../plugins/content-tabs'
import './custom.css'

export default {
  extends: DefaultTheme,
  Layout,
  enhanceApp({ app }: { app: import('vue').App }) {
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
    app.component('DocStatusBadge', DocStatusBadge)
    app.component('AuditTimeline', AuditTimeline)
    app.component('KBGraph', KBGraph)
  },
  scripts: [
    {
      src: 'data:text/javascript,' + encodeURIComponent(tabsClientScript),
      type: 'text/javascript',
    }
  ]
}
