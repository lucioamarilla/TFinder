// Ciclo 11 · D-13/D-19: meta-test permanente de coherencia navegable.
// Ninguna entrada de NAV/FOOTER_NAV ni enlace del footer puede apuntar a una
// ruta inexistente; los dead-links retirados del informe no vuelven.
import { readFileSync } from 'node:fs'
import { join } from 'node:path'
import { afterEach, describe, expect, it, vi } from 'vitest'

const raiz = join(__dirname, '..', '..')

function jsonRes(status, body) {
  return { ok: status < 400, status, headers: Object.fromEntries([['content-type', 'application/json']]), json: async () => body }
}

describe('nav ↔ rutas · meta-test (D-13)', () => {
  afterEach(() => {
    vi.unstubAllEnvs()
    vi.unstubAllGlobals()
    vi.resetModules()
  })

  it('todas las entradas de NAV y FOOTER_NAV resuelven a rutas reales', async () => {
    vi.resetModules()
    vi.stubEnv('VITE_API_MODE', 'api')
    vi.stubGlobal('fetch', vi.fn((url) => Promise.resolve(jsonRes(200, []))))
    await Promise.all([import('@/api/endpoints'), import('@/services/mesas')])
    const { NAV, FOOTER_NAV } = await import('@/config/nav')
    const { crearRouterCompleto } = await import('../helpers/routerCompleto')
    const router = crearRouterCompleto()
    const grupos = [[NAV, 'NAV'], [FOOTER_NAV, 'FOOTER_NAV']]
    for (const [mapa, nombre] of grupos) {
      for (const rol of Object.keys(mapa)) {
        for (const item of mapa[rol]) {
          const resuelta = router.resolve(item.to)
          expect(resuelta.name, `${nombre}[${rol}]: ${item.label} -> ${item.to}`).not.toBe('not-found')
        }
      }
    }
  })

  it('AppFooter no enlaza a la galería índice (retirada de producción)', () => {
    const fuente = readFileSync(join(raiz, 'src/components/AppFooter.vue'), 'utf8')
    expect(fuente).not.toContain('to="/indice"')
  })

  it('DashboardView no enlaza a matchmaking (ruta retirada)', () => {
    const fuente = readFileSync(join(raiz, 'src/views/DashboardView.vue'), 'utf8')
    expect(fuente).not.toContain('/matchmaking')
  })

  it('AppHeader no empuja la ruta de búsqueda retirada', () => {
    const fuente = readFileSync(join(raiz, 'src/components/AppHeader.vue'), 'utf8')
    expect(fuente).not.toContain("'/busqueda'")
  })
})
