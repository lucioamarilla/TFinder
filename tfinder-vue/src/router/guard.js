export function resolveGuard(to, role) {
  const need = to.meta.roles
  if (!need) return true

  const isAuthenticated = role !== 'guest'

  if (need.includes(role)) return true
  if (need.includes('guest')) {
    return role === 'admin' ? '/admin/moderacion' : '/dashboard'
  }
  if (!isAuthenticated) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
  if (need.includes('admin')) return '/dashboard'
  return true
}