import DefaultTheme from 'vitepress/theme'
import Callout from './components/Callout.vue'
import './custom.css'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('Callout', Callout)
  }
}
