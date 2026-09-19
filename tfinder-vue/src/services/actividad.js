import actividadData from '@/data/actividad.json'

const LATENCIA_SIMULADA_MS = 400

function esperar(ms = LATENCIA_SIMULADA_MS) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

export async function getActividad() {
  await esperar()
  return actividadData.actividad.map((item) => ({ ...item }))
}