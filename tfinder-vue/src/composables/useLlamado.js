import { ref, onUnmounted } from 'vue'
import { matchmakingApi } from '@/api/endpoints'

export function useLlamado(mesaId) {
  const estado = ref('cerrado')
  const ttl = ref(0)
  const mmId = ref(null)
  let timer = null

  async function refrescar() {
    if (mmId.value === null) return
    try {
      const { datos } = await matchmakingApi.estado(mmId.value)
      estado.value = datos.estado
      ttl.value = datos.ttl_restante
    } catch (e) {
      estado.value = 'error'
    }
  }

  async function abrir() {
    const { datos } = await matchmakingApi.abrir(mesaId)
    mmId.value = datos.matchmaking_id ?? datos.id
    estado.value = datos.estado
    ttl.value = datos.expira_en
    if (timer) clearInterval(timer)
    timer = setInterval(refrescar, 2000)
  }

  function detener() {
    if (timer) clearInterval(timer)
  }

  onUnmounted(detener)

  return { estado, ttl, mmId, abrir, refrescar, detener }
}