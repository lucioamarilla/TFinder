// RED Fase 2 · Reglas de negocio de mesas (RN-04/09, VAL-06..09/13/14/15/17)
import { validarMesa, validarCupo, puedeAdministrar, ESTADOS_MESA } from '@/rules/mesas'

describe('validarMesa (alta/edición de mesa)', () => {
  const base = { nombre: 'La Cripta de Vellmar', sistema: 'pf1e', estado: 'abierta', nivel: 4, cupo: 6 }

  it('una mesa válida no trae errores', () => {
    expect(validarMesa(base)).toEqual([])
  })

  it('VAL-06 · nombre obligatorio', () => {
    expect(validarMesa({ ...base, nombre: '   ' })).toContainEqual(
      expect.objectContaining({ mensaje: 'El nombre de la mesa es obligatorio' })
    )
  })

  it('VAL-07/08 · sistema obligatorio y único valor permitido pf1e', () => {
    const sinSistema = validarMesa({ ...base, sistema: '' })
    expect(sinSistema.some((e) => e.mensaje === 'El sistema de reglas es obligatorio')).toBe(true)

    const otro = validarMesa({ ...base, sistema: 'dnd5e' })
    expect(otro.some((e) => e.mensaje.includes('pf1e'))).toBe(true)
  })

  it('VAL-09 · el estado solo puede ser abierta o cerrada', () => {
    expect(ESTADOS_MESA).toEqual(['abierta', 'cerrada'])
    expect(validarMesa({ ...base, estado: 'completa' })).toContainEqual(
      expect.objectContaining({ mensaje: 'El estado solo puede ser abierta o cerrada' })
    )
  })

  it('VAL-13 · el nivel inicial, si se informa, es entero positivo', () => {
    expect(validarMesa({ ...base, nivel: -1 })).toContainEqual(
      expect.objectContaining({ mensaje: 'El nivel inicial debe ser un entero positivo' })
    )
    expect(validarMesa({ ...base, nivel: 0 })).toContainEqual(
      expect.objectContaining({ mensaje: 'El nivel inicial debe ser un entero positivo' })
    )
    expect(validarMesa({ ...base, nivel: 4.5 })).toContainEqual(
      expect.objectContaining({ mensaje: 'El nivel inicial debe ser un entero positivo' })
    )
  })

  it('VAL-14 · el cupo, si se informa, es un entero mayor a cero (sin techo arbitrario)', () => {
    expect(validarMesa({ ...base, cupo: 0 })).toContainEqual(
      expect.objectContaining({ mensaje: 'El cupo máximo debe ser un entero mayor a cero' })
    )
    expect(validarMesa({ ...base, cupo: -2 })).toContainEqual(
      expect.objectContaining({ mensaje: 'El cupo máximo debe ser un entero mayor a cero' })
    )
    expect(validarMesa({ ...base, cupo: 20 })).not.toContainEqual(
      expect.objectContaining({ mensaje: 'El cupo máximo debe ser un entero mayor a cero' })
    )
  })
})

describe('validarCupo (RN-09 / VAL-15)', () => {
  it('el cupo nuevo no puede quedar por debajo de los jugadores actuales', () => {
    const errores = validarCupo({ actuales: 4, nuevo: 3 })
    expect(errores).toContainEqual(expect.objectContaining({ codigo: '409' }))
    expect(errores.some((e) => e.mensaje === 'El cupo no puede ser menor a los jugadores actuales')).toBe(true)
  })

  it('un cupo igual o mayor a los actuales es válido', () => {
    expect(validarCupo({ actuales: 4, nuevo: 4 })).toEqual([])
    expect(validarCupo({ actuales: 4, nuevo: 8 })).toEqual([])
  })
})

describe('puedeAdministrar (RN-02 / VAL-17)', () => {
  it('solo el GM propietario administra la mesa', () => {
    expect(puedeAdministrar({ mesa: { gmEmail: 'gm@tfinder.dev' }, email: 'gm@tfinder.dev' })).toBe(true)
    expect(puedeAdministrar({ mesa: { gmEmail: 'gm@tfinder.dev' }, email: 'otro@tfinder.dev' })).toBe(false)
  })
})
