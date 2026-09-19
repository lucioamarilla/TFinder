import wikiData from '@/data/wiki.json'

const LATENCIA_SIMULADA_MS = 350

function esperar(ms = LATENCIA_SIMULADA_MS) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

const registro = Object.entries(wikiData.arboles).reduce((acc, [mesaId, arbol]) => {
  acc[mesaId] = { carpetas: [...arbol.carpetas], paginas: [...arbol.paginas] }
  return acc
}, {})

function clonarWiki(wiki) {
  return {
    carpetas: wiki.carpetas.map((c) => ({ ...c })),
    paginas: wiki.paginas.map((p) => ({
      ...p,
      contenido: [...p.contenido]
    }))
  }
}

function getWikiInterno(mesaId) {
  let wiki = registro[mesaId]
  if (!wiki) {
    wiki = { carpetas: [], paginas: [] }
    registro[mesaId] = wiki
  }
  return wiki
}

export async function getWiki(mesaId) {
  await esperar()
  const wiki = getWikiInterno(mesaId)
  return {
    carpetas: wiki.carpetas.map((c) => ({
      ...c,
      count: wiki.paginas.filter((p) => p.carpeta === c.id).length
    })),
    paginas: wiki.paginas.map((p) => ({ ...p })),
    total: wiki.paginas.length
  }
}

export async function getPagina(mesaId, paginaId) {
  await esperar()
  const wiki = getWikiInterno(mesaId)
  const pagina = wiki.paginas.find((p) => p.id === paginaId)
  if (!pagina) {
    throw new Error(`No encontramos la página "«${paginaId}»" en el grimorio de esta mesa.`)
  }
  return { ...pagina, contenido: [...pagina.contenido] }
}

export async function crearPagina(mesaId, entrada) {
  await esperar()
  const wiki = getWikiInterno(mesaId)
  const ahora = 'hoy en el grimorio'
  const pagina = {
    id: `pagina-${Date.now()}-${Math.floor(Math.random() * 1000)}`,
    carpeta: entrada.carpeta || 'notas',
    tipo: entrada.tipo || 'NOTA',
    fecha: entrada.fecha || 'HOY',
    resumen: entrada.resumen || '',
    contenido: [],
    ...entrada,
    fecha: entrada.fecha || ahora
  }
  wiki.paginas.push(pagina)
  return { ...pagina }
}

export async function actualizarPagina(mesaId, paginaId, cambios) {
  await esperar()
  const wiki = getWikiInterno(mesaId)
  const index = wiki.paginas.findIndex((p) => p.id === paginaId)
  if (index < 0) {
    throw new Error(`No encontramos la página para actualizar.`)
  }
  wiki.paginas[index] = {
    ...wiki.paginas[index],
    ...cambios,
    contenido: [...(cambios.contenido ?? wiki.paginas[index].contenido)]
  }
  return { ...wiki.paginas[index] }
}

export async function eliminarPagina(mesaId, paginaId) {
  await esperar()
  const wiki = getWikiInterno(mesaId)
  const index = wiki.paginas.findIndex((p) => p.id === paginaId)
  if (index < 0) throw new Error(`No encontramos la página a eliminar.`)
  wiki.paginas.splice(index, 1)
  return true
}

export { clonarWiki }