import jugadoresData from '@/data/jugadores.json'

const LATENCIA_SIMULADA_MS = 300

function esperar(ms = LATENCIA_SIMULADA_MS) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

const capacidad = jugadoresData.capacidad

const registro = Object.entries(jugadoresData.mesas).reduce((acc, [mesaId, dato]) => {
  acc[mesaId] = {
    miembros: dato.miembros.map((m) => ({ ...m })),
    solicitudes: dato.solicitudes.map((s) => ({ ...s }))
  }
  return acc
}, {})

function clonar(dato) {
  return {
    miembros: dato.miembros.map((m) => ({ ...m })),
    solicitudes: dato.solicitudes.map((s) => ({ ...s }))
  }
}

function getInterno(mesaId) {
  if (!registro[mesaId]) registro[mesaId] = { miembros: [], solicitudes: [] }
  return registro[mesaId]
}

export async function getMiembros(mesaId) {
  await esperar()
  const dato = getInterno(mesaId)
  return { miembros: dato.miembros.map((m) => ({ ...m })), capacidad }
}

export async function getSolicitudes(mesaId) {
  await esperar()
  return getInterno(mesaId).solicitudes.map((s) => ({ ...s }))
}

export async function aceptarSolicitud(mesaId, solicitudId) {
  await esperar()
  const dato = getInterno(mesaId)
  const index = dato.solicitudes.findIndex((s) => s.id === solicitudId)
  if (index < 0) throw new Error(`No encontramos la solicitud a aceptar.`)
  const [candidato] = dato.solicitudes.splice(index, 1)
  dato.miembros.push({
    id: `miembro-${candidato.id}`,
    nombre: candidato.nombre,
    avatar: candidato.avatar,
    personaje: candidato.personaje,
    clase: candidato.clase,
    nivel: candidato.nivel,
    estado: 'Activo',
    rol: 'Jugador',
    buildVinculado: false,
    fecha: 'Acaba de incorporarse'
  })
  return clonar(dato)
}

export async function rechazarSolicitud(mesaId, solicitudId) {
  await esperar()
  const dato = getInterno(mesaId)
  const index = dato.solicitudes.findIndex((s) => s.id === solicitudId)
  if (index < 0) throw new Error(`No encontramos la solicitud a rechazar.`)
  dato.solicitudes.splice(index, 1)
  return true
}

export async function expulsarMiembro(mesaId, miembroId) {
  await esperar()
  const dato = getInterno(mesaId)
  const index = dato.miembros.findIndex((m) => m.id === miembroId)
  if (index < 0) throw new Error(`No encontramos al miembro a expulsar.`)
  const [expulsado] = dato.miembros.splice(index, 1)
  return expulsado
}