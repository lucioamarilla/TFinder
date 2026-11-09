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

// D-11: el horario sugerido de una mesa se compone desde dos pickers nativos
// (día + hora) y se persiste en el campo de texto `horario` del contrato.
// Formato canónico: "YYYY-MM-DD", "HH:MM" o "YYYY-MM-DD HH:MM".

const PATRON_DIA = /^\d{4}-\d{2}-\d{2}$/
const PATRON_HORA = /^\d{1,2}:\d{2}$/

// Normaliza "H:MM" a "HH:MM"; devuelve vacío si la hora no es reconocible.
function horaCanonica(hora) {
  const h = String(hora ?? '').trim()
  if (!PATRON_HORA.test(h)) return ''
  return `${h.split(':')[0].padStart(2, '0')}:${h.split(':')[1]}`
}

export function componerHorario(dia, hora) {
  const d = String(dia ?? '').trim()
  return [PATRON_DIA.test(d) ? d : '', horaCanonica(hora)].filter(Boolean).join(' ')
}

// Best-effort: busca la fecha ISO y la primera hora legible del texto guardado.
// Horarios heredados tipo "Jueves 21:00" aportan solo la hora; lo que no
// calza (p. ej. "V") vuelve vacío para que el picker muestre "--".
export function descomponerHorario(texto) {
  const t = String(texto ?? '').trim()
  const dia = /(\d{4}-\d{2}-\d{2})/.exec(t)?.[1] ?? ''
  const hallazgo = /(?:^|[^\d])(\d{1,2}:\d{2})(?::\d{2})?/.exec(t)
  return { dia, hora: horaCanonica(hallazgo?.[1] ?? '') }
}
