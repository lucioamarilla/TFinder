import { ref } from 'vue'
import { getNotificaciones } from '@/services/notificaciones'

const INTERVALO_MS = 5000

const lista = ref([])
const unreadCount = ref(0)
const desconectado = ref(false)
const ultimoError = ref(null)
let timer = null
let suscriptores = 0

async function refrescar() {
  try {
    lista.value = await getNotificaciones()
    unreadCount.value = lista.value.filter((n) => !n.leida).length
    desconectado.value = false
    ultimoError.value = null
    return true
  } catch (e) {
    desconectado.value = true
    ultimoError.value = e?.message || 'No pudimos abrir el centro de avisos.'
    unreadCount.value = 0
    return false
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
  return { lista, unreadCount, desconectado, ultimoError, refrescar, arrancar, detener }
}
