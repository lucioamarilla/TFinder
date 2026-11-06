import { createApp } from 'vue'
import App from '@/App.vue'
import router from '@/router'
import '@/styles/tokens.css'
import '@/styles/base.css'
import '@/styles/app.css'
// D-07: Tailwind compilado + capas pergamino del prototipo (gestion/sim-*).
import '@/styles/tailwind.css'
import '@/styles/crono.css'
import '@/styles/harness.css'
document.documentElement.classList.add('js')

createApp(App).use(router).mount('#app')
