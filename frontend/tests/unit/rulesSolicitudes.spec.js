// RED Fase 2 · Reglas de solicitudes de unión (RN-07/08/09, VAL-18..24, Idempotencia RN-20/VAL-46)
import {
  puedoSolicitarUnion,
  aceptarSolicitud,
  rechazarSolicitud,
  claveIdempotencia
} from '@/rules/solicitudes'

const MESA_ABIERTA = { id: 'vellmar', nombre: 'La Cripta de Vellmar', estado: 'abierta', cupo: 5 }
const EMAIL = 'aldric@tfinder.dev'

describe('puedoSolicitarUnion (VAL-18/19/20)', () => {
  it('404 · la mesa debe existir para solicitar unión', () => {
    expect(puedoSolicitarUnion({ mesa: null })).toEqual([
      expect.objectContaining({ codigo: '404' })
    ])
  })

  it('VAL-18 · una mesa cerrada no acepta solicitudes (409)', () => {
    expect(puedoSolicitarUnion({ mesa: { ...MESA_ABIERTA, estado: 'cerrada' }, email: EMAIL, solicitudes: [], esMiembro: false }))
      .toContainEqual(expect.objectContaining({ codigo: '409', mensaje: 'La mesa está cerrada y no acepta solicitudes' }))
  })

  it('VAL-19 · un miembro no puede volver a solicitar unión', () => {
    expect(puedoSolicitarUnion({ mesa: MESA_ABIERTA, email: EMAIL, solicitudes: [], esMiembro: true }))
      .toContainEqual(expect.objectContaining({ codigo: '409', mensaje: 'Ya eres miembro de esta mesa' }))
  })

  it('VAL-20/RN-07 · máx una solicitud pendiente por jugador por mesa', () => {
    expect(puedoSolicitarUnion({
      mesa: MESA_ABIERTA,
      email: EMAIL,
      solicitudes: [{ jugadorEmail: EMAIL, estado: 'pendiente' }],
      esMiembro: false
    })).toContainEqual(expect.objectContaining({ codigo: '409', mensaje: 'Ya tienes una solicitud pendiente en esta mesa' }))
  })

  it('una solicitud rechazada previa permite volver a solicitar (RN-07)', () => {
    expect(puedoSolicitarUnion({
      mesa: MESA_ABIERTA,
      email: EMAIL,
      solicitudes: [{ jugadorEmail: EMAIL, estado: 'rechazada' }],
      esMiembro: false
    })).toEqual([])
  })

  it('una mesa abierta sin historial permite solicitar', () => {
    expect(puedoSolicitarUnion({ mesa: MESA_ABIERTA, email: EMAIL, solicitudes: [], esMiembro: false })).toEqual([])
  })
})

describe('aceptar/rechazar solicitud (VAL-21/22, RN-08/09)', () => {
  const PENDIENTE = { id: 's1', mesaId: MESA_ABIERTA.id, jugadorEmail: EMAIL, estado: 'pendiente' }

  it('VAL-21 · solicitar aceptación de una solicitud inexistente es 404', () => {
    expect(aceptarSolicitud({ mesa: MESA_ABIERTA, solicitud: null, actuales: 2 }))
      .toContainEqual(expect.objectContaining({ codigo: '404' }))
  })

  it('VAL-22 · una solicitud ya procesada no puede re-procesarse', () => {
    expect(aceptarSolicitud({ mesa: MESA_ABIERTA, solicitud: { ...PENDIENTE, estado: 'aceptada' }, actuales: 2 }))
      .toContainEqual(expect.objectContaining({ codigo: '409', mensaje: 'La solicitud ya fue procesada' }))
  })

  it('RN-09 · aceptar cuando la mesa no tiene vacantes es 409 y NO marca como procesada', () => {
    const errores = aceptarSolicitud({ mesa: MESA_ABIERTA, solicitud: PENDIENTE, actuales: 5 })
    expect(errores).toContainEqual(expect.objectContaining({ codigo: '409', mensaje: 'La mesa no puede exceder su cupo máximo' }))
  })

  it('aceptar con vacante es válido (RN-08 convierte al jugador en miembro en la capa del store)', () => {
    expect(aceptarSolicitud({ mesa: MESA_ABIERTA, solicitud: PENDIENTE, actuales: 4 })).toEqual([])
  })

  it('rechazar una solicitud ya procesada también es 409', () => {
    expect(rechazarSolicitud({ solicitud: { ...PENDIENTE, estado: 'rechazada' } }))
      .toContainEqual(expect.objectContaining({ codigo: '409', mensaje: 'La solicitud ya fue procesada' }))
  })

  it('rechazar una solicitud pendiente es válido', () => {
    expect(rechazarSolicitud({ solicitud: PENDIENTE })).toEqual([])
  })
})

describe('claveIdempotencia (RN-20 / VAL-46)', () => {
  it('genera UUIDs diferentes por defecto', () => {
    const a = claveIdempotencia()
    const b = claveIdempotencia()
    expect(a).not.toBe(b)
  })

  it('devuelve la clave recibida cuando la vista provee una (reintento idempotente)', () => {
    expect(claveIdempotencia('mi-clave')).toBe('mi-clave')
  })

  it('el formato del UUID es 8-4-4-4-12', () => {
    expect(claveIdempotencia()).toMatch(/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/)
  })
})
