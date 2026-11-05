import { beforeEach, afterEach, describe, expect, it, vi } from 'vitest'

const LS_KEY = 'tfinder-sesion'

function jsonRes(status, body) {
  return {
    ok: status < 400,
    status,
    headers: Object.fromEntries([['content-type', 'application/json']]),
    json: async () => body,
  }
}

const PERFIL_GM = { id: 2, email: 'gm@tfinder.dev', nombre: 'GM Demo', rol: 'gm' }

async function importarAuth(modo = 'api') {
  vi.resetModules()
  if (modo) vi.stubEnv('VITE_AUTH_MODE', modo)
  return await import('@/composables/useAuth')
}

describe('useAuth · F2 · expiración y renovación de credenciales', () => {
  beforeEach(() => {
    localStorage.clear()
  })
  afterEach(() => {
    vi.unstubAllEnvs()
    vi.unstubAllGlobals()
    vi.resetModules()
  })

  it('la renovación vive en useAuth y persiste el access nuevo', async () => {
    localStorage.setItem(LS_KEY, JSON.stringify({
      access_token: 'acc-viejo',
      refresh_token: 'ref-1',
      user: { email: PERFIL_GM.email, rol: 'gm', nombre: 'GM Demo', iniciales: 'GD' },
    }))

    const fetchMock = vi.fn().mockResolvedValueOnce(jsonRes(200, { access_token: 'acc-nuevo' }))
    vi.stubGlobal('fetch', fetchMock)

    const { hidratarSesion, renovarSesion, currentAccessToken } = await importarAuth('api')
    hidratarSesion()
    const resultado = await renovarSesion()

    expect(resultado).toBe(true)
    expect(currentAccessToken()).toBe('acc-nuevo')
    expect(JSON.parse(localStorage.getItem(LS_KEY)).access_token).toBe('acc-nuevo')
    const url = fetchMock.mock.calls[0][0]
    expect(url).toContain('/api/v1/auth/refresh')
  })

  it('si la renovación falla (refresh muerto) devuelve false y limpia la sesión', async () => {
    localStorage.setItem(LS_KEY, JSON.stringify({
      access_token: 'acc-viejo',
      refresh_token: 'ref-muerto',
      user: { email: PERFIL_GM.email, rol: 'gm', nombre: 'GM Demo', iniciales: 'GD' },
    }))

    vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce(
      jsonRes(401, { error: { codigo: 401, mensaje: 'Sesión revocada o expirada' } }),
    ))

    const { hidratarSesion, renovarSesion, currentAccessToken } = await importarAuth('api')
    hidratarSesion()
    const resultado = await renovarSesion()

    expect(resultado).toBe(false)
    expect(currentAccessToken()).toBeNull()
    expect(JSON.parse(localStorage.getItem(LS_KEY) ?? '{}').access_token ?? null).toBeNull()
  })
})

