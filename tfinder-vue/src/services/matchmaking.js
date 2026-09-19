import matchmakingData from '@/data/matchmaking.json'

const LATENCIA_SIMULADA_MS = 350

const latencia = () => new Promise((resolve) => setTimeout(resolve, LATENCIA_SIMULADA_MS))

const catalogo = matchmakingData.candidatos.map((c) => ({ ...c }))

function coincide(candidato, filtros) {
  if (!filtros) return true
  const rol = filtros.rol && filtros.rol !== 'Indistinto' ? candidato.rol === filtros.rol : true
  const modalidad = filtros.modalidad ? candidato.modalidad === filtros.modalidad : true
  const disponibilidad = filtros.disponibilidad ? candidato.disponibilidad === filtros.disponibilidad : true
  return rol && modalidad && disponibilidad
}

export async function getCandidatos(filtros) {
  await latencia()
  return catalogo.filter((c) => coincide(c, filtros)).map((c) => ({ ...c }))
}

export async function anotarseEnLlamadoAbierto() {
  await latencia(250)
  return true
}

export async function enviarSolicitud(id) {
  await latencia(250)
  const candidato = catalogo.find((c) => c.id === id)
  if (!candidato) throw new Error('No encontramos a ese aventurero en el registro del gremio.')
  return { ...candidato }
}
