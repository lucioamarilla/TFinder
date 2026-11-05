// Reglas de negocio de builds PF1e · TFinder
// VAL-44: clase obligatoria · VAL-45: atributos básicos 3–18
// CA-42/CA-43: construir sin clase o con atributo fuera de rango → 400

export const ATRIBUTOS_PF1E = ['FUE', 'DES', 'CON', 'INT', 'SAB', 'CAR']

export function validarAtributos(atributos = {}) {
  const errores = []
  for (const clave of ATRIBUTOS_PF1E) {
    const valor = atributos[clave]
    if (valor === undefined || valor === null || valor === '') continue
    const numero = Number(valor)
    if (!Number.isInteger(numero) || numero < 3 || numero > 18) {
      errores.push(`El atributo ${clave} debe estar entre 3 y 18`)
    }
  }
  return errores
}

export const TIPOS_BUILD = ['personaje', 'objeto', 'lugar', 'criatura', 'nota']

export function validarBuild({ tipo = 'personaje', clase, nivel, atributos, nombre, titulo, detalle, ficha } = {}) {
  const errores = []
  const tipoNormalizado = String(tipo || 'personaje').trim().toLowerCase()
  if (!TIPOS_BUILD.includes(tipoNormalizado)) {
    errores.push('El tipo de build debe ser personaje, objeto, lugar, criatura o nota')
    return errores
  }

  if (tipoNormalizado === 'personaje') {
    if (typeof clase !== 'string' || clase.trim() === '') {
      errores.push('La clase de personaje es obligatoria')
    }
    if (nivel !== undefined && nivel !== null) {
      const numero = Number(nivel)
      if (!Number.isInteger(numero) || numero < 1 || numero > 20) {
        errores.push('El nivel debe estar entre 1 y 20')
      }
    }
    if (atributos && typeof atributos === 'object') {
      for (const clave of ATRIBUTOS_PF1E) {
        const valor = atributos[clave]
        if (valor === undefined || valor === null || valor === '') continue
        const numero = Number(valor)
        if (!Number.isInteger(numero) || numero < 3 || numero > 18) {
          errores.push(`El atributo ${clave} debe estar entre 3 y 18`)
        }
      }
    }
  } else {
    const nombreFinal = nombre || titulo
    if (typeof nombreFinal !== 'string' || nombreFinal.trim() === '') {
      errores.push('El nombre de la creación es obligatorio')
    }
    if (tipoNormalizado === 'nota') {
      const cuerpo = detalle || (ficha && ficha.cuerpo)
      if (typeof cuerpo !== 'string' || cuerpo.trim() === '') {
        errores.push('El cuerpo de la nota es obligatorio')
      }
    }
    if (tipoNormalizado === 'lugar') {
      if (typeof detalle !== 'string' || detalle.trim() === '') {
        errores.push('La descripción del lugar es obligatoria')
      }
    }
  }

  return errores
}
