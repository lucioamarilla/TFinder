// Ciclo 14 · F09/D-15: consola admin REAL — eventos de sistema, DLQ
// (reintentar/descartar) y emails, contra notif-api con rol 'admin'.
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

const USUARIO_ADMIN = {
  access_token: 'tf-acc',
  user: { id: 1, sub: '1', email: 'admin@tfinder.dev', rol: 'admin', nombre: 'Admin TFinder', iniciales: 'AT', titulo: 'Moderación & Vigilancia' },
}

const DLQ = [
  { id: 1, cola: 'dlq.general', payload: { tipo: 'mesa.desconocida', mesa_id: 1 }, error: 'fallo simulado', fecha: '2026-11-06T10:00:00' },
]

const EVENTOS = [
  { id: 10, entidadTipo: 'mesa', entidadId: '77', accion: 'actualizada', usuarioId: '9', metadata: {}, ocurridoEn: '2026-11-06T09:00:00', correlationId: 'abc' },
]

const EMAILS = [
  { id: 3, destino: 'ana@tfinder.dev', asunto: 'Vuelta a la mesa', cuerpo: 'Hola', estado: 'fallido', error: 'SMTP caido' },
]

describe('services/admin · notif-api real (F09)', () => {
  let fetchMock

  beforeEach(() => {
    localStorage.clear()
    fetchMock = vi.fn((url, opts = {}) => {
      const u = new URL(url)
      if (u.pathname === '/api/v1/dlq' && opts.method === undefined) return Promise.resolve(jsonRes(200, DLQ))
      if (u.pathname === '/api/v1/dlq/1/reintentar') return Promise.resolve(jsonRes(200, { id: 1 }))
      if (u.pathname === '/api/v1/dlq/1') return Promise.resolve(jsonRes(204, null))
      if (u.pathname === '/api/v1/event-log') return Promise.resolve(jsonRes(200, EVENTOS))
      if (u.pathname === '/api/v1/emails') return Promise.resolve(jsonRes(200, EMAILS))
      return Promise.resolve(jsonRes(200, []))
    })
    vi.stubGlobal('fetch', fetchMock)
    vi.stubEnv('VITE_API_MODE', 'api')
    localStorage.setItem('tfinder-sesion', JSON.stringify(USUARIO_ADMIN))
  })

  afterEach(() => {
    vi.unstubAllEnvs()
    vi.unstubAllGlobals()
    vi.resetModules()
  })

  it('getDlq, reintentar y descartar hablan con las rutas reales', async () => {
    const adm = await import('@/services/admin')
    await adm.getDlq()
    await adm.reintentarDlq(1)
    await adm.descartarDlq(1)
    const metodos = fetchMock.mock.calls.map(([u, o]) => [new URL(u).pathname, o?.method ?? 'GET'])
    expect(metodos).toEqual([
      ['/api/v1/dlq', 'GET'],
      ['/api/v1/dlq/1/reintentar', 'POST'],
      ['/api/v1/dlq/1', 'DELETE'],
    ])
  })

  it('getEventos y getEmails leen event-log y emails', async () => {
    const adm = await import('@/services/admin')
    expect((await adm.getEventos())[0].accion).toBe('actualizada')
    expect((await adm.getEmails())[0].estado).toBe('fallido')
  })
})

describe('AdminDlqView · operativa DLQ (F09)', () => {
  let fetchMock

  beforeEach(() => {
    localStorage.clear()
    fetchMock = vi.fn((url, opts = {}) => {
      const u = new URL(url)
      if (u.pathname === '/api/v1/dlq') return Promise.resolve(jsonRes(200, DLQ))
      if (u.pathname === '/api/v1/dlq/1/reintentar') return Promise.resolve(jsonRes(200, { id: 1 }))
      if (u.pathname === '/api/v1/dlq/1') return Promise.resolve(jsonRes(204, null))
      if (u.pathname === '/api/v1/mias') return Promise.resolve(jsonRes(200, []))
      return Promise.resolve(jsonRes(200, []))
    })
    vi.stubGlobal('fetch', fetchMock)
    vi.stubEnv('VITE_API_MODE', 'api')
  })

  afterEach(() => {
    vi.unstubAllEnvs()
    vi.unstubAllGlobals()
    vi.resetModules()
  })

  async function montarDlq() {
    vi.resetModules()
    vi.stubEnv('VITE_API_MODE', 'api')
    localStorage.setItem('tfinder-sesion', JSON.stringify(USUARIO_ADMIN))
    await Promise.all([import('@/api/endpoints'), import('@/services/mesas'), import('@/services/admin')])
    const { default: Vista } = await import('@/views/admin/AdminDlqView.vue')
    const router = createRouter({ history: createMemoryHistory(), routes: [{ path: '/admin/dlq', component: Vista }, { path: '/', component: { template: '<div />' } }] })
    await router.push('/admin/dlq')
    const w = mount(Vista, { global: { plugins: [router] } })
    await flushPromises()
    await flushPromises()
    return w
  }

  it('muestra los mensajes DLQ con cola y error', async () => {
    const w = await montarDlq()
    expect(w.text()).toContain('dlq.general')
    expect(w.text()).toContain('fallo simulado')
  })

  it('reintentar invoca POST /dlq/:id/reintentar', async () => {
    const w = await montarDlq()
    await w.find('[data-test="dlq-reintentar"]').trigger('click')
    await flushPromises()
    const post = fetchMock.mock.calls.find(([u, o]) => new URL(u).pathname === '/api/v1/dlq/1/reintentar' && o?.method === 'POST')
    expect(post).toBeTruthy()
  })
})

describe('guard admin (F09)', () => {
  afterEach(() => {
    vi.unstubAllEnvs()
    vi.unstubAllGlobals()
    vi.resetModules()
  })

  it('la ruta /admin exige rol admin (invitado va a login, usuario va a /mesas)', async () => {
    localStorage.clear() // invitado: sin sesión en el almacenamiento
    vi.resetModules()
    vi.stubEnv('VITE_API_MODE', 'api')
    vi.stubGlobal('fetch', vi.fn((url) => Promise.resolve(jsonRes(200, []))))
    const { crearRouterCompleto } = await import('../helpers/routerCompleto')
    const router = crearRouterCompleto()
    await router.push('/admin')
    expect(router.currentRoute.value.path).toBe('/login')

    // usuario autenticado no-admin: /mesas
    localStorage.setItem('tfinder-sesion', JSON.stringify({
      access_token: 'tf-acc',
      user: { id: 3, sub: '3', email: 'ana@tfinder.dev', rol: 'usuario', nombre: 'Ana Votera', iniciales: 'AV', titulo: 'Aventurero' },
    }))
    vi.resetModules()
    const { crearRouterCompleto: otroRouter } = await import('../helpers/routerCompleto')
    const router2 = otroRouter()
    await router2.push('/admin')
    expect(router2.currentRoute.value.path).toBe('/mesas')
  })
})
