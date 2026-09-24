import { ref, onMounted } from 'vue'
import { getNotificaciones, getNoLeidas } from '@/services/notificaciones'

const lista = ref([])
const noLeidas = ref(0)
const desconectado = ref(false)
let timer = null
let arrancado = false

export async function refrescar() {
  try {
    const [items, pendientes] = await Promise.all([getNotificaciones(), getNoLeidas()])
    lista.value = items
    noLeidas.value = pendientes
    desconectado.value = false
  } catch (e) {
    desconectado.value = true
  }
}

function arrancarPolling(periodoMs) {
  if (arrancado) return
  arrancado = true
  refrescar()
  timer = setInterval(refrescar, periodoMs)
}

export function useNotifications(periodoMs = 5000) {
  onMounted(() => arrancarPolling(periodoMs))
  return { lista, noLeidas, desconectado, refrescar }
}