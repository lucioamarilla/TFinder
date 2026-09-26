import { ref } from 'vue'
import { getNoLeidas } from '@/services/notificaciones'

const INTERVALO_MS = 5000

const unreadCount = ref(0)
const desconectado = ref(false)
let timer = null
let suscriptores = 0

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
  if (timer) return
  refrescar()
  timer = setInterval(refrescar, INTERVALO_MS)
}

function detener() {
  suscriptores = Math.max(0, suscriptores - 1)
  if (suscriptores > 0 || !timer) return
  clearInterval(timer)
  timer = null
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
