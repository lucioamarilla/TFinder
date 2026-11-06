// Ciclo 3 · D-04: SesionesView debe basarse en SesionOut real
// ({id, estado: abierta|cerrada, fecha, confirmada_at}); no puede crashear con
// s.numero (#30), no puede filtrar estados confirmada/borrador/tentativa y sus
// enlaces deben resolver a /mesas/:id/gestion/sesiones/:sid/{qr,diario}.
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { crearRouterCompleto } from '../helpers/routerCompleto'

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
  { id: 1, mesa_id: 77, estado: 'cerrada', fecha: '2026-11-13T20:00:00', confirmada_at: '2026-11-14T08:00:00' },
  { id: 2, mesa_id: 77, estado: 'abierta', fecha: '2026-11-20T20:00:00', confirmada_at: null },
]

const USUARIO = {
  access_token: 'tf-acc',
  user: { id: 9, sub: '9', email: 'gm@tfinder.dev', rol: 'director', nombre: 'GM Ostirion', iniciales: 'GO', titulo: 'Director de Juego' },
}

describe('SesionesView sobre SesionOut (D-04)', () => {
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

  async function montar(sesiones = SESIONES) {
    vi.resetModules()
    vi.stubEnv('VITE_API_MODE', 'api')
    localStorage.setItem('tfinder-sesion', JSON.stringify(USUARIO))
    fetchMock.mockImplementation((url) => {
      const u = new URL(url)
      if (u.pathname === '/api/v1/mesas/77') return Promise.resolve(jsonRes(200, MESA_77))
      if (u.pathname === '/api/v1/wiki') return Promise.resolve(jsonRes(200, { total: 0 }))
      if (u.pathname === '/api/v1/mesas/77/sesiones') return Promise.resolve(jsonRes(200, sesiones))
      if (u.pathname === '/api/v1/mesas/77/miembros') return Promise.resolve(jsonRes(200, { miembros: [{ id: 9, nombre: 'GM', email: 'gm@tfinder.dev', rol: 'master' }] }))
      if (u.pathname === '/api/v1/mesas/mias') return Promise.resolve(jsonRes(200, [{ ...MESA_77, mi_rol: 'master' }]))
      return Promise.resolve(jsonRes(200, []))
    })
    // warm-up de la grafica de servicios (primer import dinamico desde hook
    // asincrono no resuelve en el runner de vitest: ver gestionShell.spec)
    await Promise.all([
      import('@/api/endpoints'),
      import('@/services/mesas'),
      import('@/services/wiki'),
      import('@/services/sesiones'),
      import('@/services/jugadores'),
      import('@/services/membresias'),
    ])
    const { default: Vista } = await import('@/views/gestion/SesionesView.vue')
    const router = crearRouterCompleto()
    await router.push('/mesas/77/gestion/sesiones')
    const w = mount(Vista, { props: { mesaId: '77' }, global: { plugins: [router] } })
    await flushPromises()
    await flushPromises()
    return w
  }

  it('renderiza 2 sesiones sin TypeError de s.numero', async () => {
    const w = await montar()
    expect(w.findAll('[data-test="sesion-fila"]').length).toBe(2)
  })

  it('orden por fecha real: la sesion mas reciente (id 2, abierta) primero', async () => {
    const w = await montar()
    const filas = w.findAll('[data-test="sesion-fila"]')
    expect(filas[0].attributes('data-sesion-id')).toBe('2')
    expect(filas[0].attributes('data-estado')).toBe('abierta')
  })

  it('etiquetas de estado del contrato: ABIERTA / CERRADA', async () => {
    const w = await montar()
    expect(w.text()).toContain('ABIERTA')
    expect(w.text()).toContain('CERRADA')
    expect(w.text()).not.toContain('BORRADOR')
  })

  it('enlaces al diario y QR resuelven en el router (/gestion/sesiones/:sid/...)', async () => {
    const w = await montar()
    const hrefs = w.findAll('a').map((a) => a.attributes('href')).filter(Boolean)
    const diario = hrefs.find((h) => h.includes('/gestion/sesiones/2/diario'))
    const qr = hrefs.find((h) => h.includes('/gestion/sesiones/2/qr'))
    const bitacora = hrefs.find((h) => h.includes('/gestion/sesiones/1/bitacora'))
    expect(diario).toBeTruthy()
    expect(qr).toBeTruthy()
    expect(bitacora).toBeTruthy()
  })

  it('mesa sin sesiones: estado vacio amable y sin crasheo', async () => {
    const w = await montar([])
    expect(w.findAll('[data-test="sesion-fila"]').length).toBe(0)
    expect(w.text()).not.toContain('Mesa no encontrada')
  })
})
