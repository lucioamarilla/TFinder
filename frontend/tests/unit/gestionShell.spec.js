// Ciclo 2 · D-02: MesaGestionShell no puede ser todo-o-nada. La mesa existe si
// getMesa responde; cada dato secundario degrada su sección con valores neutros.
// Además: las membresías exponen rol 'master' (no 'gm'), así que esGM debe
// reconocerlo — si no, el GM ve un panel sin acciones de dirección.
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'

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
  descripcion: 'Horror gotico en el castillo de Illmarsh.',
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
  { id: 2, mesa_id: 77, estado: 'cerrada', fecha: '2026-11-13T20:00:00', confirmada_at: '2026-11-14T08:00:00' },
]

const MIEMBROS = { miembros: [{ id: 9, nombre: 'GM Ostirion', email: 'gm@tfinder.dev', rol: 'master' }, { id: 3, nombre: 'Ana Votera', email: 'ana@tfinder.dev', rol: 'jugador' }] }

function cuerpoDefectuoso() {
  return { mesa: 200, wiki: 403, sesiones: 403, miembros: 403, mias: 403 }
}

function cuerpoCompleto() {
  return { mesa: 200, wiki: 200, sesiones: 200, miembros: 200, mias: 200, wikiBody: { carpetas: [], paginas: [], total: 3 }, sesionesBody: SESIONES, miembrosBody: MIEMBROS, miasBody: [{ ...MESA_77, mi_rol: 'master' }] }
}

describe('MesaGestionShell con cargas parciales (D-02)', () => {
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

  async function montar(cuerpo, usuario) {
    vi.resetModules()
    vi.stubEnv('VITE_API_MODE', 'api')
    if (usuario) localStorage.setItem('tfinder-sesion', JSON.stringify(usuario))
    fetchMock.mockImplementation((url) => {
      const u = new URL(url)
      if (u.pathname === '/api/v1/mesas/77') return Promise.resolve(jsonRes(cuerpo.mesa, cuerpo.mesa === 200 ? MESA_77 : { error: { codigo: 404, mensaje: 'Mesa no encontrada' } }))
      if (u.pathname === '/api/v1/wiki') return Promise.resolve(jsonRes(cuerpo.wiki, cuerpo.wiki === 200 ? (cuerpo.wikiBody ?? { total: 0 }) : { error: { codigo: 403, mensaje: 'Sin permisos' } }))
      if (u.pathname === '/api/v1/mesas/77/sesiones') return Promise.resolve(jsonRes(cuerpo.sesiones, cuerpo.sesiones === 200 ? (cuerpo.sesionesBody ?? []) : { error: { codigo: 403, mensaje: 'Sin permisos' } }))
      if (u.pathname === '/api/v1/mesas/77/miembros') return Promise.resolve(jsonRes(cuerpo.miembros, cuerpo.miembros === 200 ? (cuerpo.miembrosBody ?? { miembros: [] }) : { error: { codigo: 403, mensaje: 'No eres miembro' } }))
      if (u.pathname === '/api/v1/mesas/mias') return Promise.resolve(jsonRes(cuerpo.mias, cuerpo.mias === 200 ? (cuerpo.miasBody ?? []) : { error: { codigo: 403, mensaje: 'Sin sesion' } }))
      return Promise.resolve(jsonRes(200, []))
    })
    // warm-up: el runner de vitest no resuelve el primer import dinamico
    // evaluado unicamente desde un hook asincrono sin grafico previo.
    await Promise.all([
      import('@/api/endpoints'),
      import('@/services/mesas'),
      import('@/services/wiki'),
      import('@/services/sesiones'),
      import('@/services/jugadores'),
      import('@/services/membresias'),
    ])
    const { default: Shell } = await import('@/components/mesa/MesaGestionShell.vue')
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/mesas/:id/gestion', component: Shell, props: true },
        { path: '/mis-mesas', component: { template: '<div />' } },
        { path: '/mesas/:id/editar', component: { template: '<div />' } },
      ],
    })
    await router.push('/mesas/77/gestion')
    const w = mount(Shell, { props: { mesaId: '77' }, global: { plugins: [router] } })
    await flushPromises()
    await flushPromises()
    return w
  }

  const sesionGM = () => ({
    access_token: 'tf-acc',
    user: { id: 9, sub: '9', email: 'gm@tfinder.dev', rol: 'director', nombre: 'GM Ostirion', iniciales: 'GO', titulo: 'Director de Juego' },
  })

  it('con TODAS las llamadas secundarias en 403, la mesa se muestra con pestañas (no todo-o-nada)', async () => {
    const w = await montar(cuerpoDefectuoso(), sesionGM())
    expect(w.text()).toContain('Cripta de Ustalav')
    expect(w.text()).not.toContain('No encontramos la mesa')
    expect(w.text()).toContain('Resumen')
  })

  it('ocupacion degrada a mesa.jugadores/mesa.plazas cuando miembros falla', async () => {
    const w = await montar(cuerpoDefectuoso(), sesionGM())
    expect(w.text()).toContain('1/5')
  })

  it('todo responde: cuenta wiki, sesiones y ocupacion reales + acciones GM con rol master', async () => {
    const w = await montar(cuerpoCompleto(), sesionGM())
    expect(w.text()).toContain('Editar mesa') // esGM reconoce mi_rol 'master'
    const nav = w.text()
    expect(nav).toContain('2/5') // ocupacion real: 2 miembros de 5 plazas
    expect(nav).not.toMatch(/undefined/)
    expect(nav).not.toMatch(/3 de null/)
    expect(nav).toMatch(/3/) // wiki total
  })

  it('mesa 404: el shell sí muestra no-encontrada', async () => {
    const cuerpo = { ...cuerpoDefectuoso(), mesa: 404 }
    const w = await montar(cuerpo, sesionGM())
    expect(w.text()).toContain('No encontramos la mesa')
  })
})
