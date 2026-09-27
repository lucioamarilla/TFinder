import { beforeEach, afterEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { defineComponent, h } from 'vue'
import { pdfApi } from '@/api/endpoints'
import { usePdfDescarga } from '@/composables/usePdfDescarga'

vi.mock('@/api/endpoints', () => ({
  pdfApi: { estado: vi.fn(), descargar: vi.fn() }
}))

const INTERVALO_MS = 2000
const MAX_INTENTOS = 30

function montar(solicitar) {
  let api = null
  const wrapper = mount(
    defineComponent({
      setup() {
        api = usePdfDescarga(solicitar)
        return () => h('div')
      }
    })
  )
  return { wrapper, api: () => api }
}

const pdf = new Blob(['%PDF-1.4'], { type: 'application/pdf' })

let descargas = []

describe('descarga de PDF en cola', () => {
  beforeEach(() => {
    descargas = []
    vi.clearAllMocks()
    vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(function () {
      descargas.push({ nombre: this.download, href: this.getAttribute('href') })
    })
    global.URL.createObjectURL = vi.fn(() => 'blob:tfinder')
    global.URL.revokeObjectURL = vi.fn()
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.restoreAllMocks()
  })

  it('arranca inactivo y sin documento', () => {
    const { api } = montar(vi.fn())
    expect(api().fase.value).toBe('inactivo')
    expect(api().documentoId.value).toBeNull()
    expect(api().ocupado.value).toBe(false)
  })

  it('pasa a en_cola con el documento_id del 202', async () => {
    const solicitar = vi.fn().mockResolvedValue({ status: 202, datos: { documento_id: 'doc-7' } })
    const { api } = montar(solicitar)

    await api().exportar()

    expect(solicitar).toHaveBeenCalledOnce()
    expect(api().fase.value).toBe('en_cola')
    expect(api().documentoId.value).toBe('doc-7')
    expect(api().ocupado.value).toBe(true)
  })

  it('marca listo cuando el estado pasa a listo', async () => {
    vi.useFakeTimers()
    const solicitar = vi.fn().mockResolvedValue({ status: 202, datos: { documento_id: 'doc-7' } })
    pdfApi.estado.mockResolvedValue({ status: 200, datos: { estado: 'listo' } })
    const { api } = montar(solicitar)

    await api().exportar()
    await vi.advanceTimersByTimeAsync(INTERVALO_MS)

    expect(api().fase.value).toBe('listo')
    expect(api().listo.value).toBe(true)
    expect(pdfApi.estado).toHaveBeenCalledWith('doc-7')
  })

  it('sigue en cola mientras el documento no existe todavía', async () => {
    vi.useFakeTimers()
    const solicitar = vi.fn().mockResolvedValue({ status: 202, datos: { documento_id: 'doc-7' } })
    pdfApi.estado.mockRejectedValue(Object.assign(new Error('no existe'), { codigo: 404 }))
    const { api } = montar(solicitar)

    await api().exportar()
    await vi.advanceTimersByTimeAsync(INTERVALO_MS * 3)

    expect(api().fase.value).toBe('en_cola')
    expect(api().mensaje.value).toBe('')
  })

  it('propaga el error del servicio cuando la generación falla', async () => {
    vi.useFakeTimers()
    const solicitar = vi.fn().mockResolvedValue({ status: 202, datos: { documento_id: 'doc-7' } })
    pdfApi.estado.mockResolvedValue({ status: 200, datos: { estado: 'error' } })
    const { api } = montar(solicitar)

    await api().exportar()
    await vi.advanceTimersByTimeAsync(INTERVALO_MS)

    expect(api().fase.value).toBe('error')
    expect(api().mensaje.value).toMatch(/no pudo generar/i)
  })

  it('corta el polling si consultar el estado revienta', async () => {
    vi.useFakeTimers()
    const solicitar = vi.fn().mockResolvedValue({ status: 202, datos: { documento_id: 'doc-7' } })
    pdfApi.estado.mockRejectedValue(Object.assign(new Error('boom'), { codigo: 500, mensaje: 'notif-api caído' }))
    const { api } = montar(solicitar)

    await api().exportar()
    await vi.advanceTimersByTimeAsync(INTERVALO_MS)
    const llamadas = pdfApi.estado.mock.calls.length
    await vi.advanceTimersByTimeAsync(INTERVALO_MS * 5)

    expect(api().fase.value).toBe('error')
    expect(api().mensaje.value).toBe('notif-api caído')
    expect(pdfApi.estado.mock.calls.length).toBe(llamadas)
  })

  it('abandona la cola si se agota el tiempo de espera', async () => {
    vi.useFakeTimers()
    const solicitar = vi.fn().mockResolvedValue({ status: 202, datos: { documento_id: 'doc-7' } })
    pdfApi.estado.mockResolvedValue({ status: 200, datos: { estado: 'en_proceso' } })
    const { api } = montar(solicitar)

    await api().exportar()
    await vi.advanceTimersByTimeAsync(INTERVALO_MS * MAX_INTENTOS)

    expect(api().fase.value).toBe('error')
    expect(api().mensaje.value).toMatch(/60 segundos/)
  })

  it('reporta error si el 202 no trae documento_id', async () => {
    const solicitar = vi.fn().mockResolvedValue({ status: 202, datos: {} })
    const { api } = montar(solicitar)

    await api().exportar()

    expect(api().fase.value).toBe('error')
    expect(pdfApi.estado).not.toHaveBeenCalled()
  })

  it('reporta error si la solicitud es rechazada', async () => {
    const solicitar = vi.fn().mockRejectedValue(new ApiErrorStub(404, 'Build no encontrado'))
    const { api } = montar(solicitar)

    await api().exportar()

    expect(api().fase.value).toBe('error')
    expect(api().mensaje.value).toBe('Build no encontrado')
  })

  it('descarga el blob con el nombre del content-disposition', async () => {
    const solicitar = vi.fn().mockResolvedValue({ status: 202, datos: { documento_id: 'doc-7' } })
    pdfApi.descargar.mockResolvedValue({
      status: 200,
      blob: pdf,
      encabezados: { 'content-disposition': 'attachment; filename="tfinder_build_42.pdf"' }
    })
    const { api } = montar(solicitar)

    await api().exportar()
    await api().descargar()

    expect(pdfApi.descargar).toHaveBeenCalledWith('doc-7')
    expect(global.URL.createObjectURL).toHaveBeenCalledWith(pdf)
    expect(global.URL.revokeObjectURL).toHaveBeenCalledWith('blob:tfinder')
    expect(descargas).toEqual([{ nombre: 'tfinder_build_42.pdf', href: 'blob:tfinder' }])
    expect(api().fase.value).toBe('listo')
  })

  it('usa un nombre por defecto si no viene content-disposition', async () => {
    const solicitar = vi.fn().mockResolvedValue({ status: 202, datos: { documento_id: 'doc-7' } })
    pdfApi.descargar.mockResolvedValue({ status: 200, blob: pdf, encabezados: {} })
    const { api } = montar(solicitar)

    await api().exportar()
    await api().descargar()

    expect(descargas).toEqual([{ nombre: 'tfinder_doc-7.pdf', href: 'blob:tfinder' }])
    expect(api().fase.value).toBe('listo')
  })

  it('deca al usar un nombre codificado en content-disposition', async () => {
    const solicitar = vi.fn().mockResolvedValue({ status: 202, datos: { documento_id: 'doc-7' } })
    pdfApi.descargar.mockResolvedValue({
      status: 200,
      blob: pdf,
      encabezados: { 'content-disposition': "attachment; filename*=UTF-8''tfinder_build_42%20final.pdf" }
    })
    const { api } = montar(solicitar)

    await api().exportar()
    await api().descargar()

    expect(descargas[0].nombre).toBe('tfinder_build_42 final.pdf')
  })

  it('cancela el polling a pedido', async () => {
    vi.useFakeTimers()
    const solicitar = vi.fn().mockResolvedValue({ status: 202, datos: { documento_id: 'doc-7' } })
    pdfApi.estado.mockResolvedValue({ status: 200, datos: { estado: 'en_proceso' } })
    const { api } = montar(solicitar)

    await api().exportar()
    await vi.advanceTimersByTimeAsync(INTERVALO_MS)
    const llamadas = pdfApi.estado.mock.calls.length
    api().cancelar()
    await vi.advanceTimersByTimeAsync(INTERVALO_MS * 5)

    expect(api().fase.value).toBe('cancelado')
    expect(pdfApi.estado.mock.calls.length).toBe(llamadas)
  })

  it('deja de consultar cuando la vista se desmonta', async () => {
    vi.useFakeTimers()
    const solicitar = vi.fn().mockResolvedValue({ status: 202, datos: { documento_id: 'doc-7' } })
    pdfApi.estado.mockResolvedValue({ status: 200, datos: { estado: 'en_proceso' } })
    const { wrapper, api } = montar(solicitar)

    await api().exportar()
    await vi.advanceTimersByTimeAsync(INTERVALO_MS)
    const llamadas = pdfApi.estado.mock.calls.length
    wrapper.unmount()
    await vi.advanceTimersByTimeAsync(INTERVALO_MS * 5)

    expect(pdfApi.estado.mock.calls.length).toBe(llamadas)
  })
})

class ApiErrorStub extends Error {
  constructor(codigo, mensaje) {
    super(mensaje)
    this.name = 'ApiError'
    this.codigo = codigo
    this.mensaje = mensaje
  }
}
