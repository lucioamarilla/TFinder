import votacionesData from '@/data/votaciones.json'

const LATENCIA_SIMULADA_MS = 300

const latencia = () => new Promise((resolve) => setTimeout(resolve, LATENCIA_SIMULADA_MS))

const registro = Object.entries(votacionesData.mesas).reduce((acc, [mesaId, lista]) => {
  acc[mesaId] = lista.map((v) => ({
    ...v,
    favor: [...v.favor],
    contra: [...v.contra]
  }))
  return acc
}, {})

function clonar(votacion) {
  return { ...votacion, favor: [...votacion.favor], contra: [...votacion.contra] }
}

function getInterno(mesaId) {
  if (!registro[mesaId]) registro[mesaId] = []
  return registro[mesaId]
}

export async function getVotaciones(mesaId) {
  await latencia()
  return getInterno(mesaId).map(clonar)
}

export async function votar(mesaId, votacionId, direccion) {
  await latencia()
  const index = getInterno(mesaId).findIndex((v) => v.id === votacionId)
  if (index < 0) throw new Error(`No encontramos la propuesta para votar.`)
  const votacion = getInterno(mesaId)[index]
  if (votacion.miVoto === direccion) {
    if (votacion.miVoto === 'favor') {
      votacion.favor = votacion.favor.filter((n) => n !== 'Tú (Aldren)')
    } else {
      votacion.contra = votacion.contra.filter((n) => n !== 'Tú (Aldren)')
    }
    votacion.miVoto = null
    return clonar(votacion)
  }
  if (votacion.miVoto === 'favor') {
    votacion.favor = votacion.favor.filter((n) => n !== 'Tú (Aldren)')
  } else if (votacion.miVoto === 'contra') {
    votacion.contra = votacion.contra.filter((n) => n !== 'Tú (Aldren)')
  }
  if (direccion === 'favor') {
    if (!votacion.favor.includes('Tú (Aldren)')) votacion.favor.push('Tú (Aldren)')
  } else if (direccion === 'contra') {
    if (!votacion.contra.includes('Tú (Aldren)')) votacion.contra.push('Tú (Aldren)')
  }
  votacion.miVoto = direccion
  return clonar(votacion)
}

export async function proponerFecha(mesaId, { fecha, sesionNumero, titulo }) {
  await latencia(450)
  const propuesta = {
    id: `vot-prop-${Date.now()}`,
    sesionNumero: sesionNumero || '#30',
    titulo: titulo || 'Sesión Extraordinaria',
    resumen: 'Nueva convocatoria propuesta por el Director de Juego.',
    fecha,
    tipo: 'PROPUESTA OFICIAL GM',
    favor: ['Aldren (GM)'],
    contra: [],
    miVoto: null
  }
  getInterno(mesaId).unshift(propuesta)
  return clonar(propuesta)
}

export async function confirmarFecha(mesaId, votacionId) {
  await latencia(450)
  const index = getInterno(mesaId).findIndex((v) => v.id === votacionId)
  if (index < 0) throw new Error(`No encontramos la propuesta a confirmar.`)
  const [propuesta] = getInterno(mesaId).splice(index, 1)
  return clonar(propuesta)
}