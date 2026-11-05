// Sesión del frontend TFinder.
// DOS modos de operación, elegido por VITE_AUTH_MODE:
//  - "demo" (default): sesión local en localStorage, sin backend. Misma firma
//    pública (login/register/logout/recuperar/clearSession/currentRole/
//    currentAccessToken/useAuth) para que guard, header y vistas no dependan
//    del backend mientras dure la demo.
//  - "api": sesión REAL contra mesas-api (JWT + refresh + perfil). Los tokens
//    persisten en localStorage y http.js los manda como Authorization: Bearer.
//
// Contraseñas: nunca se guardan en claro. En la demo se almacena un hash no
// criptográfico (suficiente porque es localStorage local del navegador) con el
// mismo espíritu que VAL-04 (bcrypt/PBKDF2 en el backend real).

import { reactive, computed } from 'vue'
import { validarEmail, validarPassword, validarNombre, MENSAJES_AUTH } from '@/rules/auth'

// El modo se define una sola vez en el arranque del módulo (build/clase test).
const MODO = String(import.meta.env.VITE_AUTH_MODE ?? 'demo').toLowerCase()
const ES_API = MODO === 'api'

const STORAGE_KEY = 'tfinder-sesion'
const REGISTRO_KEY = 'tfinder-usuarios'
const SAL_DEMO = 'tfinder-demo-v1'
const CLAVE_SEMILLA = 'tfinder1234'

export function hashDemo(texto) {
  let h = 5381
  const s = `${SAL_DEMO}:${texto}`
  for (let i = 0; i < s.length; i++) h = ((h << 5) + h + s.charCodeAt(i)) | 0
  return (h >>> 0).toString(16)
}

function errorNegocio(codigo, mensaje) {
  const e = new Error(mensaje)
  e.codigo = String(codigo)
  e.mensaje = mensaje
  return e
}

function leerUsuarios() {
  try {
    const raw = localStorage.getItem(REGISTRO_KEY)
    if (!raw) return []
    const datos = JSON.parse(raw)
    return Array.isArray(datos) ? datos.filter((u) => u && typeof u.email === 'string') : []
  } catch {
    return []
  }
}

function guardarUsuarios(usuarios) {
  try {
    localStorage.setItem(REGISTRO_KEY, JSON.stringify(usuarios))
  } catch {
    /* almacenamiento no disponible */
  }
}

const CUENTAS_SEMILLA = [
  { email: 'admin@tfinder.dev', nombre: 'Admin TFinder', rol: 'admin' },
  { email: 'valeros@tfinder.dev', nombre: 'Valeros el Bravo', rol: 'jugador' },
  { email: 'gmostirion@tfinder.dev', nombre: 'GM Ostirion', rol: 'director' }
]

function sembrar() {
  if (ES_API) return // las cuentas reales viven en mesas_db, no en la demo local
  if (localStorage.getItem(REGISTRO_KEY)) return
  guardarUsuarios(CUENTAS_SEMILLA.map((c) => ({ ...c, hash: hashDemo(CLAVE_SEMILLA) })))
}

// Re instala las cuentas semilla (contraseña de todas: `tfinder1234`).
export function restaurarSemillas() {
  try {
    localStorage.removeItem(REGISTRO_KEY)
  } catch { /* noop */ }
  sembrar()
}

function leerGuardada() {
  return { access: null, refresh: null, user: null }
}

function leidoConRehidratacion() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return leerGuardada()
    const datos = JSON.parse(raw)
    return {
      access: typeof datos.access_token === 'string' ? datos.access_token : null,
      refresh: typeof datos.refresh_token === 'string' ? datos.refresh_token : null,
      user: typeof datos.user === 'object' && datos.user !== null ? datos.user : null
    }
  } catch {
    return leerGuardada()
  }
}

const state = reactive(leidoConRehidratacion())

function persistir() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      access_token: state.access,
      refresh_token: state.refresh,
      user: state.user
    }))
  } catch {
    /* almacenamiento no disponible */
  }
}

function mapaRol(rol) {
  if (rol === 'admin') return 'admin'
  return rol ? 'auth' : 'guest'
}

function perfilDe(email, rol, nombre, id = null) {
  const fuente = (nombre || '').trim()
  let alias
  if (fuente) {
    // El nombre provisto por el usuario se respeta tal como fue registrado.
    alias = fuente
  } else {
    alias = (email.split('@')[0] || 'Aventurero')
      .replace(/[._-]+/g, ' ')
      .replace(/\b\w/g, (c) => c.toUpperCase())
    if (!alias) alias = 'Aventurero'
  }
  const iniciales =
    alias
      .split(/\s+/)
      .filter(Boolean)
      .slice(0, 2)
      .map((p) => p[0])
      .join('')
      .toUpperCase() || 'AV'
  const titulo =
    rol === 'admin' ? 'Moderación & Vigilancia'
      : rol === 'director' || rol === 'gm' ? 'Director de Juego'
        : 'Aventurero & Cronista'
  return { email, rol, nombre: alias, iniciales, titulo, id, sub: id ? String(id) : null }
}

function instalarSesion(email, rol, nombre) {
  state.user = perfilDe(email, rol, nombre)
  persistir()
  return state.user
}

// Instala la sesión a partir de la respuesta real del backend (P0.3).
function instalarSesionBack(tokens) {
  const perfil = tokens?.perfil ?? {}
  state.access = typeof tokens?.access_token === 'string' ? tokens.access_token : null
  state.refresh = typeof tokens?.refresh_token === 'string' ? tokens.refresh_token : null
  state.user = perfilDe(perfil.email ?? '', perfil.rol ?? 'usuario', perfil.nombre, perfil.id ?? null)
  persistir()
  return state.user
}

async function cliente() {
  // Import diferido evita el ciclo estático useAuth ⇄ http en el arranque.
  const { authApi } = await import('@/api/endpoints')
  return authApi
}

export function currentAccessToken() {
  return state.access
}

export function currentRole() {
  return mapaRol(state.user?.rol)
}

export async function login(credentials) {
  const { email, password } = credentials || {}
  const errorForma = validarEmail(email) ?? validarPassword(password)
  if (errorForma) throw errorNegocio('400', errorForma)

  if (ES_API) {
    try {
      const { login: loginRemota } = await cliente()
      const { datos } = await loginRemota({ email: String(email).trim().toLowerCase(), password })
      return instalarSesionBack(datos)
    } catch (e) {
      if (e?.codigo === 401) throw errorNegocio('401', MENSAJES_AUTH.credencialesInvalidas)
      throw e
    }
  }

  sembrar()
  const usuario = leerUsuarios().find((u) => u.email === String(email).trim().toLowerCase())
  if (!usuario || usuario.hash !== hashDemo(password)) {
    throw errorNegocio('401', MENSAJES_AUTH.credencialesInvalidas)
  }
  return instalarSesion(usuario.email, usuario.rol, usuario.nombre)
}

export async function register(credentials) {
  const { nombre, email, password, rol = 'jugador' } = credentials || {}
  const errorForma = validarNombre(nombre) ?? validarEmail(email) ?? validarPassword(password)
  if (errorForma) throw errorNegocio('400', errorForma)

  if (ES_API) {
    // El backend fuerza rol 'usuario' en el registro público (no escalable).
    const { register: registrarRemoto } = await cliente()
    const { datos } = await registrarRemoto({
      nombre: nombre.trim(),
      email: String(email).trim().toLowerCase(),
      password,
    })
    return instalarSesionBack(datos)
  }

  sembrar()
  const normalizado = String(email).trim().toLowerCase()
  if (leerUsuarios().some((u) => u.email === normalizado)) {
    throw errorNegocio('409', MENSAJES_AUTH.correoDuplicado)
  }
  const usuarios = leerUsuarios()
  usuarios.push({ email: normalizado, nombre: nombre.trim(), rol, hash: hashDemo(password) })
  guardarUsuarios(usuarios)
  return instalarSesion(normalizado, rol, nombre)
}

export async function recuperar(email) {
  const errorForma = validarEmail(email)
  if (errorForma) throw errorNegocio('400', errorForma)

  if (ES_API) {
    const { recuperar: recuperarReal } = await cliente()
    const { datos } = await recuperarReal({ email })
    return datos ?? { ok: true }
  }

  // Demo sin correo real: la vista informa que el enlace "fue enviado".
  return { ok: true }
}

export async function logout() {
  if (ES_API) {
    try {
      const { logout: logoutRemoto } = await cliente()
      await logoutRemoto()
    } catch {
      /* 4xx/401 previos o backend caído: la sesión local se limpia igual */
    }
  } else {
    await Promise.resolve()
  }
  clearSession()
}

export function clearSession() {
  state.access = null
  state.refresh = null
  state.user = null
  try {
    localStorage.removeItem(STORAGE_KEY)
  } catch {
    /* almacenamiento no disponible */
  }
}

export function hidratarSesion() {
  const { access, refresh, user } = leidoConRehidratacion()
  state.access = access
  state.refresh = refresh
  if (user) state.user = user
  // (Sin validación en background: si el token está vencido, la próxima llamada
  // devuelve 401 y http.js la renueva — o limpia la sesión y redirige.)
}

// F2 (2.1 renovación): rota el access con el refresh_token guardado.
// Devuelve true si la sesión quedó renovada; false si hay que re-loguear.
export async function renovarSesion() {
  if (!state.refresh) {
    clearSession()
    return false
  }
  try {
    const { apiUrl } = await import('@/config/api')
    const respuesta = await fetch(apiUrl('mesas', '/api/v1/auth/refresh'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: state.refresh }),
    })
    if (respuesta.status !== 200) {
      clearSession()
      return false
    }
    const datos = await respuesta.json()
    state.access = typeof datos.access_token === 'string' ? datos.access_token : null
    if (!state.access) {
      clearSession()
      return false
    }
    persistir()
    return true
  } catch {
    clearSession()
    return false
  }
}

// Edita el nombre del aventurero de la sesión (VAL-05 lo mantiene obligatorio).
export async function editarPerfil(nombre) {  const errorForma = validarNombre(nombre)
  if (errorForma) throw errorNegocio('400', errorForma)
  if (!state.user) throw errorNegocio('401', 'Necesitás una sesión para editar tu perfil')

  const limpio = nombre.trim()
  sembrar()
  const usuarios = leerUsuarios()
  const indice = usuarios.findIndex((u) => u.email === state.user.email)
  if (indice >= 0) { usuarios[indice].nombre = limpio; guardarUsuarios(usuarios) }
  state.user = perfilDe(state.user.email, state.user.rol, limpio, state.user.id)
  persistir()
  return state.user
}

// Cambia la contraseña de la sesión activa: valida la actual y aplica VAL-03 a la nueva.
export async function cambiarPassword({ actual, nueva } = {}) {
  if (!state.user) throw errorNegocio('401', 'Necesitás una sesión para cambiar tu contraseña')

  const errorNueva = validarPassword(nueva)
  if (errorNueva) throw errorNegocio('400', errorNueva)

  sembrar()
  const usuarios = leerUsuarios()
  const indice = usuarios.findIndex((u) => u.email === state.user.email)
  if (indice < 0) throw errorNegocio('404', 'Cuenta no encontrada')
  if (usuarios[indice].hash !== hashDemo(actual)) {
    throw errorNegocio('400', 'La contraseña actual es incorrecta')
  }
  usuarios[indice].hash = hashDemo(nueva)
  guardarUsuarios(usuarios)
  notificarDemoCambio()
  return { ok: true }
}

// Aviso no persistente utilizable por las vistas para su toast de éxito.
function notificarDemoCambio() {}

export function useAuth() {
  const role = computed(() => currentRole())
  const user = computed(() => state.user)
  const isAuthenticated = computed(() => state.user !== null)
  const isAdmin = computed(() => state.user?.rol === 'admin')

  function can(required) {
    if (!required) return true
    return mapaRol(state.user?.rol) === required
  }

  return { role, user, isAuthenticated, isAdmin, can, login, logout, register, recuperar, clearSession, editarPerfil, cambiarPassword, hidratarSesion }
}
