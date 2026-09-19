import eventosData from '@/data/eventos.json'
import { getMesas } from './mesas'

const LATENCIA_SIMULADA_MS = 400

function esperar(ms = LATENCIA_SIMULADA_MS) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

export async function getEventosProximos() {
  await esperar()
  const mesas = await getMesas()
  return eventosData.eventos.map((evento) => {
    const mesa = mesas.find((item) => item.id === evento.mesaId)
    return { ...evento, mesaNombre: mesa?.nombre ?? evento.mesaId }
  })
}