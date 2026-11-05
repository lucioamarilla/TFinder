import { ref } from 'vue'
import { mesasApi } from '@/api/endpoints'

const PREFIJO = 'tfinder-idem:solicitud:'

function keyDe(mesaId, usuarioSub) {
  const almacen = `${PREFIJO}${mesaId}:${usuarioSub}`
  const previa = localStorage.getItem(almacen)
  if (previa) return previa
  const nueva = `${usuarioSub}-${mesaId}-${Date.now().toString(36)}`
  localStorage.setItem(almacen, nueva)
  return nueva
}

export function useSolicitud(mesaId) {
  const estado = ref('inactivo')
  const mensaje = ref('')

  async function unirse(usuarioSub) {
    estado.value = 'enviando'
    mensaje.value = ''
    try {
      const { datos, status } = await mesasApi.solicitarUnion(
        mesaId,
        {},
        keyDe(mesaId, usuarioSub)
      )
      if (status === 201) {
        estado.value = 'solicitada'
        mensaje.value = datos?.mensaje || 'Solicitud enviada al director de juego'
      } else {
        estado.value = 'agotada'
        mensaje.value = datos?.mensaje || 'Sin vacantes por ahora'
      }
    } catch (e) {
      estado.value = e?.codigo === 409 ? 'agotada' : 'error'
      mensaje.value = e?.mensaje ?? 'No pudimos procesar tu solicitud.'
    }
    return estado.value
  }

  return { estado, mensaje, unirse }
}