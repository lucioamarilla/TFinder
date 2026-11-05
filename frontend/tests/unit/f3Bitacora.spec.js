import { beforeEach, afterEach, describe, expect, it, vi } from 'vitest'
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

describe('F3 · Bitácora (dual-mode)', () => {
  beforeEach(() => {
    localStorage.clear()
  })
  afterEach(() => {
    vi.unstubAllEnvs()
    vi.unstubAllGlobals()
    vi.resetModules()
  })

  async function ver(listado = []) {
    vi.resetModules()
    vi.stubEnv('VITE_API_MODE', 'api')
    const fetchMock = vi.fn((url) => {
      if (String(url).endsWith('/anotaciones')) {
        return Promise.resolve(jsonRes(200, listado))
      }
      return Promise.resolve(jsonRes(200, []))
    })
    vi.stubGlobal('fetch', fetchMock)
    // F3: el servicio se evalúa ANTES que el componente; garantiza que la
    // instancia que la vista retiene bega el env stubbéado.
    await import('@/services/sesiones')
    const { default: BitacoraView } = await import('@/views/gestion/BitacoraView.vue')
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        {
          path: '/mesas/:mesaId/gestion/sesiones/:sesionId/bitacora',
          component: BitacoraView,
          props: true,
        },
      ],
    })
    await router.push('/mesas/3/gestion/sesiones/7/bitacora')
    const w = mount(BitacoraView, { global: { plugins: [router] } })
    await flushPromises()
    return { w, fetchMock, router }
  }

  it('lista las anotaciones cronológicas con autor (2.3)', async () => {
    const { w, fetchMock } = await ver([
      { id: 9, sesion_id: 7, texto: 'Segundo acto', autor_nombre: 'GM Demo', creado_en: '2026-11-05T10:01:00' },
      { id: 5, sesion_id: 7, texto: 'Primera toma', autor_nombre: 'Ana Votera', autor_id: 9, creado_en: '2026-11-05T10:00:00' },
    ])
    const items = w.findAll('[data-test="bitacora-lista"] li')
    expect(items.length).toBe(2)
    expect(items[0].text()).toContain('Primera toma')
    expect(items[0].text()).toContain('Ana Votera')
    expect(items[1].text()).toContain('Segundo acto')
  })

  it('VAL-33: texto vacío muestra error y no envía nada', async () => {
    const { w, fetchMock } = await ver([])
    await w.find('[data-test="bitacora-texto"]').setValue('   ')
    await w.find('form').trigger('submit')
    await flushPromises()
    expect(w.text()).toContain('El texto de la anotación no puede estar vacío')
    expect(fetchMock.mock.calls.filter((c) => c[1]?.method === 'POST').length).toBe(0)
  })

  it('registra la anotación (POST backend) y refresca la lista', async () => {
    vi.resetModules()
    vi.stubEnv('VITE_API_MODE', 'api')
    const fetchMock = vi.fn((url, init) => {
      if (String(url).endsWith('/anotaciones') && init?.method === 'POST') {
        return Promise.resolve(jsonRes(201, { id: 12, sesion_id: 7, texto: 'Llegó el mensajero', autor_nombre: 'Ana Votera', creado_en: '2026-11-05T10:05:00' }))
      }
      return Promise.resolve(jsonRes(200, [
        { id: 5, sesion_id: 7, texto: 'Primera toma', autor_nombre: 'Ana Votera', autor_id: 9, creado_en: '2026-11-05T10:00:00' },
        { id: 12, sesion_id: 7, texto: 'Llegó el mensajero', autor_nombre: 'Ana Votera', creado_en: '2026-11-05T10:05:00' },
      ]))
    })
    vi.stubGlobal('fetch', fetchMock)
    // F3: el servicio se evalúa ANTES que el componente; garantiza que la
    // instancia que la vista retiene bega el env stubbéado.
    await import('@/services/sesiones')
    const { default: BitacoraView } = await import('@/views/gestion/BitacoraView.vue')
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/mesas/:mesaId/gestion/sesiones/:sesionId/bitacora', component: BitacoraView, props: true },
      ],
    })
    await router.push('/mesas/3/gestion/sesiones/7/bitacora')
    const w = mount(BitacoraView, { global: { plugins: [router] } })
    await flushPromises()
    await w.find('[data-test="bitacora-texto"]').setValue('Llegó el mensajero')
    await w.find('form').trigger('submit')
    await flushPromises()
    const post = fetchMock.mock.calls.find((c) => c[1]?.method === 'POST')
    expect(post[0]).toContain('/api/v1/mesas/3/sesiones/7/anotaciones')
    expect(JSON.parse(post[1].body)).toEqual({ texto: 'Llegó el mensajero' })
    expect(w.findAll('[data-test="bitacora-lista"] li').length).toBe(2)
  })

  it('estado vacío diseñado sin anotaciones', async () => {
    const { w } = await ver([])
    expect(w.find('[data-test="bitacora-vacia"]').exists()).toBe(true)
  })
})
