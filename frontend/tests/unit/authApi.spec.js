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

  it('register real: POST /auth/register queda pendiente (sin sesión instalada)', async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce(
      jsonRes(202, { pendiente: true, email: 'nuevo@tfinder.dev' }),
    )
    vi.stubGlobal('fetch', fetchMock)
    const { register, currentAccessToken } = await importarAuth('api')

    const res = await register({
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
    // La cuenta nace al verificar el código del mail: acá aún no hay sesión.
    expect(res).toEqual({ pendiente: true, email: 'nuevo@tfinder.dev' })
    expect(currentAccessToken()).toBeNull()
  })

  it('verificarRegistro real: confirma el código y nace la sesión', async () => {
    const tokens = {
      access_token: 'acc-nuevo',
      refresh_token: 'ref-nuevo',
      rol: 'usuario',
      perfil: { id: 9, email: 'nuevo@tfinder.dev', nombre: 'Nuevo Aventurero', rol: 'usuario' },
    }
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonRes(202, { pendiente: true, email: 'nuevo@tfinder.dev' }))
      .mockResolvedValueOnce(jsonRes(200, tokens))
    vi.stubGlobal('fetch', fetchMock)
    const { register, verificarRegistro, currentAccessToken } = await importarAuth('api')

    await register({ nombre: 'Nuevo Aventurero', email: 'nuevo@tfinder.dev', password: 'secreto123' })
    await verificarRegistro('nuevo@tfinder.dev', '123456')

    expect(fetchMock.mock.calls[1][0]).toContain('/api/v1/auth/register/verificar')
    expect(JSON.parse(fetchMock.mock.calls[1][1].body)).toEqual({
      email: 'nuevo@tfinder.dev',
      codigo: '123456',
    })
    expect(currentAccessToken()).toBe('acc-nuevo')
  })

  it('verificarRegistro con código mal formado falla sin llamar al backend', async () => {
    const fetchMock = vi.fn()
    vi.stubGlobal('fetch', fetchMock)
    const { verificarRegistro } = await importarAuth('api')

    await expect(verificarRegistro('nuevo@tfinder.dev', '12ab6')).rejects.toMatchObject({
      codigo: '400',
    })
    expect(fetchMock).not.toHaveBeenCalled()
  })

  it('recuperar real: POST /auth/recuperar responde genérico (202)', async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce(
      jsonRes(202, { mensaje: 'Si el correo existe, te enviamos un código para restablecer la contraseña.' }),
    )
    vi.stubGlobal('fetch', fetchMock)
    const { recuperar } = await importarAuth('api')

    const res = await recuperar('viejo@tfinder.dev')
    expect(fetchMock.mock.calls[0][0]).toContain('/api/v1/auth/recuperar')
    expect(res.mensaje).toContain('Si el correo existe')
  })

  it('confirmarRecupero real: POST /auth/recuperar/verificar con código y nueva clave', async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce(
      jsonRes(200, { mensaje: 'Contraseña actualizada. Ya podés entrar con la nueva.' }),
    )
    vi.stubGlobal('fetch', fetchMock)
    const { confirmarRecupero } = await importarAuth('api')

    const res = await confirmarRecupero('viejo@tfinder.dev', '654321', 'nuevaclave99')
    expect(fetchMock.mock.calls[0][0]).toContain('/api/v1/auth/recuperar/verificar')
    expect(JSON.parse(fetchMock.mock.calls[0][1].body)).toEqual({
      email: 'viejo@tfinder.dev',
      codigo: '654321',
      nueva_password: 'nuevaclave99',
    })
    expect(res.mensaje).toContain('actualizada')
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
