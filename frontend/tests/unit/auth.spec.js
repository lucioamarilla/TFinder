// RED Fase 1 · Reglas de autenticación y sesión demo (VAL-01/02/03/05, CA-01..05)
import {
  validarEmail,
  validarPassword,
  validarNombre
} from '@/rules/auth'
import {
  login,
  register,
  logout,
  clearSession,
  currentRole,
  restaurarSemillas,
  hidratarSesion
} from '@/composables/useAuth'

const MENSAJES = {
  email: 'El correo electrónico no tiene un formato válido',
  password: 'La contraseña debe tener al menos 8 caracteres',
  nombre: 'El nombre de usuario es obligatorio',
  duplicado: 'El correo electrónico ya está registrado',
  credenciales: 'Credenciales inválidas'
}

describe('validadores de reglas de negocio (auth)', () => {
  it('VAL-01 · acepta correos válidos y rechaza los inválidos con el mensaje del backend', () => {
    expect(validarEmail('jugador@tfinder.dev')).toBe(null)
    for (const invalido of ['', 'sin-arroba', 'a@', '@b.com', 'a b@x.com']) {
      expect(validarEmail(invalido)).toBe(MENSAJES.email)
    }
  })

  it('VAL-03 · la contraseña exige mínimo 8 caracteres (límite exacto en 7 y 8)', () => {
    expect(validarPassword('1234567' + 'x')).toBe(null) // 8
    expect(validarPassword('1234567')).toBe(MENSAJES.password)
    expect(validarPassword('')).toBe(MENSAJES.password)
  })

  it('VAL-05 · el nombre de usuario es obligatorio (se recortan espacios)', () => {
    expect(validarNombre('Aldric')).toBe(null)
    expect(validarNombre('  Aldric  ')).toBe(null)
    expect(validarNombre('')).toBe(MENSAJES.nombre)
    expect(validarNombre('   ')).toBe(MENSAJES.nombre)
  })
})

describe('sesión demo (useAuth)', () => {
  beforeEach(() => {
    localStorage.clear()
    clearSession()
    restaurarSemillas()
  })

  it('CA-01 · registrar con datos válidos crea la cuenta e inicia sesión automáticamente', async () => {
    const usuario = await register({ nombre: 'Aldric', email: 'aldric@tfinder.dev', password: 'contraseña8', rol: 'jugador' })
    expect(usuario.email).toBe('aldric@tfinder.dev')
    expect(usuario.rol).toBe('jugador')
    expect(currentRole()).toBe('auth')
    expect(JSON.parse(localStorage.getItem('tfinder-sesion')).user.email).toBe('aldric@tfinder.dev')
  })

  it('VAL-02 · registrar un correo ya registrado responde 409 con el mensaje estandarizado', async () => {
    await expect(register({ nombre: 'Otro', email: 'valeros@tfinder.dev', password: 'contraseña8', rol: 'jugador' }))
      .rejects.toMatchObject({ codigo: '409', mensaje: MENSAJES.duplicado })
  })

  it('CA-05 · login con credenciales inválidas falla sin crear sesión', async () => {
    await expect(login({ email: 'valeros@tfinder.dev', password: 'incorrecta1' }))
      .rejects.toMatchObject({ codigo: '401', mensaje: MENSAJES.credenciales })
    expect(currentRole()).toBe('guest')
  })

  it('CA-05b · login de un correo no registrado falla sin crear sesión', async () => {
    await expect(login({ email: 'fantasma@tfinder.dev', password: 'contraseña8' }))
      .rejects.toMatchObject({ codigo: '401', mensaje: MENSAJES.credenciales })
  })

  it('CA-04 · login con credenciales sembradas habilita el rol según la cuenta', async () => {
    await login({ email: 'valeros@tfinder.dev', password: 'tfinder1234' })
    expect(currentRole()).toBe('auth')

    await login({ email: 'admin@tfinder.dev', password: 'tfinder1234' })
    expect(currentRole()).toBe('admin')
  })

  it('la sesión persiste entre hidrataciones (recarga del módulo) y describe perfil', async () => {
    const { useAuth } = await import('@/composables/useAuth')
    await login({ email: 'gmostirion@tfinder.dev', password: 'tfinder1234' })
    hidratarSesion()

    expect(currentRole()).toBe('auth')
    const { user } = useAuth()
    expect(user.value.nombre).toBeTruthy()
    expect(user.value.iniciales.length).toBeGreaterThan(0)
  })

  it('logout limpia la sesión y el almacenamiento', async () => {
    await login({ email: 'valeros@tfinder.dev', password: 'tfinder1234' })
    await logout()
    expect(currentRole()).toBe('guest')
    expect(localStorage.getItem('tfinder-sesion')).toBe(null)
  })
})
