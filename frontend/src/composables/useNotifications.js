import { ref } from 'vue'
import { apiUrl } from '@/config/api'
import { currentAccessToken } from '@/composables/useAuth'
import { getNoLeidas } from '@/services/notificaciones'

const INTERVALO_MS = 5000
const MODO_API = true

const unreadCount = ref(0)
const desconectado = ref(false)
let timer = null
let suscriptores = 0
let fuenteSSE = null

async function refrescar() {
  try {
    unreadCount.value = await getNoLeidas()
    desconectado.value = false
  } catch {
    desconectado.value = true
  }
}

function arrancar() {
  suscriptores += 1
  if (timer || fuenteSSE) return
  refrescar()
  if (MODO_API) {
    const token = currentAccessToken()
    if (token) {
      const url = apiUrl('notif', `/api/v1/notificaciones/stream?token=${encodeURIComponent(token)}`)
      try {
        fuenteSSE = new EventSource(url)
        fuenteSSE.onmessage = (e) => {
          try {
            const datos = JSON.parse(e.data)
            // Un ping/evento nuevo → re-contar
            if (datos?.titulo || datos?.id) refrescar()
          } catch {
            refrescar()
          }
        }
        fuenteSSE.onerror = () => {
          // fallback a polling si SSE se rompe
          if (fuenteSSE) {
            fuenteSSE.close()
            fuenteSSE = null
          }
          desconectado.value = true
          timer = setInterval(refrescar, INTERVALO_MS)
        }
        return
      } catch {
        /* cae al polling */
      }
    }
  }
  timer = setInterval(refrescar, INTERVALO_MS)
}

function detener() {
  suscriptores = Math.max(0, suscriptores - 1)
  if (suscriptores > 0) return
  if (timer) {
    clearInterval(timer)
    timer = null
  }
  if (fuenteSSE) {
    fuenteSSE.close()
    fuenteSSE = null
  }
}

export function useNotifications() {
  async function loadCount() {
    try {
      unreadCount.value = await getNoLeidas()
      desconectado.value = false
    } catch {
      desconectado.value = true
      unreadCount.value = 0
    }
  }

  function setUnread(value) {
    unreadCount.value = value
  }

  return { unreadCount, desconectado, loadCount, setUnread, arrancar, detener }
}
