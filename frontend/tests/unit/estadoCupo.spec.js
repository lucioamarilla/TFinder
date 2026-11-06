// Ciclo 8 · D-09/D-10: un UNICO formato de estado (helpers sobre el literal
// del contrato abierta|cerrada) y cupo/plazas unificados (nunca undefined).
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

const MESA_CERRADA = { id: 77, nombre: 'Cripta de Ustalav', sistema: 'pf1e', gm_id: 9, gm_nombre: 'GM Ostirion', descripcion: 'x', tono: 'Terror', horario: 'V', estado: 'cerrada', nivel_inicial: 5, jugadores_actuales: 5, jugadores_max: 5, fecha_creacion: '2026-11-01' }
const MESA_ABIERTA = { ...MESA_CERRADA, estado: 'abierta', jugadores_actuales: 1 }

describe('helpers de estado y cupo (D-09)', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.stubEnv('VITE_API_MODE', 'api')
  })

  afterEach(() => {
    vi.unstubAllEnvs()
    vi.unstubAllGlobals()
    vi.resetModules()
  })

  it('normalizarMesa expone plazas y helpers aceptan ambos formatos', async () => {
    await import('@/services/mesas')
    const { normalizarMesa, esMesaAbierta, esMesaCerrada, cupoDe, ocupacionDe } = await import('@/services/mesas')
    const n = normalizarMesa(MESA_CERRADA)
    expect(n.plazas).toBe(5)
    expect(esMesaCerrada(n)).toBe(true)
    expect(esMesaCerrada({ estado: 'cerrada' })).toBe(true)
    expect(esMesaAbierta({ estado: 'Abierta' })).toBe(true)
    expect(cupoDe(n)).toBe(5)
    expect(ocupacionDe(n)).toBe(5)
  })
})

describe('MesaDetailJugadorView · cerrada (D-09)', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  afterEach(() => {
    vi.unstubAllEnvs()
    vi.unstubAllGlobals()
    vi.resetModules()
  })

  it('mesa cerrada se anuncia CERRADA y no ofrece solicitar unión', async () => {
    vi.resetModules()
    vi.stubEnv('VITE_API_MODE', 'api')
    localStorage.setItem('tfinder-sesion', JSON.stringify(USUARIO))
    const stub = (url) => {
      const u = new URL(url)
      if (u.pathname === '/api/v1/mesas/77') return Promise.resolve(jsonRes(200, MESA_CERRADA))
      return Promise.resolve(jsonRes(200, []))
    }
    vi.stubGlobal('fetch', vi.fn(stub))
    await Promise.all([import('@/api/endpoints'), import('@/services/mesas'), import('@/services/jugadores')])
    const { default: Vista } = await import('@/views/MesaDetailJugadorView.vue')
    const router = createRouter({ history: createMemoryHistory(), routes: [{ path: '/mesas/:id', component: Vista, props: true }, { path: '/mesas', component: { template: '<div />' } }, { path: '/login', component: { template: '<div />' } }, { path: '/wiki', component: { template: '<div />' } }] })
    await router.push('/mesas/77')
    const w = mount(Vista, { props: { id: '77' }, global: { plugins: [router] } })
    await flushPromises()
    await flushPromises()
    expect(w.text()).toContain('Cerrada')
    const boton = w.findAll('button').find((b) => b.text().includes('Solicitar'))
    expect(boton?.attributes('disabled')).toBeDefined()
  })
})

describe('MesaDetailGmView · cupo plazas (D-10)', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  afterEach(() => {
    vi.unstubAllEnvs()
    vi.unstubAllGlobals()
    vi.resetModules()
  })

  async function montarGm(mesaData) {
    vi.resetModules()
    vi.stubEnv('VITE_API_MODE', 'api')
    localStorage.setItem('tfinder-sesion', JSON.stringify(USUARIO))
    const stub = (url) => {
      const u = new URL(url)
      if (u.pathname === '/api/v1/mesas/77') return Promise.resolve(jsonRes(200, mesaData))
      if (u.pathname === '/api/v1/mesas/77/miembros') return Promise.resolve(jsonRes(200, { miembros: [{ id: 9, nombre: 'GM', email: 'gm@tfinder.dev' }, { id: 3, nombre: 'Ana', email: 'ana@tfinder.dev' }] }))
      return Promise.resolve(jsonRes(200, []))
    }
    vi.stubGlobal('fetch', vi.fn(stub))
    await Promise.all([import('@/api/endpoints'), import('@/services/mesas'), import('@/services/jugadores')])
    const { default: Vista } = await import('@/views/MesaDetailGmView.vue')
    const router = createRouter({ history: createMemoryHistory(), routes: [{ path: '/mesas/:id/gm', component: Vista, props: true }, { path: '/mesas', component: { template: '<div />' } }, { path: '/mesas/:id/sesion', component: { template: '<div />' } }, { path: '/wiki/nueva', component: { template: '<div />' } }] })
    await router.push('/mesas/77/gm')
    const w = mount(Vista, { props: { id: '77' }, global: { plugins: [router] } })
    await flushPromises()
    await flushPromises()
    return w
  }

  it('abierta: asientos XX de plazas reales con vacantes positivas (sin undefined/NaN)', async () => {
    const w = await montarGm(MESA_ABIERTA)
    expect(w.text()).not.toContain('undefined')
    expect(w.text()).not.toContain('NaN')
    expect(w.text()).toContain('2/5')
    expect(w.text()).toContain('3') // vacantes
    expect(w.text()).toContain('Abierta')
  })

  it('cerrada: tag Cerrada + acción Reabrir mesa', async () => {
    const w = await montarGm(MESA_CERRADA)
    expect(w.text()).not.toContain('undefined')
    expect(w.text()).toContain('Cerrada')
    expect(w.text()).toContain('Reabrir mesa')
  })

  it('toggleEstado: Click Cerrar mesa envia PUT estado cerrada y actualiza desde la respuesta', async () => {
    vi.resetModules()
    vi.stubEnv('VITE_API_MODE', 'api')
    localStorage.setItem('tfinder-sesion', JSON.stringify(USUARIO))
    const stub = vi.fn((url, opts = {}) => {
      const u = new URL(url)
      if (u.pathname === '/api/v1/mesas/77' && opts.method === 'PUT') return Promise.resolve(jsonRes(200, { ...MESA_ABIERTA, estado: 'cerrada' }))
      if (u.pathname === '/api/v1/mesas/77') return Promise.resolve(jsonRes(200, MESA_ABIERTA))
      if (u.pathname === '/api/v1/mesas/77/miembros') return Promise.resolve(jsonRes(200, { miembros: [{ id: 9, nombre: 'GM', email: 'gm@tfinder.dev' }] }))
      return Promise.resolve(jsonRes(200, []))
    })
    vi.stubGlobal('fetch', stub)
    await Promise.all([import('@/api/endpoints'), import('@/services/mesas'), import('@/services/jugadores')])
    const { default: Vista } = await import('@/views/MesaDetailGmView.vue')
    const router = createRouter({ history: createMemoryHistory(), routes: [{ path: '/mesas/:id/gm', component: Vista, props: true }, { path: '/mesas', component: { template: '<div />' } }, { path: '/mesas/:id/sesion', component: { template: '<div />' } }, { path: '/wiki/nueva', component: { template: '<div />' } }] })
    await router.push('/mesas/77/gm')
    const w = mount(Vista, { props: { id: '77' }, global: { plugins: [router] } })
    await flushPromises()
    await flushPromises()
    const boton = w.findAll('button').find((b) => b.text().includes('Cerrar mesa'))
    await boton.trigger('click')
    await flushPromises()
    const llamada = stub.mock.calls.find(([u, o]) => new URL(u).pathname === '/api/v1/mesas/77' && o?.method === 'PUT')
    expect(JSON.parse(llamada?.[1]?.body).estado).toBe('cerrada')
    expect(w.text()).toContain('Cerrada')
  })

  it('guardar: Guardar cambios envia PUT con nombre/horario/cupo', async () => {
    vi.resetModules()
    vi.stubEnv('VITE_API_MODE', 'api')
    localStorage.setItem('tfinder-sesion', JSON.stringify(USUARIO))
    const stub = vi.fn((url, opts = {}) => {
      const u = new URL(url)
      if (u.pathname === '/api/v1/mesas/77' && opts.method === 'PUT') return Promise.resolve(jsonRes(200, MESA_ABIERTA))
      if (u.pathname === '/api/v1/mesas/77') return Promise.resolve(jsonRes(200, MESA_ABIERTA))
      if (u.pathname === '/api/v1/mesas/77/miembros') return Promise.resolve(jsonRes(200, { miembros: [{ id: 9, nombre: 'GM', email: 'gm@tfinder.dev' }] }))
      return Promise.resolve(jsonRes(200, []))
    })
    vi.stubGlobal('fetch', stub)
    await Promise.all([import('@/api/endpoints'), import('@/services/mesas'), import('@/services/jugadores')])
    const { default: Vista } = await import('@/views/MesaDetailGmView.vue')
    const router = createRouter({ history: createMemoryHistory(), routes: [{ path: '/mesas/:id/gm', component: Vista, props: true }, { path: '/mesas', component: { template: '<div />' } }, { path: '/mesas/:id/sesion', component: { template: '<div />' } }, { path: '/wiki/nueva', component: { template: '<div />' } }] })
    await router.push('/mesas/77/gm')
    const w = mount(Vista, { props: { id: '77' }, global: { plugins: [router] } })
    await flushPromises()
    await flushPromises()
    await w.find('#e-nombre').setValue('Cripta de Ustalav II')
    await w.find('[data-test="guardar-detalle"]').trigger('click')
    await flushPromises()
    const llamada = stub.mock.calls.find(([u, o]) => new URL(u).pathname === '/api/v1/mesas/77' && o?.method === 'PUT')
    const cuerpo = JSON.parse(llamada?.[1]?.body)
    expect(cuerpo.nombre).toBe('Cripta de Ustalav II')
    expect(cuerpo).toHaveProperty('jugadores_max')
  })
})
