import { ref, computed } from 'vue'
import { mesasApi } from '@/api/endpoints'

export function useMesas() {
  const mesas = ref([])
  const mesa = ref(null)
  const isLoading = ref(false)
  const isDetalleLoading = ref(false)
  const uniendo = ref(false)
  const error = ref('')
  const vacantes = ref(0)
  const hayVacantes = computed(() => vacantes.value > 0)
  const cacheTierLista = ref('')
  const cacheTierDetalle = ref('')

  function extenderTier(resp, refTier) {
    if (!resp) return ''
    const h = resp.encabezados || {}
    return h['x-cache-tier'] || h['x-cache'] || h['x-tier'] || refTier.value
  }

  async function cargarLista() {
    isLoading.value = true
    try {
      const resp = await mesasApi.listar()
      mesas.value = resp?.datos ?? resp?.data ?? []
      cacheTierLista.value = extenderTier(resp, cacheTierLista)
    } catch (e) {
      error.value = e?.mensaje || e?.message || 'No pudimos leer el archivo de mesas.'
    } finally {
      isLoading.value = false
    }
  }

  async function cargarDetalle(id) {
    isDetalleLoading.value = true
    try {
      const resp = await mesasApi.detalle(id)
      const m = resp?.datos ?? resp?.data ?? null
      mesa.value = m
      cacheTierDetalle.value = extenderTier(resp, cacheTierDetalle)
      vacantes.value = m ? Math.max((m.plazas ?? 0) - (m.jugadores ?? 0), 0) : 0
    } catch (e) {
      error.value = e?.mensaje || e?.message || 'No pudimos abrir los detalles de la mesa.'
    } finally {
      isDetalleLoading.value = false
    }
  }

  function nuevaIdempotenciaKey() {
    return (crypto?.randomUUID?.() || (Date.now().toString(36) + Math.random().toString(36).slice(2))) + '-union'
  }

  async function unirse() {
    if (!mesa.value || uniendo.value) return false
    uniendo.value = true
    const idempotencyKey = nuevaIdempotenciaKey()
    try {
      const resp = await mesasApi.solicitarUnion(mesa.value.id, {
        jugadorId: 'anonimo-lector',
        key: idempotencyKey
      }, idempotencyKey)
      // Evidencia real: la vacante se controla en el correo al vuelo (carrera). Reconsultamos cache-tier.
      vacantes.value = heapRestantes(mesa.value, resp)
      error.value = 'Tu solicitud se entrego con llave de idempotencia (' + idempotencyKey.slice(0, 13) + '...); si la plaza seguia libre quedo en el pergamino.'
      return true
    } catch (e) {
      if (e?.estado === 409 || e?.status === 409) {
        error.value = 'Tu solicitud ya figuraba con esa llave de idempotencia: no se duplico en el pergamino.'
      } else {
        error.value = e?.mensaje || e?.message || 'El correo no pudo entregar tu solicitud; intenta de nuevo.'
      }
      return false
    } finally {
      uniendo.value = false
    }
  }

  function heapRestantes(m, resp) {
    const actual = m ? Math.max((m.plazas ?? 0) - (m.jugadores ?? 0), 0) : 0
    const tras = resp?.datos?.vacantes ?? resp?.datos?.plazasLibres
    if (typeof tras === 'number') return tras
    return actual
  }

  return { mesas, mesa, isLoading, isDetalleLoading, uniendo, error, vacantes, hayVacantes, cacheTierLista, cacheTierDetalle, cargarLista, cargarDetalle, unirse }
}