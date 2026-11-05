// Reglas de negocio de solicitudes de unión · TFinder (Documentación §13.1 / §14)
// RN-07: máxima 1 solicitud "pendiente" por jugador por mesa (rechazada se puede reenviar)
// RN-08: al aceptar, el jugador es automáticamente miembro con rol "jugador"
// RN-09: la mesa no puede exceder su cupo máximo
// RN-20/VAL-46: idempotencia con claves UUID
// VAL-18: mesa "abierta" para solicitar · VAL-19: no ser miembro · VAL-20: sin pendiente previa
// VAL-21/22/23/24: solicitud existente, solo pendiente, solo GM, acción válida

const errorRegla = (codigo, mensaje) => ({ codigo, mensaje })

export function puedoSolicitarUnion({ mesa, solicitudes = [], esMiembro = false } = {}) {
  if (!mesa) return [errorRegla('404', 'Mesa inexistente')]

  if (mesa.estado !== 'abierta') {
    return [errorRegla('409', 'La mesa está cerrada y no acepta solicitudes')]
  }
  if (esMiembro) {
    return [errorRegla('409', 'Ya eres miembro de esta mesa')]
  }
  if (solicitudes.some((s) => s.estado === 'pendiente')) {
    return [errorRegla('409', 'Ya tienes una solicitud pendiente en esta mesa')]
  }
  return []
}

export function aceptarSolicitud({ mesa, solicitud, actuales } = {}) {
  if (!solicitud) return [errorRegla('404', 'Solicitud inexistente')]
  if (solicitud.estado !== 'pendiente') {
    return [errorRegla('409', 'La solicitud ya fue procesada')]
  }
  if (!mesa || Number(actuales) >= Number(mesa.cupo)) {
    return [errorRegla('409', 'La mesa no puede exceder su cupo máximo')]
  }
  return []
}

export function rechazarSolicitud({ solicitud } = {}) {
  if (!solicitud) return [errorRegla('404', 'Solicitud inexistente')]
  if (solicitud.estado !== 'pendiente') {
    return [errorRegla('409', 'La solicitud ya fue procesada')]
  }
  return []
}

export function validarAccionSolicitud(accion) {
  return ['aceptar', 'rechazar'].includes(accion)
    ? null
    : errorRegla('400', "La acción solo puede ser 'aceptar' o 'rechazar'")
}

let contadorFallback = 0
export function claveIdempotencia(clave) {
  if (clave) return clave
  try {
    return crypto.randomUUID()
  } catch {
    contadorFallback += 1
    const hex = (n) => Array.from({ length: n }, () => Math.floor(Math.random() * 16).toString(16)).join('')
    return `${hex(8)}-4${hex(3)}-a${hex(3)}-8${hex(3)}-${hex(12)}`
  }
}
