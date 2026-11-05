// Reglas de negocio de mesas · TFinder (Documentación §13.1 / §14)
// RN-02: el GM que crea la mesa es su único propietario
// RN-04: estados únicamente "abierta" | "cerrada"
// RN-09: la mesa no puede exceder su cupo máximo
// VAL-06/07/08: nombre y sistema (único valor permitido: pf1e) obligatorios
// VAL-09/13/14: estado de dominio, nivel entero positivo, cupo entero > 0
// VAL-15: cupo >= jugadores actuales; VAL-17: solo GM propietario administra

export const ESTADOS_MESA = ['abierta', 'cerrada']
export const SISTEMA_UNICO = 'pf1e'

const errorRegla = (codigo, mensaje) => ({ codigo, mensaje })

export function validarMesa({ nombre, sistema, estado = 'abierta', nivel = null, cupo = null } = {}) {
  const errores = []

  if (typeof nombre !== 'string' || nombre.trim() === '') {
    errores.push(errorRegla('400', 'El nombre de la mesa es obligatorio'))
  }

  if (typeof sistema !== 'string' || sistema.trim() === '') {
    errores.push(errorRegla('400', 'El sistema de reglas es obligatorio'))
  } else if (sistema.trim() !== SISTEMA_UNICO) {
    errores.push(errorRegla('400', `Sistema de reglas inválido. Valores permitidos: ${SISTEMA_UNICO}`))
  }

  if (!ESTADOS_MESA.includes(estado)) {
    errores.push(errorRegla('400', 'El estado solo puede ser abierta o cerrada'))
  }

  if (nivel !== null && nivel !== undefined && nivel !== '') {
    const numero = Number(nivel)
    if (!Number.isInteger(numero) || numero <= 0) {
      errores.push(errorRegla('400', 'El nivel inicial debe ser un entero positivo'))
    }
  }

  if (cupo !== null && cupo !== undefined && cupo !== '') {
    const numero = Number(cupo)
    if (!Number.isInteger(numero) || numero <= 0) {
      errores.push(errorRegla('400', 'El cupo máximo debe ser un entero mayor a cero'))
    }
  }

  return errores
}

export function validarCupo({ actuales, nuevo } = {}) {
  const numero = Number(nuevo)
  if (!Number.isInteger(numero) || numero < Number(actuales)) {
    return [errorRegla('409', 'El cupo no puede ser menor a los jugadores actuales')]
  }
  return []
}

export function puedeAdministrar({ mesa, email } = {}) {
  if (!mesa || typeof email !== 'string') return false
  return mesa.gmEmail === email
}
