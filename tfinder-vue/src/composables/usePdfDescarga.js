import { ref, computed, onUnmounted } from 'vue'
import { pdfApi } from '@/api/endpoints'

const INTERVALO_MS = 2000
const MAX_INTENTOS = 30

function nombreArchivo(contentDisposition) {
  if (!contentDisposition) return null
  const extendida = /filename\*=(?:UTF-8'')?([^;]+)/i.exec(contentDisposition)
  if (extendida) return decodeURIComponent(extendida[1].trim().replace(/^"|"$/g, ''))
  const simple = /filename="?([^";]+)"?/i.exec(contentDisposition)
  return simple ? simple[1] : null
}

function guardarBlob(blob, nombre) {
  const url = URL.createObjectURL(blob)
  const enlace = document.createElement('a')
  enlace.href = url
  enlace.download = nombre
  document.body.appendChild(enlace)
  enlace.click()
  enlace.remove()
  URL.revokeObjectURL(url)
}

export function usePdfDescarga(solicitar, etiquetaBase = 'Exportar PDF') {
  const fase = ref('inactivo')
  const mensaje = ref('')
  const documentoId = ref(null)
  let timer = null
  let intentos = 0

  const ocupado = computed(() => ['enviando', 'en_cola', 'descargando'].includes(fase.value))
  const listo = computed(() => fase.value === 'listo')
  const etiqueta = computed(() => {
    if (fase.value === 'enviando') return 'Enviando…'
    if (fase.value === 'en_cola') return 'Generando PDF…'
    if (fase.value === 'descargando') return 'Descargando…'
    if (fase.value === 'listo') return 'Descargar PDF'
    if (fase.value === 'error') return 'Reintentar'
    return etiquetaBase
  })

  function detener() {
    if (timer) clearTimeout(timer)
    timer = null
  }

  async function exportar() {
    detener()
    intentos = 0
    mensaje.value = ''
    fase.value = 'enviando'
    try {
      const { status, datos } = await solicitar()
      if (status !== 202 && status !== 200) {
        fase.value = 'error'
        mensaje.value = datos?.detalle ?? 'La generación no fue aceptada.'
        return
      }
      documentoId.value = datos?.documento_id ?? null
      if (!documentoId.value) {
        fase.value = 'error'
        mensaje.value = 'La respuesta no incluyó el identificador del documento.'
        return
      }
      fase.value = 'en_cola'
      vigilar()
    } catch (e) {
      fase.value = 'error'
      mensaje.value = e?.mensaje || e?.message || 'No se pudo solicitar el PDF.'
    }
  }

  async function consultar() {
    let estado = null
    try {
      const { datos } = await pdfApi.estado(documentoId.value)
      estado = datos?.estado ?? null
    } catch (e) {
      if (e?.codigo !== 404) {
        detener()
        fase.value = 'error'
        mensaje.value = e?.mensaje || e?.message || 'No pudimos consultar el estado del PDF.'
        return
      }
      estado = 'en_proceso'
    }

    if (estado === 'listo') {
      detener()
      fase.value = 'listo'
      return
    }
    if (estado === 'error') {
      detener()
      fase.value = 'error'
      mensaje.value = 'El servicio no pudo generar el PDF.'
      return
    }

    intentos += 1
    if (intentos >= MAX_INTENTOS) {
      detener()
      fase.value = 'error'
      mensaje.value = `El PDF no se generó en ${Math.round((MAX_INTENTOS * INTERVALO_MS) / 1000)} segundos.`
    }
  }

  function vigilar() {
    detener()
    const tick = async () => {
      if (fase.value !== 'en_cola') return
      await consultar()
      if (fase.value === 'en_cola') timer = setTimeout(tick, INTERVALO_MS)
    }
    timer = setTimeout(tick, INTERVALO_MS)
  }

  async function descargar() {
    if (!documentoId.value) return
    fase.value = 'descargando'
    try {
      const { blob, encabezados } = await pdfApi.descargar(documentoId.value)
      const nombre = nombreArchivo(encabezados?.['content-disposition']) ?? `tfinder_${documentoId.value}.pdf`
      guardarBlob(blob, nombre)
      fase.value = 'listo'
    } catch (e) {
      fase.value = 'error'
      mensaje.value = e?.mensaje || e?.message || 'No pudimos descargar el PDF.'
    }
  }

  function cancelar() {
    if (fase.value === 'inactivo') return
    detener()
    documentoId.value = null
    fase.value = 'cancelado'
  }

  onUnmounted(detener)

  return { fase, mensaje, documentoId, ocupado, listo, etiqueta, exportar, descargar, cancelar }
}
