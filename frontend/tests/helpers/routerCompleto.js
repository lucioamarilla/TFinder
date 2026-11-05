import { createRouter, createMemoryHistory } from 'vue-router'
import { routes, instalarGuard } from '@/router'

// Router "completo" para tests: mismas rutas y guard que producción, pero con
// componentes resueltos (sin import() dinámico) para navegaciones síncronas en
// flushPromises. Los specs montan las vistas reales explícitamente.
function plano(r) {
  return {
    ...r,
    component: typeof r.component === 'function' ? { template: '<div />' } : r.component,
    children: r.children?.map(plano)
  }
}

export function crearRouterCompleto() {
  const router = createRouter({ history: createMemoryHistory(), routes: routes.map(plano) })
  instalarGuard(router)
  return router
}
