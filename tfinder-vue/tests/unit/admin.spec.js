import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/api/endpoints', () => ({
  notifApi: {
    notificaciones: vi.fn(),
    marcarLeida: vi.fn(),
    eventLog: vi.fn()
  },
  adminApi: {
    live: vi.fn(),
    ready: vi.fn(),
    dlq: vi.fn(),
    reintentarDlq: vi.fn(),
    descartarDlq: vi.fn()
  }
}))

const { notifApi, adminApi } = await import('@/api/endpoints')
const { estadoDe, getCanalesReales, getEventosRecorridos, getDlq, reintentarMensaje, descartarMensaje, drenarCola, getResiliencia } =
  await import('@/services/admin')

const LISTO = { postgres: true, redis: true, rabbitmq: true }

const EN_COLA = [
  {
    id: 7,
    cola: 'tfinder.notif.dlq',
    payload: { tipo: 'solicitud_creada', id: 3 },
    error: 'Connection timed out',
    fecha: '2026-03-05T15:04:05Z'
  },
  {
    id: 8,
    cola: 'tfinder.notif.dlq',
    payload: '{"tipo":"mesa_abierta","id":9}',
    error: 'redis unavailable',
    fecha: '2026-03-05T15:06:00Z'
  }
]

// vivo()/caido() devuelven el par {live, ready} que respondería cada endpoint.
// Ambos son perezosos: la promesa rechazada de caido() solo nace si algún test la pide.
function vivo(estado = 'listo', dependencias = LISTO) {
  return {
    live: () => Promise.resolve({ status: 200, datos: { estado: 'vivo' } }),
    ready: () => Promise.resolve({ status: estado === 'listo' ? 200 : 503, datos: { estado, dependencias } })
  }
}

function caido(mensaje) {
  const rechazar = () => Promise.reject(new Error(mensaje))
  return { live: rechazar, ready: rechazar }
}

// mockImplementation para adminApi.live (clave 'live') o adminApi.ready (clave 'ready').
const porEndpoint = (escenario) => (clave) => (id) => (escenario[id] ?? vivo())[clave]()

beforeEach(() => {
  vi.clearAllMocks()
})

describe('salud real de los canales', () => {
  it('arma una tarjeta por servicio con live, ready y dependencias', async () => {
    adminApi.live.mockResolvedValue({ status: 200, datos: { estado: 'vivo' } })
    adminApi.ready.mockResolvedValue({ status: 200, datos: { estado: 'listo', dependencias: LISTO } })

    const canal = await estadoDe('mesas')

    expect(canal).toMatchObject({ id: 'mesas', nombre: 'mesas-api', live: true, ready: 'listo', tono: 'verde' })
    expect(canal.dependencias).toEqual([
      { clave: 'postgres', nombre: 'PostgreSQL', ok: true },
      { clave: 'redis', nombre: 'Redis', ok: true },
      { clave: 'rabbitmq', nombre: 'RabbitMQ', ok: true }
    ])
  })

  it('lee el cuerpo del 503 de /ready y marca el canal como degradado', async () => {
    adminApi.live.mockResolvedValue({ status: 200, datos: { estado: 'vivo' } })
    adminApi.ready.mockResolvedValue({
      status: 503,
      datos: { estado: 'degradado', dependencias: { postgres: true, redis: false, rabbitmq: true } }
    })

    const canal = await estadoDe('notif')

    expect(canal.ready).toBe('degradado')
    expect(canal.tono).toBe('ocre')
    expect(canal.dependencias.find((d) => d.clave === 'redis').ok).toBe(false)
  })

  it('marca sin datos cuando el servicio no responde, sin romper la consulta', async () => {
    adminApi.live.mockRejectedValue(Object.assign(new Error('fetch failed'), { mensaje: 'fetch failed' }))
    adminApi.ready.mockRejectedValue(Object.assign(new Error('fetch failed'), { mensaje: 'fetch failed' }))

    const canal = await estadoDe('feed')

    expect(canal.live).toBe(false)
    expect(canal.ready).toBe('sin_datos')
    expect(canal.tono).toBe('gris')
    expect(canal.detalle).toBe('fetch failed')
  })

  it('consulta los cuatro servicios y conserva el orden del conclave', async () => {
    adminApi.live.mockImplementation((id) => Promise.resolve({ status: 200, datos: { estado: 'vivo' } }))
    adminApi.ready.mockImplementation((id) =>
      id === 'builds'
        ? Promise.resolve({ status: 503, datos: { estado: 'degradado', dependencias: { postgres: true, redis: true, rabbitmq: false } } })
        : Promise.resolve({ status: 200, datos: { estado: 'listo', dependencias: LISTO } })
    )

    const canales = await getCanalesReales()

    expect(canales.map((c) => c.nombre)).toEqual(['mesas-api', 'builds-api', 'feed-api', 'notif-api'])
    expect(canales.filter((c) => c.tono === 'verde')).toHaveLength(3)
    expect(canales.find((c) => c.id === 'builds').tono).toBe('ocre')
  })
})

describe('event-log con correlation ID', () => {
  it('mapea EventOut a las columnas del recorrido', async () => {
    notifApi.eventLog.mockResolvedValue({
      datos: [
        {
          id: 4,
          entidadTipo: 'solicitud',
          entidadId: 3,
          accion: 'creada',
          usuarioId: null,
          metadata: { canal: 'web' },
          ocurridoEn: '2026-03-05T15:04:05Z',
          correlationId: 'cid-abc'
        }
      ]
    })

    const eventos = await getEventosRecorridos()

    expect(notifApi.eventLog).toHaveBeenCalledWith({})
    expect(eventos[0]).toMatchObject({ id: 4, entidad: 'solicitud #3', accion: 'creada', correlationId: 'cid-abc' })
    expect(eventos[0].ocurridoEn).toContain('2026')
    expect(eventos[0].metadata).toEqual({ canal: 'web' })
  })

  it('envía el filtro de correlation ID y tolera entidad sin id', async () => {
    notifApi.eventLog.mockResolvedValue({
      datos: [{ id: 5, entidadTipo: 'mesa', entidadId: null, accion: 'abierta', ocurridoEn: '2026-03-05T15:04:05Z', correlationId: null }]
    })

    const eventos = await getEventosRecorridos({ correlationId: 'cid-abc' })

    expect(notifApi.eventLog).toHaveBeenCalledWith({ correlationId: 'cid-abc' })
    expect(eventos[0].entidad).toBe('mesa')
    expect(eventos[0].correlationId).toBeNull()
  })

  it('devuelve lista vacía si el event-log no trae datos', async () => {
    notifApi.eventLog.mockResolvedValue({ datos: null })
    expect(await getEventosRecorridos()).toEqual([])
  })
})

describe('DLQ real', () => {
  it('normaliza id, cola, error y fecha, y saca el tipo del payload', async () => {
    adminApi.dlq.mockResolvedValue({ datos: EN_COLA })

    const { mensajes } = await getDlq()

    expect(mensajes).toHaveLength(2)
    expect(mensajes[0]).toMatchObject({ id: 7, tipo: 'solicitud_creada', cola: 'tfinder.notif.dlq', error: 'Connection timed out' })
    expect(mensajes[0].fecha).toContain('2026')
    expect(mensajes[0].payload).toEqual({ tipo: 'solicitud_creada', id: 3 })
  })

  it('parsea el payload cuando el backend lo manda como texto JSON', async () => {
    adminApi.dlq.mockResolvedValue({ datos: [EN_COLA[1]] })
    const { mensajes } = await getDlq()
    expect(mensajes[0].tipo).toBe('mesa_abierta')
  })

  it('no inventa un tipo de mensaje cuando el payload no lo trae', async () => {
    adminApi.dlq.mockResolvedValue({ datos: [{ id: 9, cola: 'tfinder.notif.dlq', payload: null, error: 'x', fecha: null }] })
    const { mensajes } = await getDlq()
    expect(mensajes[0].tipo).toBe('tfinder.notif.dlq')
    expect(mensajes[0].fecha).toBe('—')
  })

  it('devuelve la cola vacía sin inventar mensajes', async () => {
    adminApi.dlq.mockResolvedValue({ datos: null })
    expect(await getDlq()).toEqual({ mensajes: [] })
  })

  it('reintenta contra el endpoint real y devuelve la cola de destino', async () => {
    adminApi.reintentarDlq.mockResolvedValue({ datos: { ok: true, id: 7, cola: 'tfinder.notif' } })
    expect(await reintentarMensaje(7)).toEqual({ id: 7, cola: 'tfinder.notif' })
    expect(adminApi.reintentarDlq).toHaveBeenCalledWith(7)
  })

  it('propaga el error del backend al reintentar', async () => {
    adminApi.reintentarDlq.mockRejectedValue(new Error('Ese mensaje ya salió de la cola de fallidos.'))
    await expect(reintentarMensaje('inexistente')).rejects.toThrow('cola de fallidos')
  })

  it('descarta un mensaje contra el DELETE real', async () => {
    adminApi.descartarDlq.mockResolvedValue({ status: 200, datos: { ok: true, id: 7 } })
    expect(await descartarMensaje(7)).toEqual({ id: 7 })
    expect(adminApi.descartarDlq).toHaveBeenCalledWith(7)
  })

  it('drena la cola con un DELETE por mensaje y reporta el progreso', async () => {
    adminApi.dlq.mockResolvedValue({ datos: EN_COLA })
    adminApi.descartarDlq.mockResolvedValue({ status: 200, datos: { ok: true } })

    const progreso = []
    const resultado = await drenarCola({ alProgresar: (p) => progreso.push(p) })

    expect(adminApi.descartarDlq.mock.calls.map((c) => c[0])).toEqual([7, 8])
    expect(resultado).toEqual({ total: 2, hechos: 2 })
    expect(progreso).toEqual([
      { hechos: 1, total: 2, id: 7 },
      { hechos: 2, total: 2, id: 8 }
    ])
  })

  it('no manda ningún DELETE cuando la cola ya está vacía', async () => {
    adminApi.dlq.mockResolvedValue({ datos: [] })
    expect(await drenarCola()).toEqual({ total: 0, hechos: 0 })
    expect(adminApi.descartarDlq).not.toHaveBeenCalled()
  })

  it('corta el drenaje y propaga el error si un DELETE falla', async () => {
    adminApi.dlq.mockResolvedValue({ datos: EN_COLA })
    adminApi.descartarDlq
      .mockResolvedValueOnce({ status: 200, datos: { ok: true } })
      .mockRejectedValueOnce(new Error('no autorizado'))
    await expect(drenarCola()).rejects.toThrow('no autorizado')
    expect(adminApi.descartarDlq).toHaveBeenCalledTimes(2)
  })
})

describe('resiliencia derivada del estado real', () => {
  it('cierra el breaker cuando mesas-api está listo', async () => {
    adminApi.live.mockImplementation(porEndpoint({ mesas: vivo() })('live'))
    adminApi.ready.mockImplementation(porEndpoint({ mesas: vivo() })('ready'))
    adminApi.dlq.mockResolvedValue({ datos: [] })

    const r = await getResiliencia()

    expect(r).toMatchObject({ breakerEstado: 'CERRADO', alcanzable: true, ready: 'listo', dlqEnCola: 0, servicio: 'mesas-api' })
    expect(r.ajustes.length).toBeGreaterThan(0)
  })

  it('abre el breaker y cuenta la DLQ cuando rabbitmq está caído', async () => {
    const degradado = vivo('degradado', { postgres: true, redis: true, rabbitmq: false })
    adminApi.live.mockImplementation(porEndpoint({ mesas: degradado })('live'))
    adminApi.ready.mockImplementation(porEndpoint({ mesas: degradado })('ready'))
    adminApi.dlq.mockResolvedValue({ datos: EN_COLA })

    const r = await getResiliencia()

    expect(r.breakerEstado).toBe('ABIERTO')
    expect(r.dlqEnCola).toBe(2)
    expect(r.dependencias.find((d) => d.clave === 'rabbitmq').ok).toBe(false)
  })

  it('reporta sin datos del operador cuando mesas-api no responde', async () => {
    adminApi.live.mockImplementation(porEndpoint({ mesas: caido('mesas-api no responde') })('live'))
    adminApi.ready.mockImplementation(porEndpoint({ mesas: caido('mesas-api no responde') })('ready'))
    adminApi.dlq.mockResolvedValue({ datos: [] })

    const r = await getResiliencia()

    expect(r).toMatchObject({ breakerEstado: 'ABIERTO', alcanzable: false, ready: 'sin_datos' })
    expect(r.detalle).toBe('mesas-api no responde')
  })
})
