// RED Fase 1 · Guard de rutas por rol y feature
import { resolveGuard } from '@/router/guard'

const ruta = (meta, path = '/destino') => ({ fullPath: path, path, meta })
const PROXIMO = { name: 'proximamente' }

describe('resolveGuard', () => {
  it('rutas sin meta se permiten a cualquiera', () => {
    expect(resolveGuard(ruta({}), 'guest')).toBe(true)
    expect(resolveGuard(ruta({}), 'auth')).toBe(true)
  })

  it('rutas con feature cerrada redirigen a proximamente con el feature informado', () => {
    // Los features revividos están disponibles; el guard se prueba con uno inexistente.
    const destino = resolveGuard(ruta({ feature: 'inexistente' }), 'auth')
    expect(destino.name).toBe('proximamente')
    expect(destino.params.feature).toBe('inexistente')
  })

  it('un invitado en una ruta auth-only es enviado a login conservando el redirect', () => {
    const destino = resolveGuard(ruta({ roles: ['auth'] }, '/mis-mesas'), 'guest')
    expect(destino.path).toBe('/login')
    expect(destino.query.redirect).toBe('/mis-mesas')
  })

  it('un usuario autenticado accede a rutas auth', () => {
    expect(resolveGuard(ruta({ roles: ['auth'] }), 'auth')).toBe(true)
  })

  it('un autenticado que reingresa a login/registro (guest-only) es llevado a mesas', () => {
    expect(resolveGuard(ruta({ roles: ['guest'] }, '/login'), 'auth')).toBe('/mesas')
  })

  it('un invitado sí puede entrar a login/registro (guest-only)', () => {
    expect(resolveGuard(ruta({ roles: ['guest'] }, '/login'), 'guest')).toBe(true)
  })

  it('un admin accede a rutas admin; un auth no', () => {
    expect(resolveGuard(ruta({ roles: ['admin'] }), 'admin')).toBe(true)
    expect(resolveGuard(ruta({ roles: ['admin'] }), 'auth')).toBe('/mesas')
  })
})

describe('isFeatureEnabled (features cerradas por defecto)', () => {
  it('FEATURE definido como disponible responde disponible y el camino de proximamente es estable', async () => {
    const { isFeatureEnabled, comingSoonPath } = await import('@/config/features')
    expect(isFeatureEnabled('crearMesa')).toBe(true)
    expect(isFeatureEnabled('inexistente')).toBe(false)
    expect(comingSoonPath('feed')).toBe('/proximamente/feed')
    expect(comingSoonPath('Desconocido')).toBe('/proximamente/no-disponible')
  })
})
