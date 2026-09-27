import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/api/endpoints', () => ({
  notifApi: {
    notificaciones: vi.fn(),
    marcarLeida: vi.fn()
  }
}))

const { notifApi } = await import('@/api/endpoints')
const { formatearFecha, normalizarNotificacion, getNotificaciones, marcarLeida, marcarTodasLeidas } = await import(
  '@/services/notificaciones'
)

const DEL_BACKEND = {
  id: 1,
  grupo: 'mesas',
  icono: 'solicitud',
  leida: false,
  autor: null,
  mensaje: 'Solicitud aceptada',
  entidad: 'mesa',
  detalle: 'Tu solicitud para la mesa 3 fue aceptada',
  enlace: { label: 'ver mesa', to: '/mesas/3' },
  fecha: null,
  creado_en: '2026-09-27T14:32:00+00:00'
}

beforeEach(() => {
  vi.clearAllMocks()
})

describe('normalización de notificaciones', () => {
  it('saca la fecha de creado_en porque la columna fecha llega vacía', () => {
    const n = normalizarNotificacion({ ...DEL_BACKEND })
    expect(n.fecha).not.toBeNull()
    expect(n.fecha).not.toBe(DEL_BACKEND.creado_en)
    expect(n.fecha).toContain('2026')
  })

  it('usa la columna fecha cuando no viene creado_en', () => {
    const n = normalizarNotificacion({ ...DEL_BACKEND, creado_en: null, fecha: '2026-01-02T08:00:00+00:00' })
    expect(n.fecha).toContain('2026')
    expect(n.fecha).toContain('01')
  })

  it('devuelve el texto tal cual si la fecha no es parseable', () => {
    expect(formatearFecha('ahora')).toBe('ahora')
    expect(formatearFecha(null)).toBeNull()
    expect(formatearFecha(undefined)).toBeNull()
  })

  it('convierte leida a booleano sin importar lo que mande el backend', () => {
    expect(normalizarNotificacion({ leida: false }).leida).toBe(false)
    expect(normalizarNotificacion({ leida: true }).leida).toBe(true)
    expect(normalizarNotificacion({}).leida).toBe(false)
  })

  it('respeta el enlace {label,to} que manda notif-api', () => {
    const n = normalizarNotificacion({ ...DEL_BACKEND })
    expect(n.enlace).toEqual({ label: 'ver mesa', to: '/mesas/3' })
  })

  it('descarta el enlace si no trae una ruta navegable', () => {
    expect(normalizarNotificacion({ enlace: null }).enlace).toBeNull()
    expect(normalizarNotificacion({ enlace: { '/mesas/3': 'ver mesa' } }).enlace).toBeNull()
    expect(normalizarNotificacion({ enlace: { label: 'ver mesa' } }).enlace).toBeNull()
    expect(normalizarNotificacion({ enlace: { to: '/mesas/3' } }).enlace).toEqual({
      label: 'Ver detalle',
      to: '/mesas/3'
    })
  })

  it('rellena los campos que el backend nunca escribe', () => {
    const n = normalizarNotificacion({ id: 9, mensaje: 'Aviso' })
    expect(n).toMatchObject({ id: 9, grupo: 'mesas', icono: 'solicitud', autor: null, leida: false, fecha: null, enlace: null })
  })

  it('conserva el resto de campos tal cual', () => {
    const n = normalizarNotificacion({ ...DEL_BACKEND })
    expect(n.mensaje).toBe('Solicitud aceptada')
    expect(n.detalle).toBe('Tu solicitud para la mesa 3 fue aceptada')
    expect(n.entidad).toBe('mesa')
  })
})

describe('operaciones contra notif-api', () => {
  it('lista y normaliza cada notificación', async () => {
    notifApi.notificaciones.mockResolvedValue({ datos: [DEL_BACKEND] })
    const lista = await getNotificaciones()
    expect(lista).toHaveLength(1)
    expect(lista[0]).toMatchObject({ id: 1, leida: false, mensaje: 'Solicitud aceptada' })
  })

  it('devuelve lista vacía si el backend no trae datos', async () => {
    notifApi.notificaciones.mockResolvedValue({ datos: null })
    expect(await getNotificaciones()).toEqual([])
  })

  it('marca una notificación como leída y la devuelve normalizada', async () => {
    notifApi.marcarLeida.mockResolvedValue({ datos: { ...DEL_BACKEND, leida: true } })
    const actualizada = await marcarLeida(1)
    expect(notifApi.marcarLeida).toHaveBeenCalledWith(1)
    expect(actualizada.leida).toBe(true)
    expect(actualizada.fecha).toContain('2026')
  })

  it('marca todas solo las que siguen sin leer', async () => {
    notifApi.notificaciones.mockResolvedValue({
      datos: [
        { ...DEL_BACKEND, id: 1, leida: false },
        { ...DEL_BACKEND, id: 2, leida: true },
        { ...DEL_BACKEND, id: 3, leida: false }
      ]
    })
    notifApi.marcarLeida.mockResolvedValue({ datos: { ...DEL_BACKEND, leida: true } })

    expect(await marcarTodasLeidas()).toBe(true)
    expect(notifApi.marcarLeida.mock.calls.map((c) => c[0])).toEqual([1, 3])
  })

  it('propaga el error cuando notif-api está caído', async () => {
    notifApi.notificaciones.mockRejectedValue(Object.assign(new Error('notif-api caído'), { codigo: 503 }))
    await expect(getNotificaciones()).rejects.toThrow('notif-api caído')
  })
})
