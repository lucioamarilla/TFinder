import { ref, onUnmounted } from 'vue'
import { pdfApi } from '@/api/endpoints'

export function usePdfDescarga(solicitar) {
  const fase = ref('inactivo')
  const mensaje = ref('')
  const documentoId = ref(null)
  let timer = null

  async function exportar() {
    fase.value = 'enviando'
    mensaje.value = ''
    try {
      const { status, datos } = await solicitar()
      if (status === 202 || status === 200) {
        fase.value = 'en_cola'
        documentoId.value = datos.documento_id
        vigilar()
      } else {
        fase.value = 'error'
        mensaje.value = datos?.detalle ?? 'La generación no fue aceptada.'
      }
    } catch (e) {
      fase.value = 'error'
      mensaje.value = e?.mensaje ?? 'No se pudo solicitar el PDF.'
    }
  }

  function vigilar() {
    if (timer) clearInterval(timer)
    timer = setInterval(async () => {
      try {
        const { status } = await pdfApi.estado(documentoId.value)
        if (status === 200) {
          fase.value = 'listo'
          if (timer) clearInterval(timer)
        }
      } catch (e) {
        if (e?.codigo === 404) return
        if (timer) clearInterval(timer)
        fase.value = 'error'
        mensaje.value = e?.mensaje ?? 'Falló la generación.'
      }
    }, 2000)
  }

  function abrirDescarga() {
    window.open(`http://localhost:8004/api/v1/pdf/${documentoId.value}`, '_blank')
  }

  onUnmounted(() => timer && clearInterval(timer))

  return { fase, mensaje, documentoId, exportar, abrirDescarga }
}