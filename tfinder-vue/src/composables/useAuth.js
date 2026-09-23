import { reactive, computed } from 'vue'

const PROFILES = {
  auth: { nombre: 'Aldren Valeros', rol: 'auth', iniciales: 'AV', titulo: 'Aventurero & Cronista' },
  admin: { nombre: 'Alguacil del Cónclave', rol: 'admin', iniciales: 'AC', titulo: 'Moderación & Vigilancia' }
}

const STORAGE_KEY = 'tfinder-rol'
const TOKEN_KEY = 'tfinder-access'

function readStoredRole() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    return stored === 'admin' || stored === 'auth' ? stored : 'guest'
  } catch {
    return 'guest'
  }
}

const state = reactive({
  role: readStoredRole(),
  user: PROFILES[readStoredRole()] || null
})

function persist(role) {
  try {
    localStorage.setItem(STORAGE_KEY, role)
  } catch {
    /* almacenamiento no disponible */
  }
}

function limpiarSesionLocal() {
  state.role = 'guest'
  state.user = null
  persist('guest')
  try {
    localStorage.removeItem(TOKEN_KEY)
  } catch {
    /* almacenamiento no disponible */
  }
}

export function useAuth() {
  const role = computed(() => state.role)
  const user = computed(() => state.user)
  const isAuthenticated = computed(() => state.role !== 'guest')
  const isAdmin = computed(() => state.role === 'admin')

  function login(credentials = {}) {
    const target = credentials.role === 'admin' ? 'admin' : 'auth'
    state.role = target
    state.user = PROFILES[target]
    persist(target)
    return state.user
  }

  function loginAs(role) {
    state.role = role
    state.user = PROFILES[role] || null
    persist(role)
    return state.user
  }

  function logout() {
    limpiarSesionLocal()
  }

  function can(required) {
    if (!required) return true
    return state.role === required
  }

  return { role, user, isAuthenticated, isAdmin, login, loginAs, logout, can }
}

export function currentRole() {
  return state.role
}

export function currentAccessToken() {
  try {
    return localStorage.getItem(TOKEN_KEY)
  } catch {
    return null
  }
}

export function clearSession() {
  limpiarSesionLocal()
}