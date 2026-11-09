// Ciclo 1 · D-01/D-21: el detalle de mesa no puede anularse por una llamada
// secundaria (miembros/solicitudes) que exige membresía. Un invitado o un
// no-miembro deben ver la ficha pública aunque esas llamadas devuelvan 401/403.
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

function sesionGM() {
  return {
    access_token: 'tf-acc',
    refresh_token: 'tf-ref',
    user: { id: 9, sub: '9', email: 'gm@tfinder.dev', rol: 'director', nombre: 'GM Ostirion', iniciales: 'GO', titulo: 'Director de Juego' },
  }
}

describe('Detalle de mesa tolerante a fallos secundarios (D-01)', () => {
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

  async function montar(vistaPath, ruta, { usuario = null, cuerpo = { mesa: 200, miembros: 403, fechas: [], solicitudes: [] } } = {}) {
    vi.resetModules()
    vi.stubEnv('VITE_API_MODE', 'api')
    if (usuario) localStorage.setItem('tfinder-sesion', JSON.stringify(usuario))
    fetchMock.mockImplementation((url) => {
      const pathname = new URL(url).pathname
      if (pathname === '/api/v1/mesas/77') {
        return Promise.resolve(cuerpo.mesa === 200 ? jsonRes(200, MESA_77) : jsonRes(404, { error: { codigo: 404, mensaje: 'Mesa no encontrada' } }))
      }
      if (pathname === '/api/v1/mesas/77/miembros') {
        return Promise.resolve(jsonRes(cuerpo.miembros, { error: { codigo: 403, mensaje: 'No eres miembro de esta mesa.' } }))
      }
      return Promise.resolve(jsonRes(200, Array.isArray(cuerpo.fechas) ? cuerpo.fechas : []))
    })
    // fuerza la evaluación de http/axios config con el env stubbeado
    await import('@/services/mesas')
    const { default: Vista } = await import(vistaPath)
    const router = createRouter({ history: createMemoryHistory(), routes: [{ path: ruta, component: Vista, props: true }] })
    await router.push(ruta.replace(':id', '77'))
    const w = mount(Vista, { global: { plugins: [router] } })
    await flushPromises()
    await flushPromises()
    return w
  }

  it('INVITADO con miembros 403 ve la ficha de la mesa (no "Mesa no encontrada")', async () => {
    const w = await montar('@/views/MesaDetailJugadorView.vue', '/mesas/:id')
    expect(fetchMock.mock.calls.length).toBeGreaterThan(0)
    expect(w.text()).toContain('Cripta de Ustalav')
    expect(w.text()).not.toContain('Mesa no encontrada')
  })

  it('MIEMBRO autenticado: la pestaña Personajes lista miembros cuando el endpoint responde', async () => {
    const w = await montar('@/views/MesaDetailJugadorView.vue', '/mesas/:id', {
      usuario: sesionGM(),
      cuerpo: { mesa: 200, miembros: 200 },
    })
    await w.findAll('.tabs button')[1].trigger('click')
    expect(w.text()).toContain('GM Ostirion')
  })

  it('NO-MIEMBRO autenticado: mesa visible y pestaña Personajes vacía sin crashear', async () => {
    const w = await montar('@/views/MesaDetailJugadorView.vue', '/mesas/:id', { usuario: sesionGM() })
    expect(w.text()).toContain('Cripta de Ustalav')
    expect(w.text()).not.toContain('Mesa no encontrada')
    await w.findAll('.tabs button')[1].trigger('click')
    await flushPromises()
    expect(w.text()).toContain('Sin miembros')
  })

  it('PANENA Resumen (pestaña por defecto): muestra los parametros de la mesa', async () => {
    const w = await montar('@/views/MesaDetailJugadorView.vue', '/mesas/:id', { usuario: sesionGM() })
    expect(w.text()).toContain('Resumen de la mesa')
    expect(w.text()).toContain('Terror') // ambientacion
    expect(w.text()).toContain('Viernes 20:00') // frecuencia / horario
    expect(w.text()).toContain('GM Ostirion') // dirigida por
  })

  it('mesa inexistente (404) sigue mostrando "Mesa no encontrada"', async () => {
    const w = await montar('@/views/MesaDetailJugadorView.vue', '/mesas/:id', {
      usuario: sesionGM(),
      cuerpo: { mesa: 404, miembros: 403 },
    })
    expect(w.text()).toContain('Mesa no encontrada')
  })

  it('PANEL GM: un fallo de getMiembros no borra el panel (D-01 en MesaDetailGmView)', async () => {
    const w = await montar('@/views/MesaDetailGmView.vue', '/mesas/:id/gm', { usuario: sesionGM() })
    expect(w.text()).toContain('Panel de mesa')
    expect(w.text()).not.toContain('Mesa no encontrada')
    expect(w.text()).not.toContain('Esta mesa no es tuya')
  })
})
