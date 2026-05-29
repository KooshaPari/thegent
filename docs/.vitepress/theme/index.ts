import DefaultTheme from 'vitepress/theme'
import type { Theme } from 'vitepress'
import Callout from './components/Callout.vue'
import DemoGif from './components/DemoGif.vue'
import './style.css'

const theme: Theme = {
  ...DefaultTheme,
  enhanceApp({ app }) {
    app.component('Callout', Callout)
    app.component('DemoGif', DemoGif)
  },
}

export default theme
