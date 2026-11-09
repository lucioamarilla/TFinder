// Ciclo 5 · D-06/D-08: la ambientación es texto libre y se persiste en tono;
// la frecuencia se mapea a horario en crear Y actualizar; el literal 'A
// coordinar' del normalizador no puede contaminar horario al editar.
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

describe('CrearMesaView · ambientación libre (D-06)', () => {
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

  async function montar() {
    vi.resetModules()
    vi.stubEnv('VITE_API_MODE', 'api')
    localStorage.setItem('tfinder-sesion', JSON.stringify(USUARIO))
    fetchMock.mockImplementation((url, opts = {}) => {
      const u = new URL(url)
      if (u.pathname === '/api/v1/mesas' && opts.method === 'POST') return Promise.resolve(jsonRes(201, { ...MESA_CREADA }))
      return Promise.resolve(jsonRes(200, []))
    })
    await Promise.all([import('@/api/endpoints'), import('@/services/mesas')])
    const { default: Vista } = await import('@/views/CrearMesaView.vue')
    const router = createRouter({ history: createMemoryHistory(), routes: [{ path: '/mesas/nueva', component: Vista }, { path: '/mis-mesas-gm', component: { template: '<div />' } }, { path: '/login', component: { template: '<div />' } }] })
    await router.push('/mesas/nueva')
    const w = mount(Vista, { global: { plugins: [router] } })
    await flushPromises()
    return w
  }

  const MESA_CREADA = { id: 88, nombre: 'Cripta de Vellmar', sistema: 'pf1e', gm_id: 9, gm_nombre: 'GM Ostirion', descripcion: 'x', tono: 'El ruido del mar en Skarn', horario: '', estado: 'abierta', nivel_inicial: 5, jugadores_actuales: 1, jugadores_max: 5, fecha_creacion: '2026-11-06' }

  it('la ambientación es textarea libre y viaja en tono (no un select de 5 opciones)', async () => {
    const w = await montar()
    expect(w.find('[data-test="input-ambientacion"]').exists()).toBe(true)
    expect(w.find('#f-lugar[select]').exists()).toBe(false)
  })

  it('submit: el valor libre queda en tono y no envia lugar (extra=forbid del backend)', async () => {
    const w = await montar()
    await w.find('#f-nombre').setValue('Cripta de Vellmar')
    await w.find('[data-test="input-ambientacion"]').setValue('El ruido del mar en Skarn')
    await w.find('#f-nivel').setValue(5)
    await w.find('#f-cupos').setValue(5)
    await w.find('form').trigger('submit')
    await flushPromises()
    const llamada = fetchMock.mock.calls.find(([u, o]) => new URL(u).pathname === '/api/v1/mesas' && o?.method === 'POST')
    expect(llamada).toBeTruthy()
    const cuerpo = JSON.parse(llamada?.[1]?.body)
    expect(cuerpo.tono).toBe('El ruido del mar en Skarn')
    expect(cuerpo.lugar).toBeUndefined()
  })

  it('submit: los pickers dia/hora componen el horario ISO del contrato (D-11)', async () => {
    const w = await montar()
    await w.find('#f-nombre').setValue('Cripta de Vellmar')
    await w.find('#f-dia').setValue('2026-11-12')
    await w.find('#f-hora').setValue('21:00')
    await w.find('form').trigger('submit')
    await flushPromises()
    const llamada = fetchMock.mock.calls.find(([u, o]) => new URL(u).pathname === '/api/v1/mesas' && o?.method === 'POST')
    expect(llamada).toBeTruthy()
    const cuerpo = JSON.parse(llamada?.[1]?.body)
    expect(cuerpo.horario).toBe('2026-11-12 21:00')
    // el aside de preview muestra el mismo horario compuesto
    expect(w.text()).toContain('2026-11-12 21:00')
  })
})

describe('servicios/mesas · mapeo de horario (D-08)', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.stubEnv('VITE_API_MODE', 'api')
  })

  afterEach(() => {
    vi.unstubAllEnvs()
    vi.unstubAllGlobals()
    vi.resetModules()
  })

  it('crearMesa mapea frecuencia -> horario', async () => {
    const fetchMock = vi.fn((url, opts = {}) => {
      const u = new URL(url)
      if (u.pathname === '/api/v1/mesas' && opts.method === 'POST') return Promise.resolve(jsonRes(201, { id: 1, nombre: 'x', sistema: 'pf1e', estado: 'abierta', fecha_creacion: '2026-11-06' }))
      return Promise.resolve(jsonRes(200, []))
    })
    vi.stubGlobal('fetch', fetchMock)
    await Promise.all([import('@/api/endpoints'), import('@/services/mesas')])
    const { crearMesa } = await import('@/services/mesas')
    await crearMesa({ nombre: 'Mesa X', sistema: 'pf1e', estado: 'abierta', frecuencia: 'Sabados 18:00' })
    const llamada = fetchMock.mock.calls.find(([u, o]) => new URL(u).pathname === '/api/v1/mesas' && o?.method === 'POST')
    expect(JSON.parse(llamada?.[1]?.body).horario).toBe('Sabados 18:00')
  })

  it('actualizarMesa mapea frecuencia -> horario (semilla existente)', async () => {
    const fetchMock = vi.fn((url, opts = {}) => {
      const u = new URL(url)
      if (u.pathname === '/api/v1/mesas/77' && opts.method === 'PUT') return Promise.resolve(jsonRes(200, { id: 77, nombre: 'x', sistema: 'pf1e', estado: 'abierta', horario: 'Jueves 20:30', fecha_creacion: '2026-11-01' }))
      return Promise.resolve(jsonRes(200, []))
    })
    vi.stubGlobal('fetch', fetchMock)
    await Promise.all([import('@/api/endpoints'), import('@/services/mesas')])
    const { actualizarMesa } = await import('@/services/mesas')
    await actualizarMesa('77', { frecuencia: 'Jueves 20:30' })
    const llamada = fetchMock.mock.calls.find(([u, o]) => new URL(u).pathname === '/api/v1/mesas/77' && o?.method === 'PUT')
    expect(JSON.parse(llamada?.[1]?.body).horario).toBe('Jueves 20:30')
  })
})

describe('MesaFormularioView · edición sin contaminar horario (D-08)', () => {
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

  const MESA_77 = { id: 77, nombre: 'Cripta de Ustalav', sistema: 'pf1e', gm_id: 9, gm_nombre: 'GM Ostirion', descripcion: 'x', tono: 'Terror', horario: '', estado: 'abierta', nivel_inicial: 5, jugadores_actuales: 1, jugadores_max: 5, fecha_creacion: '2026-11-01' }

  it('mesa sin horario definido: al guardar, PUT escribe horario vacío (no "A coordinar")', async () => {
    vi.resetModules()
    vi.stubEnv('VITE_API_MODE', 'api')
    localStorage.setItem('tfinder-sesion', JSON.stringify(USUARIO))
    fetchMock.mockImplementation((url, opts = {}) => {
      const u = new URL(url)
      if (u.pathname === '/api/v1/mesas/77' && opts.method === 'PUT') return Promise.resolve(jsonRes(200, MESA_77))
      return Promise.resolve(jsonRes(200, []))
    })
    await Promise.all([import('@/api/endpoints'), import('@/services/mesas')])
    const { default: Vista } = await import('@/views/MesaFormularioView.vue')
    const router = createRouter({ history: createMemoryHistory(), routes: [{ path: '/mesas/:id/editar', component: Vista, props: true }, { path: '/mesas/:id/gestion', component: { template: '<div />' } }, { path: '/mis-mesas', component: { template: '<div />' } }] })
    await router.push('/mesas/77/editar')
    const w = mount(Vista, { props: { id: '77' }, global: { plugins: [router] } })
    await flushPromises()
    await flushPromises()
    // cambia solo el nombre para provocar un guardado
    const inputs = w.findAll('input')
    await inputs[0].setValue('Cripta de Ustalav Renovada')
    await w.find('form').trigger('submit')
    await flushPromises()
    const llamada = fetchMock.mock.calls.find(([u, o]) => new URL(u).pathname === '/api/v1/mesas/77' && o?.method === 'PUT')
    expect(llamada).toBeTruthy()
    const cuerpo = JSON.parse(llamada?.[1]?.body)
    expect(cuerpo.nombre).toBe('Cripta de Ustalav Renovada')
    expect(cuerpo.horario ?? '').toBe('')
    expect(cuerpo.horario).not.toBe('A coordinar')
  })
})
