import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  // Same-origin en desarrollo: el dev server proxy-a hacia los 4 APIs de la
  // misma forma que nginx.conf lo hace en producción.
  server: {
    port: 5173,
    proxy: {
      '/mesas-api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        rewrite: (p) => p.replace(/^\/mesas-api/, '')
      }
    }
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./tests/setup.js'],
    include: ['tests/**/*.spec.js']
  }
})
