// Reglas de negocio de autenticación · TFinder (Documentación §13-14)
// VAL-01: correo con formato válido
// VAL-03: contraseña mínimo 8 caracteres
// VAL-05: nombre de usuario obligatorio
// Los mensajes réplican el envelope del backend {error:{codigo,mensaje}}.

export const MENSAJES_AUTH = {
  emailInvalido: 'El correo electrónico no tiene un formato válido',
  passwordCorta: 'La contraseña debe tener al menos 8 caracteres',
  nombreObligatorio: 'El nombre de usuario es obligatorio',
  correoDuplicado: 'El correo electrónico ya está registrado',
  credencialesInvalidas: 'Credenciales inválidas'
}

const PATRON_EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export function validarEmail(email) {
  if (typeof email !== 'string' || !PATRON_EMAIL.test(email.trim())) {
    return MENSAJES_AUTH.emailInvalido
  }
  return null
}

export function validarPassword(password) {
  if (typeof password !== 'string' || password.length < 8) {
    return MENSAJES_AUTH.passwordCorta
  }
  return null
}

export function validarNombre(nombre) {
  if (typeof nombre !== 'string' || nombre.trim() === '') {
    return MENSAJES_AUTH.nombreObligatorio
  }
  return null
}

export function validarRegistracion({ nombre, email, password }) {
  return validarNombre(nombre)
    ?? validarEmail(email)
    ?? validarPassword(password)
}
