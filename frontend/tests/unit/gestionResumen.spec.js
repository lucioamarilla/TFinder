// Ciclo 10 · D-12: GestionView habla el contrato real de sesiones
// (abierta|cerrada + fecha) y muestra datos reales de mesa (GM, ocupacion).
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

const USUARIO = {
  access_token: 'tf-acc',
  user: { id: 9, sub: '9', email: 'gm@tfinder.dev', rol: 'director', nombre: 'GM Ostirion', iniciales: 'GO', titulo: 'Director de Juego' },
}

const MESA_77 = { id: 77, nombre: 'Cripta de Ustalav', sistema: 'pf1e', gm_id: 9, gm_nombre: 'GM Ostirion', descripcion: 'Horror gotico.', tono: 'Terror', horario: 'Viernes 20:00', estado: 'abierta', nivel_inicial: 5, jugadores_actuales: 2, jugadores_max: 5, fecha_creacion: '2026-11-01' }

const SESIONES = [
  { id: 1, mesa_id: 77, estado: 'cerrada', fecha: '2026-11-13T20:00:00', confirmada_at: '2026-11-14T08:00:00' },
  { id: 2, mesa_id: 77, estado: 'abierta', fecha: '2026-11-20T20:00:00', confirmada_at: null },
]

describe('GestionView sobre el contrato real (D-12)', () => {
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

  it('muestra la sesion ABIERTA por fecha, sin TypeError ni campos inventados', async () => {
    vi.resetModules()
    vi.stubEnv('VITE_API_MODE', 'api')
    localStorage.setItem('tfinder-sesion', JSON.stringify(USUARIO))
    fetchMock.mockImplementation((url) => {
      const u = new URL(url)
      if (u.pathname === '/api/v1/mesas/77') return Promise.resolve(jsonRes(200, MESA_77))
      if (u.pathname === '/api/v1/wiki') return Promise.resolve(jsonRes(200, { total: 2 }))
      if (u.pathname === '/api/v1/mesas/77/sesiones') return Promise.resolve(jsonRes(200, SESIONES))
      if (u.pathname === '/api/v1/mesas/77/miembros') return Promise.resolve(jsonRes(200, { miembros: [{ id: 9, nombre: 'GM Ostirion', email: 'gm@tfinder.dev', rol: 'master' }] }))
      if (u.pathname === '/api/v1/mesas/mias') return Promise.resolve(jsonRes(200, [{ ...MESA_77, mi_rol: 'master' }]))
      return Promise.resolve(jsonRes(200, []))
    })
    await Promise.all([
      import('@/api/endpoints'),
      import('@/services/mesas'),
      import('@/services/wiki'),
      import('@/services/sesiones'),
      import('@/services/jugadores'),
      import('@/services/membresias'),
    ])
    const { default: Layout } = await import('@/layouts/GestionLayout.vue')
    const { default: Vista } = await import('@/views/gestion/GestionView.vue')
    const { routes: nested } = await import('@/router/index.js')

    // rama de gestion REAL (layout + shell proveen contexto) y apuntadas a div
    const gestionRama = { ...nested.find((r) => r.path === '/mesas/:id/gestion') }
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { ...gestionRama, children: [{ path: '', component: Vista }] },
        { path: '/mis-mesas', component: { template: '<div />' } },
        { path: '/mesas/:id/editar', component: { template: '<div />' } },
        { path: '/mesas/:id/calendario', component: { template: '<div />' } },
        { path: '/mesas/:id', component: { template: '<div />' } },
      ],
    })
    await router.push('/mesas/77/gestion')
    const w = mount(Layout, { global: { plugins: [router] } })
    await flushPromises()
    await flushPromises()
    const texto = w.text()
    expect(texto).not.toContain('Aldren Valeros')
    expect(texto).toContain('GM Ostirion')
    expect(texto).toContain('2/5')
    expect(texto).toContain('ABIERTA')
    expect(texto).toContain('20/11/2026')
    expect(texto).not.toContain('undefined')
    expect(texto).not.toContain('NaN')
  })
})
