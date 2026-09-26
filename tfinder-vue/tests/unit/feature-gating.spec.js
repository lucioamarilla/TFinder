import { describe, expect, it } from 'vitest'
import { resolveGuard } from '@/router/guard'

describe('funcionalidades próximas', () => {
  it('redirige una función deshabilitada', () => {
    expect(resolveGuard({ meta: { roles: ['auth'], feature: 'builds' } }, 'auth')).toEqual({
      name: 'proximamente',
      params: { feature: 'builds' }
    })
  })

  it('permite una función habilitada', () => {
    expect(resolveGuard({ meta: { roles: ['auth'], feature: 'notificaciones' } }, 'auth')).toBe(true)
  })

  it('permite encuentros, que no necesita backend', () => {
    expect(resolveGuard({ meta: { roles: ['auth'], feature: 'encuentros' } }, 'auth')).toBe(true)
  })

  it('permite una ruta habilitada', () => {
    expect(resolveGuard({ meta: { roles: ['guest', 'auth'] } }, 'guest')).toBe(true)
  })

  it('mantiene la redirección de acceso protegido', () => {
    expect(resolveGuard({ meta: { roles: ['auth'] }, fullPath: '/perfil' }, 'guest')).toEqual({
      path: '/login',
      query: { redirect: '/perfil' }
    })
  })

  it('envía al administrador a explorar mesas', () => {
    expect(resolveGuard({ meta: { roles: ['guest'] } }, 'admin')).toBe('/mesas')
  })
})
