import { isFeatureEnabled } from '@/config/features'

export function resolveGuard(to, role) {
  const feature = to.meta.feature
  if (feature && !isFeatureEnabled(feature)) {
    return { name: 'proximamente', params: { feature } }
  }

  const need = to.meta.roles
  if (!need) return true

  const isAuthenticated = role !== 'guest'

  if (need.includes(role)) return true
  if (need.includes('guest')) return '/mesas'
  if (!isAuthenticated) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
  if (need.includes('admin')) return '/mesas'
  return true
}
