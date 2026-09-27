import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/services/notificaciones', () => ({
  getNotificaciones: vi.fn()
}))

const { getNotificaciones } = await import('@/services/notificaciones')

const INTERVALO_MS = 5000

const aviso = (id, leida) => ({ id, leida, mensaje: `Aviso ${id}`, grupo: 'mesas' })

async function composable() {
  const mod = await import('@/composables/useNotifications')
  return mod.useNotifications()
}

beforeEach(() => {
  vi.clearAllMocks()
  vi.resetModules()
  getNotificaciones.mockResolvedValue([aviso(1, false), aviso(2, true), aviso(3, false)])
})

afterEach(() => {
  vi.useRealTimers()
})

describe('estado compartido de notificaciones', () => {
  it('arranca sin lista y con el contador en cero', async () => {
    const { lista, unreadCount, desconectado } = await composable()
    expect(lista.value).toEqual([])
    expect(unreadCount.value).toBe(0)
    expect(desconectado.value).toBe(false)
  })

  it('comparte la misma lista y el mismo contador entre dos consumidores', async () => {
    const header = await composable()
    const vista = await composable()

    await header.refrescar()

    expect(vista.lista).toBe(header.lista)
    expect(vista.unreadCount).toBe(header.unreadCount)
    expect(vista.lista.value).toHaveLength(3)
  })

  it('deriva el contador de sin leer de la lista en una sola llamada', async () => {
    const { lista, unreadCount, refrescar } = await composable()

    expect(getNotificaciones).not.toHaveBeenCalled()
    await refrescar()

    expect(getNotificaciones).toHaveBeenCalledOnce()
    expect(lista.value).toHaveLength(3)
    expect(unreadCount.value).toBe(2)
  })

  it('baja el contador cuando el backend responde todo leído', async () => {
    getNotificaciones.mockResolvedValue([aviso(1, true), aviso(2, true)])
    const { unreadCount, refrescar } = await composable()

    await refrescar()

    expect(unreadCount.value).toBe(0)
  })
})

describe('polling cada 5 s', () => {
  it('consulta al arrancar y en cada tick', async () => {
    vi.useFakeTimers()
    const { arrancar, unreadCount } = await composable()

    arrancar()
    await vi.advanceTimersByTimeAsync(0)
    expect(getNotificaciones).toHaveBeenCalledTimes(1)
    expect(unreadCount.value).toBe(2)

    await vi.advanceTimersByTimeAsync(INTERVALO_MS)
    expect(getNotificaciones).toHaveBeenCalledTimes(2)

    await vi.advanceTimersByTimeAsync(INTERVALO_MS * 2)
    expect(getNotificaciones).toHaveBeenCalledTimes(4)
  })

  it('no duplica el timer si varios componentes se suscriben', async () => {
    vi.useFakeTimers()
    const a = await composable()
    const b = await composable()

    a.arrancar()
    b.arrancar()
    await vi.advanceTimersByTimeAsync(INTERVALO_MS * 3)

    expect(getNotificaciones).toHaveBeenCalledTimes(4)
  })

  it('sigue consultando mientras quede un suscriptor', async () => {
    vi.useFakeTimers()
    const a = await composable()
    const b = await composable()

    a.arrancar()
    b.arrancar()
    a.detener()
    await vi.advanceTimersByTimeAsync(INTERVALO_MS)

    expect(getNotificaciones).toHaveBeenCalledTimes(2)
  })

  it('corta el polling cuando el último suscriptor se va', async () => {
    vi.useFakeTimers()
    const { arrancar, detener } = await composable()

    arrancar()
    await vi.advanceTimersByTimeAsync(0)
    detener()
    const llamadas = getNotificaciones.mock.calls.length
    await vi.advanceTimersByTimeAsync(INTERVALO_MS * 5)

    expect(getNotificaciones).toHaveBeenCalledTimes(llamadas)
  })

  it('no pisa el timer cuando se refresca a mano', async () => {
    vi.useFakeTimers()
    const { arrancar, refrescar } = await composable()

    arrancar()
    await vi.advanceTimersByTimeAsync(INTERVALO_MS)
    await refrescar()
    expect(getNotificaciones).toHaveBeenCalledTimes(3)

    await vi.advanceTimersByTimeAsync(INTERVALO_MS)
    expect(getNotificaciones).toHaveBeenCalledTimes(4)
  })
})

describe('notif-api caído', () => {
  it('marca desconectado, oculta el número y guarda el último mensaje', async () => {
    getNotificaciones.mockRejectedValue(Object.assign(new Error('notif-api caído'), { codigo: 503 }))
    const { lista, unreadCount, desconectado, ultimoError, refrescar } = await composable()

    expect(await refrescar()).toBe(false)
    expect(desconectado.value).toBe(true)
    expect(unreadCount.value).toBe(0)
    expect(ultimoError.value).toBe('notif-api caído')
    expect(lista.value).toEqual([])
  })

  it('conserva la última lista conocida si se corta notif-api', async () => {
    const { lista, desconectado, refrescar } = await composable()
    await refrescar()
    expect(lista.value).toHaveLength(3)

    getNotificaciones.mockRejectedValue(new Error('notif-api caído'))
    await refrescar()

    expect(desconectado.value).toBe(true)
    expect(lista.value).toHaveLength(3)
  })

  it('no rompe el polling cuando una llamada falla', async () => {
    vi.useFakeTimers()
    getNotificaciones
      .mockResolvedValueOnce([aviso(1, false)])
      .mockRejectedValueOnce(new Error('notif-api caído'))
      .mockResolvedValueOnce([aviso(1, false), aviso(2, false)])
    const { arrancar, desconectado, unreadCount } = await composable()

    arrancar()
    await vi.advanceTimersByTimeAsync(INTERVALO_MS)
    expect(desconectado.value).toBe(true)
    expect(unreadCount.value).toBe(0)

    await vi.advanceTimersByTimeAsync(INTERVALO_MS)
    expect(desconectado.value).toBe(false)
    expect(unreadCount.value).toBe(2)
  })

  it('vuelve a poblar cuando notif-api se levanta', async () => {
    const { lista, desconectado, ultimoError, refrescar } = await composable()
    getNotificaciones.mockRejectedValue(new Error('notif-api caído'))
    await refrescar()

    getNotificaciones.mockResolvedValue([aviso(9, false)])
    expect(await refrescar()).toBe(true)

    expect(desconectado.value).toBe(false)
    expect(ultimoError.value).toBeNull()
    expect(lista.value).toHaveLength(1)
  })
})
