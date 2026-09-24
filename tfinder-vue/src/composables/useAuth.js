import { reactive, computed } from 'vue'
import { authApi } from '@/api/endpoints'

const STORAGE_KEY = 'tfinder-sesion'

function leerGuardada() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return { access: null, refresh: null, user: null }
    const datos = JSON.parse(raw)
    return {
      access: typeof datos.access === 'string' ? datos.access : null,
      refresh: typeof datos.refresh === 'string' ? datos.refresh : null,
      user: typeof datos.user === 'object' && datos.user !== null ? datos.user : null
    }
  } catch {
    return { access: null, refresh: null, user: null }
  }
}

const state = reactive(leerGuardada())

function persistir() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      access: state.access,
      refresh: state.refresh,
      user: state.user
    }))
  } catch {
    /* almacenamiento no disponible */
  }
}

export function currentAccessToken() {
  return state.access
}

export function currentRole() {
  return state.user?.rol ?? (state.access ? 'auth' : 'guest')
}

export async function login(credentials) {
  const { datos } = await authApi.login(credentials)
  state.access = datos.access_token
  state.refresh = datos.refresh_token
  const me = await authApi.me()
  state.user = { sub: me.datos.sub, email: me.datos.email, rol: me.datos.rol }
  persistir()
  return state.user
}

export async function register(credentials) {
  const { datos } = await authApi.register(credentials)
  state.access = datos.access_token
  state.refresh = datos.refresh_token
  const me = await authApi.me()
  state.user = { sub: me.datos.sub, email: me.datos.email, rol: me.datos.rol }
  persistir()
  return state.user
}

export async function recuperar(email) {
  return authApi.recuperar(email)
}

export async function logout() {
  try {
    await authApi.logout()
  } catch {
    /* red ca��da: igual limpiamos la sesi��n local */
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

export function useAuth() {
  const role = computed(() => currentRole())
  const user = computed(() => state.user)
  const isAuthenticated = computed(() => currentRole() !== 'guest')
  const isAdmin = computed(() => state.user?.rol === 'admin')

  return { role, user, isAuthenticated, isAdmin, login, register, recuperar, logout, clearSession }
}