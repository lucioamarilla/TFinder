import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/api/endpoints', () => ({
  mesasApi: {
    listar: vi.fn(),
    detalle: vi.fn(),
    crear: vi.fn(),
    actualizar: vi.fn(),
    eliminar: vi.fn()
  },
  authApi: {
    login: vi.fn(),
    register: vi.fn(),
    me: vi.fn(),
    logout: vi.fn(),
    recuperar: vi.fn()
  },
  notifApi: {
    notificaciones: vi.fn(),
    marcarLeida: vi.fn()
  }
}))

const { mesasApi, authApi, notifApi } = await import('@/api/endpoints')
const { getMesas, crearMesa, eliminarMesa } = await import('@/services/mesas')
const { useAuth, currentRole, clearSession } = await import('@/composables/useAuth')
const { getCandidatos, enviarSolicitud } = await import('@/services/matchmaking')
const { getNotificaciones, marcarLeida } = await import('@/services/notificaciones')
const { getAdminUsuarios, getDlq, reintentarMensaje } = await import('@/services/admin')

beforeEach(() => {
  vi.clearAllMocks()
  localStorage.clear()
  clearSession()
})

describe('flujos de servicios con API simulada', () => {
  it('normaliza mesas y permite crear y eliminar', async () => {
    mesasApi.listar.mockResolvedValue({ datos: [{ id: 1, nombre: 'Mesa', sistema: 'PF1e', estado: 'abierta', jugadores_actuales: 1, jugadores_max: 4 }] })
    mesasApi.crear.mockResolvedValue({ datos: { id: 2, nombre: 'Nueva', sistema: 'PF1e', estado: 'abierta' } })
    mesasApi.eliminar.mockResolvedValue({})
    const mesas = await getMesas()
    expect(mesas[0]).toMatchObject({ id: 1, estado: 'Abierta', jugadores: 1, plazas: 4, vacante: true })
    expect((await crearMesa({ nombre: 'Nueva' })).id).toBe(2)
    expect(await eliminarMesa(2)).toEqual({ id: 2 })
  })

  it('completa login, perfil y cierre de sesión', async () => {
    authApi.login.mockResolvedValue({ datos: { access_token: 'a', refresh_token: 'r' } })
    authApi.me.mockResolvedValue({ datos: { email: 'gm@tfinder.dev', rol: 'gm' } })
    authApi.logout.mockResolvedValue({})
    const { login, logout, user, isAuthenticated, isAdmin } = useAuth()
    await login({ email: 'gm@tfinder.dev', password: 'secreto' })
    expect(user.value.email).toBe('gm@tfinder.dev')
    expect(isAuthenticated.value).toBe(true)
    expect(isAdmin.value).toBe(false)
    expect(currentRole()).toBe('auth')
    await logout()
    expect(isAuthenticated.value).toBe(false)
  })

  it('filtra matchmaking y rechaza candidatos inexistentes', async () => {
    const candidatos = await getCandidatos({ rol: 'Guardián' })
    expect(Array.isArray(candidatos)).toBe(true)
    await expect(enviarSolicitud('no-existe')).rejects.toThrow('No encontramos')
  })

  it('consulta administración y procesa DLQ', async () => {
    const usuarios = await getAdminUsuarios({ busqueda: 'a' })
    expect(usuarios.total).toBeGreaterThan(0)
    const dlq = await getDlq()
    expect(Array.isArray(dlq.mensajes)).toBe(true)
    if (dlq.mensajes.length > 0) {
      const resultado = await reintentarMensaje(dlq.mensajes[0].id)
      expect(resultado.id).toBe(dlq.mensajes[0].id)
    }
    await expect(reintentarMensaje('inexistente')).rejects.toThrow('cola de fallidos')
  })

  it('lista notificaciones desde la API y marca una como leída', async () => {
    notifApi.notificaciones.mockResolvedValue({ datos: [{ id: 1, mensaje: 'solicitud', leida: false }] })
    notifApi.marcarLeida.mockResolvedValue({ datos: { id: 1, mensaje: 'solicitud', leida: true } })
    const iniciales = await getNotificaciones()
    expect(iniciales.length).toBeGreaterThan(0)
    expect(iniciales[0].leida).toBe(false)
    const actualizada = await marcarLeida(iniciales[0].id)
    expect(actualizada.leida).toBe(true)
    notifApi.marcarLeida.mockRejectedValue(new Error('No encontramos'))
    await expect(marcarLeida('inexistente')).rejects.toThrow('No encontramos')
  })
})
