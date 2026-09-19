import sesionesData from '@/data/sesiones.json'

const LATENCIA_SIMULADA_MS = 300

function esperar(ms = LATENCIA_SIMULADA_MS) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

const registro = Object.entries(sesionesData.sesiones).reduce((acc, [mesaId, lista]) => {
  acc[mesaId] = lista.map((s) => ({ ...s }))
  return acc
}, {})

function clonarSesion(sesion) {
  return { ...sesion, diario: sesion.diario ? String(sesion.diario) : null }
}

function getInterno(mesaId) {
  if (!registro[mesaId]) registro[mesaId] = []
  return registro[mesaId]
}

export async function getSesiones(mesaId) {
  await esperar()
  return getInterno(mesaId).map(clonarSesion)
}

export async function getSesion(mesaId, sesionId) {
  await esperar()
  const sesion = getInterno(mesaId).find((s) => s.id === sesionId)
  if (!sesion) {
    throw new Error(`No encontramos la sesión «${sesionId}» en el archivo de campaña.`)
  }
  return clonarSesion(sesion)
}

export async function registrarDiario(mesaId, sesionId) {
  await esperar()
  const index = getInterno(mesaId).findIndex((s) => s.id === sesionId)
  if (index < 0) throw new Error(`No encontramos la sesión para registrar su diario.`)
  getInterno(mesaId)[index].pendienteDiario = false
  return clonarSesion(getInterno(mesaId)[index])
}

export async function guardarDiario(mesaId, sesionId, diario) {
  await esperar(450)
  const index = getInterno(mesaId).findIndex((s) => s.id === sesionId)
  if (index < 0) throw new Error(`No encontramos la sesión para guardar el diario.`)
  getInterno(mesaId)[index].diario = diario
  getInterno(mesaId)[index].pendienteDiario = false
  return clonarSesion(getInterno(mesaId)[index])
}