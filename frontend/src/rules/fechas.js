// Reglas de negocio del calendario de fechas · TFinder
// RN-06: un voto (a favor/en contra) por jugador por fecha propuesta; actualizable, no duplicable
// RN-17: solo miembros con rol jugador (o co-GM futuro) votan; el GM no vota lo que propone
// VAL-29: la fecha propuesta no puede ser anterior a hoy
// VAL-30: el voto es 'a favor' o 'en contra'
// VAL-31: el votante debe ser miembro de la mesa
// VAL-32: no se duplican votos — se actualiza el propio

const errorRegla = (codigo, mensaje) => ({ codigo, mensaje })

export function validarFechaPropuesta(fecha) {
  if (typeof fecha !== 'string' || fecha.trim() === '') {
    return 'La fecha propuesta es obligatoria'
  }
  const d = new Date(`${fecha}T00:00:00`)
  if (Number.isNaN(d.getTime())) {
    return 'La fecha propuesta no tiene un formato válido'
  }
  const hoy = new Date()
  hoy.setHours(0, 0, 0, 0)
  if (d < hoy) {
    return 'La fecha propuesta no puede ser anterior a hoy'
  }
  return null
}

export function validarVotoFecha(dir) {
  if (dir !== 'favor' && dir !== 'contra') {
    return "El voto solo puede ser 'a favor' o 'en contra'"
  }
  return null
}

export function puedeVotarFecha({ esGM = false, esMiembro = false } = {}) {
  if (esGM) return { ok: false, codigo: '403', mensaje: 'El GM no puede votar sus propias propuestas' }
  if (!esMiembro) return { ok: false, codigo: '403', mensaje: 'Solo los miembros de la mesa pueden votar fechas' }
  return { ok: true }
}
