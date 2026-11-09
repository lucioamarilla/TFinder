import { createApp } from 'vue'
import App from '@/App.vue'
import router from '@/router'
import '@/styles/tokens.css'
import '@/styles/base.css'
import '@/styles/app.css'
// D-07 (corregido): SOLO utilidades de Tailwind (sin base/preflight):
// el diseño visual proviene de tokens/base/app, que es el estilo del proyecto.
// (Las hojas muertas del prototipo pergamino fueron retiradas del repo.)
import '@/styles/tailwind.css'
document.documentElement.classList.add('js')

createApp(App).use(router).mount('#app')
