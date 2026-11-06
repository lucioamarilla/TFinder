// Ciclo 4 · D-05/D-14: dia y hora reales (nunca labels), ISO aceptado por el
// backend, marcas del calendario por fecha real, capacidad desde la mesa
// (nunca 'de null') y voto propio real (mi_voto del backend, inferencia por
// nombre como contingencia).
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'

function jsonRes(status, body) {
  return {
    ok: status < 400,
    status,
    headers: Object.fromEntries([['content-type', 'application/json']]),
    json: async () => body,
  }
}

const MESA_77 = {
  id: 77,
  nombre: 'Cripta de Ustalav',
  sistema: 'pf1e',
  gm_id: 9,
  gm_nombre: 'GM Ostirion',
  descripcion: 'Horror gotico.',
  tono: 'Terror',
  horario: 'Viernes 20:00',
  estado: 'abierta',
  nivel_inicial: 5,
  jugadores_actuales: 1,
  jugadores_max: 5,
  fecha_creacion: '2026-11-01',
}

const SESIONES = [
  { id: 1, mesa_id: 77, estado: 'abierta', fecha: '2026-11-20T20:00:00', confirmada_at: null },
]

const FECHAS = [
  { id: 5, estado: 'activa', propuesta: '2026-11-15T18:00:00', a_favor_nombres: 'Ana Votera', en_contra_nombres: '' },
]

const USUARIO_JUGADOR = {
  access_token: 'tf-acc',
  user: { id: 3, sub: '3', email: 'ana@tfinder.dev', rol: 'usuario', nombre: 'Ana Votera', iniciales: 'AV', titulo: 'Aventurero & Cronista' },
}

const USUARIO_GM = {
  access_token: 'tf-acc',
  user: { id: 9, sub: '9', email: 'gm@tfinder.dev', rol: 'director', nombre: 'GM Ostirion', iniciales: 'GO', titulo: 'Director de Juego' },
}

function stubCompleto(extra = {}) {
  return (url, opts = {}) => {
    const u = new URL(url)
    const metodo = opts?.method ?? 'GET'
    if (u.pathname === '/api/v1/mesas/77') return Promise.resolve(jsonRes(200, MESA_77))
    if (u.pathname === '/api/v1/wiki') return Promise.resolve(jsonRes(200, { total: 0 }))
    if (u.pathname === '/api/v1/mesas/77/sesiones') return Promise.resolve(jsonRes(200, SESIONES))
    if (u.pathname === '/api/v1/mesas/77/miembros') return Promise.resolve(jsonRes(200, { miembros: [{ id: 9, nombre: 'GM Ostirion', email: 'gm@tfinder.dev', rol: 'master' }] }))
    if (u.pathname === '/api/v1/mesas/mias') return Promise.resolve(jsonRes(200, [{ ...MESA_77, mi_rol: 'master' }]))
    if (u.pathname === '/api/v1/mesas/77/fechas' && metodo === 'POST') {
      return Promise.resolve(jsonRes(201, { ...FECHAS[0] }))
    }
    if (u.pathname === '/api/v1/mesas/77/fechas') return Promise.resolve(jsonRes(200, FECHAS))
    return Promise.resolve(jsonRes(200, []))
  }
}

describe('votaciones.js · servicio (D-05/D-14)', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.stubEnv('VITE_API_MODE', 'api')
  })

  afterEach(() => {
    vi.unstubAllEnvs()
    vi.unstubAllGlobals()
    vi.resetModules()
  })

  it('proponerFecha construye ISO con la hora elegida (no un label humano)', async () => {
    localStorage.setItem('tfinder-sesion', JSON.stringify(USUARIO_GM))
    const fetchMock = vi.fn(stubCompleto())
    vi.stubGlobal('fetch', fetchMock)
    await Promise.all([import('@/api/endpoints'), import('@/services/mesas')])
    const { proponerFecha } = await import('@/services/votaciones')
    const p = await proponerFecha('77', { fecha: '2026-11-15', hora: '18:00' })
    const llamada = fetchMock.mock.calls.find(([u, o]) => new URL(u).pathname === '/api/v1/mesas/77/fechas' && o?.method === 'POST')
    expect(JSON.parse(llamada?.[1]?.body).propuesta).toBe('2026-11-15T18:00:00')
    expect(p.fecha).toBe('2026-11-15T18:00:00')
  })

  it('proponerFecha sin hora propone las 20:00 por omision', async () => {
    localStorage.setItem('tfinder-sesion', JSON.stringify(USUARIO_GM))
    const fetchMock = vi.fn(stubCompleto())
    vi.stubGlobal('fetch', fetchMock)
    await Promise.all([import('@/api/endpoints'), import('@/services/mesas')])
    const { proponerFecha } = await import('@/services/votaciones')
    await proponerFecha('77', { fecha: '2026-11-15' })
    const llamada = fetchMock.mock.calls.find(([u, o]) => new URL(u).pathname === '/api/v1/mesas/77/fechas' && o?.method === 'POST')
    expect(JSON.parse(llamada?.[1]?.body).propuesta).toBe('2026-11-15T20:00:00')
  })

  it('miVoto se toma del backend (mi_voto) o se infiere por nombre', async () => {
    localStorage.setItem('tfinder-sesion', JSON.stringify(USUARIO_JUGADOR))
    vi.stubGlobal('fetch', vi.fn((url) => {
      const u = new URL(url)
      if (u.pathname === '/api/v1/mesas/77/fechas') {
        return Promise.resolve(jsonRes(200, [
          { id: 1, estado: 'activa', propuesta: '2026-11-15T18:00:00', a_favor_nombres: 'Ana Votera', en_contra_nombres: '' },
          { id: 2, estado: 'activa', propuesta: '2026-11-16T18:00:00', a_favor_nombres: '', en_contra_nombres: 'Otro', mi_voto: 'en_contra' },
          { id: 3, estado: 'activa', propuesta: '2026-11-17T18:00:00', a_favor_nombres: '', en_contra_nombres: '' },
        ]))
      }
      return Promise.resolve(jsonRes(200, []))
    }))
    await Promise.all([import('@/api/endpoints'), import('@/services/mesas')])
    const { getVotaciones } = await import('@/services/votaciones')
    const lista = await getVotaciones('77')
    expect(lista.find((v) => v.id === 1).miVoto).toBe('favor') // inferido por nombre
    expect(lista.find((v) => v.id === 2).miVoto).toBe('contra') // del backend
    expect(lista.find((v) => v.id === 3).miVoto).toBeNull()
  })
})

describe('CalendarioView de gestion (D-05)', () => {
  let fetchMock

  beforeEach(() => {
    localStorage.clear()
    fetchMock = vi.fn()
    vi.stubGlobal('fetch', fetchMock)
  })

  afterEach(() => {
    vi.unstubAllEnvs()
    vi.unstubAllGlobals()
    vi.resetModules()
  })

  async function montar(usuario = USUARIO_GM) {
    vi.resetModules()
    vi.stubEnv('VITE_API_MODE', 'api')
    localStorage.setItem('tfinder-sesion', JSON.stringify(usuario))
    fetchMock.mockImplementation(stubCompleto())
    await Promise.all([
      import('@/api/endpoints'),
      import('@/services/mesas'),
      import('@/services/wiki'),
      import('@/services/sesiones'),
      import('@/services/jugadores'),
      import('@/services/membresias'),
      import('@/services/votaciones'),
    ])
    const { crearRouterCompleto } = await import('../helpers/routerCompleto')
    const { default: Vista } = await import('@/views/gestion/CalendarioView.vue')
    const router = crearRouterCompleto()
    await router.push('/mesas/77/gestion/calendario')
    const w = mount(Vista, { props: { mesaId: '77' }, global: { plugins: [router] } })
    await flushPromises()
    await flushPromises()
    return w
  }

  it('quorum con capacidad real de la mesa (nunca "de null")', async () => {
    const w = await montar()
    expect(w.text()).toContain('3 de 5')
    expect(w.text()).not.toContain('de null')
  })

  it('marca el dia de una sesion/propuesta real por su fecha (no selloNum)', async () => {
    const w = await montar()
    const dia20 = w.find('[data-celda="20"]')
    const dia15 = w.find('[data-celda="15"]')
    expect(dia20.text()).toContain('SESIÓN')
    expect(dia15.text()).toContain('PROPUESTA')
  })

  it('elige dia y hora con inputs y envia ISO real (no label)', async () => {
    const w = await montar()
    await w.find('[data-test="btn-abrir-proponer"]').trigger('click')
    await flushPromises()
    await w.find('[data-test="input-fecha"]').setValue('2026-11-15')
    await w.find('[data-test="input-hora"]').setValue('18:00')
    await w.find('[data-test="btn-proponer"]').trigger('submit')
    await flushPromises()
    await flushPromises()
    const llamada = fetchMock.mock.calls.find(([u, o]) => new URL(u).pathname === '/api/v1/mesas/77/fechas' && o?.method === 'POST')
    expect(llamada).toBeTruthy()
    expect(JSON.parse(llamada?.[1]?.body).propuesta).toBe('2026-11-15T18:00:00')
  })
})

describe('MesaCalendarioView (calendario del jugador) (D-05)', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.stubEnv('VITE_API_MODE', 'api')
  })

  afterEach(() => {
    vi.unstubAllEnvs()
    vi.unstubAllGlobals()
    vi.resetModules()
  })

  it('el GM elige dia + hora y el POST lleva ISO con la hora', async () => {
    localStorage.setItem('tfinder-sesion', JSON.stringify(USUARIO_GM))
    const fetchStub = vi.fn((url, opts = {}) => stubCompleto()(url, opts))
    vi.stubGlobal('fetch', fetchStub)
    await Promise.all([
      import('@/api/endpoints'),
      import('@/services/mesas'),
      import('@/services/wiki'),
      import('@/services/sesiones'),
      import('@/services/jugadores'),
      import('@/services/membresias'),
      import('@/services/votaciones'),
    ])
    const { crearRouterCompleto } = await import('../helpers/routerCompleto')
    const { default: Vista } = await import('@/views/MesaCalendarioView.vue')
    const router = crearRouterCompleto()
    await router.push('/mesas/77/calendario')
    const w = mount(Vista, { props: { mesaId: '77' }, global: { plugins: [router] } })
    await flushPromises()
    await flushPromises()
    await w.find('[data-test="input-fecha"]').setValue('2026-11-15')
    await w.find('[data-test="input-hora"]').setValue('18:00')
    await w.find('[data-test="btn-proponer"]').trigger('submit')
    await flushPromises()
    await flushPromises()
    const posts = fetchStub.mock.calls.filter(([u, o]) => new URL(u).pathname === '/api/v1/mesas/77/fechas' && o?.method === 'POST')
    expect(posts.length).toBe(1)
    expect(JSON.parse(posts[0][1].body).propuesta).toBe('2026-11-15T18:00:00')
  })

  it('el voto del jugador aparece marcado (aria-pressed) con miVoto real', async () => {
    localStorage.setItem('tfinder-sesion', JSON.stringify(USUARIO_JUGADOR))
    vi.stubGlobal('fetch', vi.fn(stubCompleto()))
    await Promise.all([
      import('@/api/endpoints'),
      import('@/services/mesas'),
      import('@/services/wiki'),
      import('@/services/sesiones'),
      import('@/services/jugadores'),
      import('@/services/membresias'),
      import('@/services/votaciones'),
    ])
    const { crearRouterCompleto } = await import('../helpers/routerCompleto')
    const { default: Vista } = await import('@/views/MesaCalendarioView.vue')
    const router = crearRouterCompleto()
    await router.push('/mesas/77/calendario')
    const w = mount(Vista, { props: { mesaId: '77' }, global: { plugins: [router] } })
    await flushPromises()
    await flushPromises()
    const favor = w.find('[data-test="voto-favor"]')
    expect(favor.attributes('aria-pressed')).toBe('true')
  })
})
