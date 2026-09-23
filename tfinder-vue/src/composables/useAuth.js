import { reactive, computed } from 'vue'
import { authApi } from '@/api/endpoints'

const STORAGE = 'tfinder-sesion'

const state = reactive({ access: null, refresh: null, user: null })

function leerGuardado() {
  try {
    const guardado = localStorage.getItem(STORAGE)
    if (guardado) Object.assign(state, JSON.parse(guardado))
  } catch {
    /* almacenamiento no disponible */
  }
}

function persistir() {
  try {
    localStorage.setItem(
      STORAGE,
      JSON.stringify({
        access: state.access,
        refresh: state.refresh,
        user: state.user
      })
    )
  } catch {
    /* almacenamiento no disponible */
  }
}

function mapaRol(rol) {
  if (rol === 'admin') return 'admin'
  return rol ? 'auth' : 'guest'
}

function perfilDe(email, rol) {
  const alias =
    (email.split('@')[0] || 'Aventurero')
      .replace(/[._-]+/g, ' ')
      .replace(/\b\w/g, (c) => c.toUpperCase()) || 'Aventurero'
  const iniciales =
    alias
      .split(/\s+/)
      .filter(Boolean)
      .slice(0, 2)
      .map((p) => p[0])
      .join('') || 'AV'
  return {
    email,
    rol,
    nombre: alias,
    iniciales,
    titulo: rol === 'admin' ? 'Moderación & Vigilancia' : 'Aventurero & Cronista'
  }
}

export async function login(credentials) {
  const { datos } = await authApi.login(credentials)
  state.access = datos.access_token
  state.refresh = datos.refresh_token
  const { datos: perfil } = await authApi.me()
  state.user = perfilDe(perfil.email, perfil.rol)
  persistir()
  return state.user
}

export async function logout() {
  try {
    await authApi.logout()
  } catch {
    /* red caída: igual limpiamos */
  }
  clearSession()
}

export function clearSession() {
  state.access = null
  state.refresh = null
  state.user = null
  try {
    localStorage.removeItem(STORAGE)
  } catch {
    /* almacenamiento no disponible */
  }
}

leerGuardado()

export function useAuth() {
  const role = computed(() => mapaRol(state.user?.rol))
  const user = computed(() => state.user)
  const isAuthenticated = computed(() => Boolean(state.access))
  const isAdmin = computed(() => state.user?.rol === 'admin')

  function can(required) {
    if (!required) return true
    return mapaRol(state.user?.rol) === required
  }

  return { role, user, isAuthenticated, isAdmin, login, logout, can }
}

export function currentRole() {
  return mapaRol(state.user?.rol)
}

export function currentAccessToken() {
  return state.access
}