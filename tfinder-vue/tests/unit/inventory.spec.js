import { describe, expect, it } from 'vitest'

const componentes = import.meta.glob('../../src/components/**/*.vue', { eager: true })
const vistas = import.meta.glob('../../src/views/**/*.vue', { eager: true })
const composables = import.meta.glob('../../src/composables/*.js', { eager: true })
const servicios = import.meta.glob('../../src/services/*.js', { eager: true })

function comprobarExportaciones(nombre, modulos) {
  it(`${nombre} tiene exports importables`, () => {
    expect(Object.keys(modulos).length).toBeGreaterThan(0)
    for (const modulo of Object.values(modulos)) {
      expect(modulo).toBeDefined()
    }
  })
}

describe('inventario frontend', () => {
  comprobarExportaciones('componentes', componentes)
  comprobarExportaciones('vistas', vistas)
  comprobarExportaciones('composables', composables)
  comprobarExportaciones('servicios', servicios)
})
