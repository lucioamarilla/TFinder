// Ciclo 9 · D-11: getMiembros respeta el rol real del backend (master|jugador)
// y deriva capacidad desde la mesa (jugadores_max), sin hardcodear 'Jugador'.
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

function jsonRes(status, body) {
  return {
    ok: status < 400,
    status,
    headers: Object.fromEntries([['content-type', 'application/json']]),
    json: async () => body,
  }
}

describe('getMiembros · rol y capacidad reales (D-11)', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.stubEnv('VITE_API_MODE', 'api')
  })

  afterEach(() => {
    vi.unstubAllEnvs()
    vi.unstubAllGlobals()
    vi.resetModules()
  })

  it('el GM aparece como Master y el jugador como Jugador', async () => {
    vi.stubGlobal('fetch', vi.fn((url) => {
      const u = new URL(url)
      if (u.pathname === '/api/v1/mesas/77/miembros') {
        return Promise.resolve(jsonRes(200, {
          miembros: [
            { id: 9, nombre: 'GM Ostirion', email: 'gm@tfinder.dev', rol: 'master' },
            { id: 3, nombre: 'Ana Votera', email: 'ana@tfinder.dev', rol: 'jugador' },
          ],
        }))
      }
      return Promise.resolve(jsonRes(200, []))
    }))
    await Promise.all([import('@/api/endpoints'), import('@/services/mesas')])
    const { getMiembros } = await import('@/services/jugadores')
    const { normalizarMesa } = await import('@/services/mesas')
    const mesa = normalizarMesa({ id: 77, estado: 'abierta', jugadores_max: 5, jugadores_actuales: 1 })
    const { miembros, capacidad } = await getMiembros('77', mesa)
    expect(miembros.find((m) => m.id === '9')?.rol).toBe('Master')
    expect(miembros.find((m) => m.id === '3')?.rol).toBe('Jugador')
    expect(capacidad).toBe(5)
  })
})
