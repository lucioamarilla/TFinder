import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest'
import { apiUrl } from '@/config/api'

describe('config/api · contrato de construcción de URLs', () => {
  it('con define de entorno same-origin, arma la ruta vía proxy (/mesas-api)', async () => {
    vi.resetModules()
    vi.stubEnv('VITE_MESAS_API', '/mesas-api')
    const { apiUrl: apiUrlProxied } = await import('@/config/api')
    expect(apiUrlProxied('mesas', '/api/v1/mesas')).toBe('/mesas-api/api/v1/mesas')
    expect(apiUrlProxied('mesas', '/api/v1/auth/login')).toBe(
      '/mesas-api/api/v1/auth/login',
    )
  })

  it('sin configuración de entorno, cae al puerto de desarrollo 8001', () => {
    expect(apiUrl('mesas', '/api/v1/x')).toBe('http://localhost:8001/api/v1/x')
  })

  it('RED: un servicio desconocido ya no cae silenciosamente al API de mesas', () => {
    expect(() => apiUrl('juego-nuevo', '/api/v1/x')).toThrowError(/servicio desconocido/i)
  })

  beforeEach(() => {
    vi.unstubAllEnvs()
  })
  afterEach(() => {
    vi.unstubAllEnvs()
    vi.resetModules()
  })
})
