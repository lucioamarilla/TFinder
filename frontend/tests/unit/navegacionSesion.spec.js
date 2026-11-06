// Ciclo 6 · D-03: la landing muestra la sesión (nombre/panel + cerrar sesión),
// sin enlaces muertos (bestiario/compendio). El panel móvil se abre desde un
// trigger real en el header (useShell.toggleMenu), y AppShell lo renderiza.
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

const stubsGenerales = () => (url, opts = {}) => {
  const u = new URL(url)
  if (u.pathname === '/api/v1/mesas') return Promise.resolve(jsonRes(200, [{ id: 77, nombre: 'Cripta de Ustalav', sistema: 'pf1e', estado: 'abierta', jugadores_actuales: 1, jugadores_max: 5, fecha_creacion: '2026-11-01', gm_nombre: 'GM Ostirion', horario: 'Viernes 20:00' }]))
  if (u.pathname === '/api/v1/feed') return Promise.resolve(jsonRes(200, []))
  if (u.pathname === '/api/v1/feed/comunidades') return Promise.resolve(jsonRes(200, []))
  if (u.pathname === '/api/v1/notificaciones') return Promise.resolve(jsonRes(200, []))
  if (u.pathname === '/api/v1/mesas/mias') return Promise.resolve(jsonRes(200, []))
  return Promise.resolve(jsonRes(200, []))
}

describe('LandingView · sesión visible (D-03)', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.stubEnv('VITE_API_MODE', 'api')
  })

  afterEach(() => {
    vi.unstubAllEnvs()
    vi.unstubAllGlobals()
    vi.resetModules()
  })

  async function montarLanding(usuario = USUARIO) {
    vi.resetModules()
    if (usuario) localStorage.setItem('tfinder-sesion', JSON.stringify(usuario))
    vi.stubGlobal('fetch', vi.fn(stubsGenerales()))
    await Promise.all([
      import('@/api/endpoints'),
      import('@/services/mesas'),
      import('@/services/feed'),
      import('@/services/notificaciones'),
      import('@/services/jugadores'),
      import('@/services/membresias'),
    ])
    const { default: Vista } = await import('@/views/LandingView.vue')
    const router = createRouter({ history: createMemoryHistory(), routes: [{ path: '/', component: Vista }, { path: '/login', component: { template: '<div />' } }, { path: '/registro', component: { template: '<div />' } }, { path: '/mesas', component: { template: '<div />' } }, { path: '/feed', component: { template: '<div />' } }, { path: '/perfil', component: { template: '<div />' } }] })
    await router.push('/')
    const w = mount(Vista, { global: { plugins: [router] } })
    await flushPromises()
    await flushPromises()
    return w
  }

  it('invitado: nav con iniciar sesión + crear cuenta (semilla existente)', async () => {
    const w = await montarLanding(null)
    expect(w.text()).toContain('Iniciar sesión')
    expect(w.text()).toContain('Crear cuenta')
  })

  it('autenticado: la landing reconoce la sesión (nombre/perfil + cerrar sesión)', async () => {
    const w = await montarLanding()
    expect(w.text()).toContain('Cerrar sesión')
    expect(w.find('[data-test="perfil-acceso"]').exists() || w.find('[data-test="cerrar-sesion-landing"]').exists()).toBe(true)
    expect(w.text()).toContain('GM Ostirion')
  })

  it('lautenticado: la landing no muestra iniciar sesión fijo', async () => {
    const w = await montarLanding()
    expect(w.text()).not.toContain('Iniciar sesión')
  })

  it('sin enlaces muertos a /bestiario ni /compendio', async () => {
    const w = await montarLanding(null)
    const hrefs = w.findAll('a').map((a) => a.attributes('href'))
    expect(hrefs.find((h) => (h || '').includes('bestiario'))).toBeFalsy()
    expect(hrefs.find((h) => (h || '').includes('compendio'))).toBeFalsy()
  })
})

describe('AppShell · trigger del menú móvil (D-03)', () => {
  let fetchMock

  beforeEach(() => {
    localStorage.clear()
    fetchMock = vi.fn()
    vi.stubGlobal('fetch', fetchMock)
    vi.stubEnv('VITE_API_MODE', 'api')
  })

  afterEach(() => {
    vi.unstubAllEnvs()
    vi.unstubAllGlobals()
    vi.resetModules()
  })

  async function montarShell(usuario = null) {
    vi.resetModules()
    if (usuario) localStorage.setItem('tfinder-sesion', JSON.stringify(usuario))
    fetchMock.mockImplementation(stubsGenerales())
    await Promise.all([
      import('@/api/endpoints'),
      import('@/services/mesas'),
      import('@/services/feed'),
      import('@/services/notificaciones'),
      import('@/services/jugadores'),
      import('@/services/membresias'),
    ])
    const { default: Shell } = await import('@/layouts/AppShell.vue')
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', component: { template: '<div />' } },
        { path: '/login', component: { template: '<div />' } },
        { path: '/registro', component: { template: '<div />' } },
        { path: '/mesas', component: { template: '<div />' } },
        { path: '/builds', component: { template: '<div />' } },
        { path: '/notificaciones', component: { template: '<div />' } },
        { path: '/perfil', component: { template: '<div />' } },
      ],
    })
    await router.push('/')
    const w = mount(Shell, { global: { plugins: [router], slots: { default: '<p data-slot>contenido</p>' } } })
    await flushPromises()
    return w
  }

  it('el header expone un trigger de menú móvil (hamburguesa)', async () => {
    const w = await montarShell()
    expect(w.find('[data-test="menu-movil"]').exists()).toBe(true)
  })

  it('al pulsar el trigger, el panel móvil se abre con la nav y cerrar sesión', async () => {
    const w = await montarShell(USUARIO)
    await w.find('[data-test="menu-movil"]').trigger('click')
    await flushPromises()
    const panel = w.find('[data-test="panel-movil"]')
    expect(panel.exists()).toBe(true)
    expect(w.text()).toContain('Cerrar sesión')
  })

  it('clic en el trigger con panel abierto lo cierra (toggle)', async () => {
    const w = await montarShell(USUARIO)
    await w.find('[data-test="menu-movil"]').trigger('click')
    await flushPromises()
    expect(w.find('[data-test="panel-movil"]').exists()).toBe(true)
    await w.find('[data-test="menu-movil"]').trigger('click')
    await flushPromises()
    expect(w.find('[data-test="panel-movil"]').exists()).toBe(false)
  })
})
