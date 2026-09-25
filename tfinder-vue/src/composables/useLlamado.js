import { ref, computed, onMounted, onUnmounted } from 'vue'
import { matchmakingApi } from '@/api/endpoints'

const ESTADOS = { ABIERTO: 'abierto', CERRADO: 'cerrado', EXPIRADO: 'expirado' }

export function useLlamado(mesaId) {
  const estado = ref(ESTADOS.CERRADO)
  const ttl = ref(0)
  const cargando = ref(false)
  const error = ref('')
  const anotando = ref(false)
  let timer = null

  const expiraEn = computed(() => ttl.value)

  async function refrescar() {
    const resp = await matchmakingApi.estado(mesaId)
    const datos = resp?.datos ?? resp
    estado.value = datos.estado === 'abierto' ? ESTADOS.ABIERTO : datos.estado
    ttl.value = datos.ttl_restante ?? 0
    if (ttl.value <= 0) {
      estado.value = ESTADOS.EXPIRADO
      ttl.value = 0
      clearInterval(timer)
    }
  }

  async function abrir() {
    cargando.value = true
    error.value = ''
    try {
      const resp = await matchmakingApi.abrir(mesaId)
      const datos = resp?.datos ?? resp
      estado.value = ESTADOS.ABIERTO
      ttl.value = datos?.expira_en ?? 120
      iniciarPolling()
    } catch (e) {
      error.value = e?.mensaje || e?.message || 'No pudimos abrir el llamado.'
    } finally {
      cargando.value = false
    }
  }

  async function anotarse() {
    anotando.value = true
    error.value = ''
    try {
      const resp = await matchmakingApi.anotarse(mesaId, {
        rol: 'jugador',
        key: crypto?.randomUUID?.() || Math.random().toString(36).slice(2)
      })
      return { aceptado: resp?.datos?.estado === 'aceptado', datos: resp?.datos, estatus: resp?.status }
    } catch (e) {
      if (e?.status === 409 || e?.estado === 409) {
        return { aceptado: false, cupoAgotado: true, estatus: 409 }
      }
      throw e
    } finally {
      anotando.value = false
    }
  }

  function iniciarPolling() {
    clearInterval(timer)
    timer = setInterval(async () => {
      try { await refrescar() } catch { clearInterval(timer) }
    }, 2000)
  }

  onMounted(() => { refrescar().catch(() => {}) })
  onUnmounted(() => clearInterval(timer))

  return { estado, ttl, expiraEn, cargando, error, anotando, abrir, anotarse, refrescar }
}