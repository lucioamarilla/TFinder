// Consola admin (sin datos demo).
export async function getModeracion() { return [] }
export async function ocultarCaso(id) { return true }
export async function restaurarCaso(id) { return true }
export async function eliminarCaso(id) { return true }
export async function getAdminUsuarios(filtros = {}) { return [] }
export async function suspenderUsuario(id) { return true }
export async function activarUsuario(id) { return true }
export async function getEstadisticas() { return {} }
export async function getPlataforma() { return {} }
export async function getTrazabilidad() { return [] }
export async function getObservabilidad() { return {} }
export async function getDlq() { return [] }
export async function reintentarMensaje(id) { return true }
export async function descartarMensaje(id) { return true }
export async function drenarCola() { return true }
export async function getResiliencia() { return {} }
export async function guardarResiliencia(limites) { return true }
export async function simularCaida() { return true }
export async function getComparador() { return {} }
export async function consultarMetrica(query) { return {} }
export async function getPrometheus() { return {} }