// Reglas de negocio de sesiones y diario · TFinder
// VAL-33: el resumen del diario es obligatorio
// Iniciativa: entero entre 1 y 20 (d20). Los turnos envuelven al terminar la cola.

const errorRegla = (codigo, mensaje) => ({ codigo, mensaje })

export function validarDiario(resumen) {
  if (typeof resumen !== 'string' || resumen.trim() === '') {
    return 'El resumen del diario es obligatorio'
  }
  return null
}

export function validarCombatiente({ nombre, init, pv = 0, pvMax = 1 } = {}) {
  const errores = []

  if (typeof nombre !== 'string' || nombre.trim() === '') {
    errores.push(errorRegla('400', 'El nombre del combatiente es obligatorio'))
  }

  const iniciativa = Number(init)
  if (!Number.isInteger(iniciativa) || iniciativa < 1 || iniciativa > 20) {
    errores.push(errorRegla('400', 'La iniciativa debe ser un entero entre 1 y 20'))
  }

  const vida = Number(pv)
  const vidaMax = Number(pvMax)
  if (!Number.isInteger(vida) || vida < 0 || !Number.isInteger(vidaMax) || vidaMax < 0) {
    errores.push(errorRegla('400', 'Los puntos de vida deben ser enteros no negativos'))
  }

  return errores
}

export function siguienteTurno(turnoActual, cantidad) {
  if (cantidad <= 0) return 0
  return (Number(turnoActual) + 1) % cantidad
}
