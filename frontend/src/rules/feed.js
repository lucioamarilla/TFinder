// Reglas de negocio del feed social · TFinder
// VAL-41: contenido de publicación no vacío · VAL-43 (via votos): único voto por usuario, actualizable
// RN-14: solo se publica contenido propio · RN-18: lo de mesa es solo para sus miembros

export const DIRECCIONES_VOTO = ['up', 'down']

const errorRegla = (codigo, mensaje) => ({ codigo, mensaje })

export function validarPublicacion({ titulo, contenido } = {}) {
  const errores = []

  if (typeof titulo !== 'string' || titulo.trim().length < 4) {
    errores.push(errorRegla('400', 'La publicación necesita un título'))
  }
  if (typeof contenido !== 'string' || contenido.trim() === '') {
    errores.push(errorRegla('400', 'El contenido de la publicación no puede estar vacío'))
  }

  return errores.map((e) => e.mensaje)
}

export function validarVoto(dir) {
  return DIRECCIONES_VOTO.includes(dir)
    ? null
    : errorRegla('400', 'El voto solo puede ser a favor o en contra')
}

// Delta del conteo al aplicar el voto del usuario (RN: un voto activo, actualizable).
export function aplicarVoto(votadoActual, dir) {
  if (votadoActual === dir) {
    return { delta: dir === 'up' ? -1 : 1, nuevo: null }
  }
  if (votadoActual && votadoActual !== dir) {
    return { delta: dir === 'up' ? 2 : -2, nuevo: dir }
  }
  return { delta: dir === 'up' ? 1 : -1, nuevo: dir }
}
