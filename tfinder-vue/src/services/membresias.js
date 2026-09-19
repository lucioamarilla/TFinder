import membresiasData from '@/data/membresias.json'
import { getMesas } from './mesas'

const LATENCIA_SIMULADA_MS = 400

function esperar(ms = LATENCIA_SIMULADA_MS) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

export async function getMembresias() {
  await esperar()
  const mesas = await getMesas()
  return membresiasData.membresias.map((membresia) => {
    const mesa = mesas.find((item) => item.id === membresia.mesaId) ?? {
      id: membresia.mesaId,
      nombre: membresia.mesaId,
      plazas: 0,
      jugadores: 0,
      sistema: 'PF1e'
    }
    return {
      ...mesa,
      ...membresia,
      ocupacion: `${mesa.jugadores ?? 0}/${mesa.plazas ?? 0} Jugadores`
    }
  })
}