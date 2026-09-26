import { afterEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/config/api', () => ({ apiUrl: (servicio, ruta) => `http://test/${servicio}${ruta}` }))
vi.mock('@/composables/useAuth', () => ({
  currentAccessToken: () => 'token-test',
  clearSession: vi.fn()
}))

const { api, ApiError } = await import('@/api/http')

afterEach(() => {
  vi.restoreAllMocks()
  vi.unstubAllGlobals()
})

describe('cliente HTTP', () => {
  it('agrega token, body e idempotencia en una escritura', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 201,
      json: async () => ({ id: 1 }),
      headers: { forEach: () => {} }
    })
    vi.stubGlobal('fetch', fetchMock)

    const resultado = await api('mesas', '/api/v1/mesas', {
      metodo: 'POST',
      cuerpo: { nombre: 'Mesa' },
      idempotenciaKey: 'clave-1'
    })

    expect(resultado.datos).toEqual({ id: 1 })
    const [, opciones] = fetchMock.mock.calls[0]
    expect(opciones.headers.Authorization).toBe('Bearer token-test')
    expect(opciones.headers['Idempotency-Key']).toBe('clave-1')
    expect(opciones.headers['X-Correlation-Id']).toBeTruthy()
  })

  it('convierte errores HTTP en ApiError', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: false,
      status: 409,
      json: async () => ({ error: { codigo: 409, mensaje: 'Sin cupo' } }),
      headers: { forEach: () => {} }
    }))

    await expect(api('mesas', '/api/v1/mesas/1/solicitar')).rejects.toMatchObject({
      name: 'ApiError',
      codigo: 409,
      mensaje: 'Sin cupo'
    })
    expect(ApiError).toBeDefined()
  })
})
