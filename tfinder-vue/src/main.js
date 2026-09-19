import { createApp } from 'vue'
import App from '@/App.vue'
import router from '@/router'
import '@/styles/app.css'
import '@/styles/tokens.css'
import '@/styles/harness.css'
import '@/styles/crono.css'

createApp(App).use(router).mount('#app')
