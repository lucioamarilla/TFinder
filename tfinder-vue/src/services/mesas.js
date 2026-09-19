import mesasData from '@/data/mesas.json'

const LATENCIA_SIMULADA_MS = 400

const catalogo = mesasData.mesas.map((mesa) => ({
  ...mesa,
  etiquetas: [...mesa.etiquetas]
}))

let nextId = catalogo.length + 1

function esperar(ms = LATENCIA_SIMULADA_MS) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

function clonar(mesa) {
  return { ...mesa, etiquetas: [...mesa.etiquetas] }
}

export async function getMesas() {
  await esperar()
  return catalogo.map(clonar)
}

export async function getMesa(id) {
  await esperar()
  const mesa = catalogo.find((item) => item.id === id)
  if (!mesa) {
    throw new Error(`No encontramos ninguna mesa con el identificador "${id}".`)
  }
  return clonar(mesa)
}

export async function crearMesa(entrada) {
  await esperar(600)
  const mesa = {
    id: `mesa-${nextId++}`,
    jugadores: 0,
    estado: 'Abierta',
    etiquetas: [],
    ...entrada
  }
  catalogo.unshift(mesa)
  return clonar(mesa)
}

export async function actualizarMesa(id, cambios) {
  await esperar()
  const index = catalogo.findIndex((item) => item.id === id)
  if (index < 0) {
    throw new Error(`No encontramos ninguna mesa con el identificador "${id}".`)
  }
  catalogo[index] = { ...catalogo[index], ...cambios, etiquetas: [...(cambios.etiquetas ?? catalogo[index].etiquetas)] }
  return clonar(catalogo[index])
}

export async function eliminarMesa(id) {
  await esperar()
  const index = catalogo.findIndex((item) => item.id === id)
  if (index < 0) {
    throw new Error(`No encontramos ninguna mesa con el identificador "${id}".`)
  }
  const [removida] = catalogo.splice(index, 1)
  return removida
}