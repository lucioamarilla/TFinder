import { createApp } from 'vue'
import App from '@/App.vue'
import router from '@/router'
import '@/styles/tokens.css'
import '@/styles/base.css'
import '@/styles/app.css'
document.documentElement.classList.add('js')

createApp(App).use(router).mount('#app')
