// Reglas de negocio de la wiki de campaña · TFinder
// RN-05: tres niveles de visibilidad — privada (solo GM) → jugadores (GM+miembros) → pública (todos)
// RN-18: lo público se ve sin sesión pero no es editable por terceros
// VAL-25: título obligatorio · VAL-26: tipos NPC, Lugar, Criatura, Nota, Sesión
// VAL-28: permisos de acceso según visibilidad

export const TIPOS_PAGINA = ['NPC', 'Lugar', 'Criatura', 'Nota', 'Sesión']
export const VISIBILIDADES = ['privada', 'jugadores', 'publica']

const errorRegla = (codigo, mensaje) => ({ codigo, mensaje })

export function validarPaginaWiki({ titulo, tipo, visibilidad = 'jugadores' } = {}) {
  const errores = []

  if (typeof titulo !== 'string' || titulo.trim() === '') {
    errores.push(errorRegla('400', 'El título de la página es obligatorio'))
  }

  if (!TIPOS_PAGINA.includes(tipo)) {
    errores.push(errorRegla('400', `Tipo de página inválido. Valores permitidos: ${TIPOS_PAGINA.join(', ')}`))
  }

  if (!VISIBILIDADES.includes(visibilidad)) {
    errores.push(errorRegla('400', `Visibilidad inválida. Valores permitidos: ${VISIBILIDADES.join(', ')}`))
  }

  return errores
}

export function puedeVerPaginaRegla(pagina, { esGM = false, esMiembro = false, conSesion = false } = {}) {
  const visibilidad = pagina?.visibilidad || 'publica'
  if (visibilidad === 'publica') return { ok: true }
  if (!conSesion) {
    return { ok: false, codigo: '403', mensaje: 'No tienes permisos para ver esta página' }
  }
  if (esGM) return { ok: true }
  if (visibilidad === 'jugadores' && esMiembro) return { ok: true }
  return { ok: false, codigo: '403', mensaje: 'No tienes permisos para ver esta página' }
}

// RN-18: en la demo la wiki es escrita por el GM propietario de la mesa.
export function puedeEditarPaginaRegla({ esGM } = {}) {
  return esGM
}
