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

const PERFIL_GM = { id: 7, email: 'gm@tfinder.dev', nombre: 'GM Ostirion', rol: 'gm' }

async function importarAuth(modo = 'api') {
  vi.resetModules()
  if (modo) vi.stubEnv('VITE_AUTH_MODE', modo)
  return await import('@/composables/useAuth')
}

describe('useAuth · modo API (sesión real con bearer)', () => {
  beforeEach(() => {
    localStorage.clear()
  })
  afterEach(() => {
    vi.unstubAllEnvs()
    vi.unstubAllGlobals()
    vi.resetModules()
  })

  it('login real: POST /auth/login, guarda tokens y arma el usuario con el perfil', async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce(
      jsonRes(200, {
        access_token: 'acc-1',
        refresh_token: 'ref-1',
        rol: 'gm',
        perfil: PERFIL_GM,
      }),
    )
    vi.stubGlobal('fetch', fetchMock)
    const { login, currentAccessToken, currentRole } = await importarAuth('api')

    const user = await login({ email: 'gm@tfinder.dev', password: 'secreto123' })

    expect(fetchMock.mock.calls[0][0]).toContain('/api/v1/auth/login')
    expect(currentAccessToken()).toBe('acc-1')
    expect(user.email).toBe(PERFIL_GM.email)
    expect(user.rol).toBe('gm')
    // el guard map: gm → 'auth' con permisos ampliables
    expect(currentRole()).toBe('auth')
  })

  it('logout real: POST /auth/logout con Bearer y borra la sesión local', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        jsonRes(200, { access_token: 'acc-1', refresh_token: 'ref-1', rol: 'gm', perfil: PERFIL_GM }),
      )
      .mockResolvedValueOnce(jsonRes(200, { ok: true }))
    vi.stubGlobal('fetch', fetchMock)
    const { login, logout, currentAccessToken } = await importarAuth('api')

    await login({ email: 'gm@tfinder.dev', password: 'secreto123' })
    await logout()

    expect(fetchMock.mock.calls[1][0]).toContain('/api/v1/auth/logout')
    expect(fetchMock.mock.calls[1][1].headers.Authorization).toBe('Bearer acc-1')
    expect(currentAccessToken()).toBeNull()
  })

  it('la sesión persiste tokens y usuario; hidratarSesion los recupera', async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce(
      jsonRes(200, { access_token: 'acc-1', refresh_token: 'ref-1', rol: 'gm', perfil: PERFIL_GM }),
    )
    vi.stubGlobal('fetch', fetchMock)
    const { login } = await importarAuth('api')
    await login({ email: 'gm@tfinder.dev', password: 'secreto123' })

    const guardado = JSON.parse(localStorage.getItem(LS_KEY))
    expect(guardado.access_token).toBe('acc-1')
    expect(guardado.refresh_token).toBe('ref-1')
    expect(guardado.user.rol).toBe('gm')

    const { hidratarSesion, currentAccessToken } = await importarAuth('api')
    hidratarSesion()
    expect(currentAccessToken()).toBe('acc-1')
  })

  it('credenciales inválidas: reproduce el envelope del backend', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValueOnce(
        jsonRes(401, { error: { codigo: 401, mensaje: 'Credenciales inválidas' } }),
      ),
    )
    const { login } = await importarAuth('api')
    await expect(login({ email: 'gm@tfinder.dev', password: 'otraclave99' })).rejects.toMatchObject({
      mensaje: 'Credenciales inválidas',
    })
  })

  it('register real: POST /auth/register tipo usuario con el perfil devuelto', async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce(
      jsonRes(201, {
        access_token: 'acc-nuevo',
        refresh_token: 'ref-nuevo',
        rol: 'usuario',
        perfil: { id: 9, email: 'nuevo@tfinder.dev', nombre: 'Nuevo Aventurero', rol: 'usuario' },
      }),
    )
    vi.stubGlobal('fetch', fetchMock)
    const { register, currentAccessToken } = await importarAuth('api')

    const user = await register({
      nombre: 'Nuevo Aventurero',
      email: 'nuevo@tfinder.dev',
      password: 'secreto123',
    })
    const url = fetchMock.mock.calls[0][0]
    const init = fetchMock.mock.calls[0][1]
    expect(url).toContain('/api/v1/auth/register')
    expect(JSON.parse(init.body)).toEqual(
      expect.objectContaining({ email: 'nuevo@tfinder.dev', password: 'secreto123' }),
    )
    expect(user.rol).toBe('usuario')
    expect(currentAccessToken()).toBe('acc-nuevo')
  })
})

describe('http · robustez de reintentos', () => {
  afterEach(() => {
    vi.unstubAllEnvs()
    vi.unstubAllGlobals()
  })

  it('RED: cada intento tiene su propio AbortController (un timeout no mata al re-intento)', async () => {
    let intentos = 0
    vi.stubGlobal(
      'fetch',
      vi.fn((url, init) => {
        intentos += 1
        if (intentos === 1) {
          return new Promise((_, reject) => {
            init.signal.addEventListener('abort', () =>
              reject(new DOMException('aborted', 'AbortError')),
            )
          })
        }
        return Promise.resolve(jsonRes(200, { ok: 1 }))
      }),
    )
    const { api } = await import('@/api/http')
    const res = await api('mesas', '/api/v1/x', { timeoutMs: 15 })
    expect(res.status).toBe(200)
    expect(intentos).toBe(2)
  })
})
