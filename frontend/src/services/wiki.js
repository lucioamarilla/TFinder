// Wiki colaborativa (wiki-api).
export function paginaApi(p) {
  const cuerpo = (p.contenido || [])
    .filter((b) => typeof b?.texto === 'string' && b.texto)
    .map((b) => b.texto)
    .join('\n\n')
  return {
    id: p.id,
    mesaId: p.mesaId ?? p.mesa_id ?? null,
    carpeta: p.carpeta || 'notas',
    titulo: p.titulo,
    tipo: p.tipo || 'Nota',
    fecha: p.fecha || '',
    resumen: p.resumen || '',
    visibilidad: p.visibilidad || 'jugadores',
    contenido: Array.isArray(p.contenido) ? p.contenido : cuerpo ? [{ kind: 'parrafo', texto: cuerpo }] : [],
    cuerpo
  }
}

export async function getWiki(mesaId) {
  const { wikiApi } = await import('@/api/endpoints')
  const { datos } = await wikiApi.listar(mesaId)
  return {
    carpetas: (datos?.carpetas ?? []).map((c) => ({ ...c, count: c.count ?? 0 })),
    paginas: (datos?.paginas ?? []).map(paginaApi),
    total: datos?.total ?? 0
  }
}

export async function enviarContribucion(mesaId, paginaId, cuerpo) {
  const { wikiApi } = await import('@/api/endpoints')
  const { datos } = await wikiApi.crearContribucion(mesaId, paginaId, { cuerpo })
  return datos
}

export async function listarContribuciones(mesaId, estado = 'pendiente') {
  const { wikiApi } = await import('@/api/endpoints')
  const { datos } = await wikiApi.listarContribuciones(mesaId, estado)
  return datos ?? []
}

export async function decidirContribucion(mesaId, contribucionId, decision) {
  const { wikiApi } = await import('@/api/endpoints')
  const fn = decision === 'aprobada' ? wikiApi.aprobarContribucion : wikiApi.rechazarContribucion
  const { datos } = await fn(mesaId, contribucionId)
  return datos
}

export async function getPagina(mesaId, paginaId) {
  const { wikiApi } = await import('@/api/endpoints')
  const { datos } = await wikiApi.detallar(paginaId)
  return paginaApi(datos)
}

export async function crearPagina(mesaId, entrada) {
  const { wikiApi } = await import('@/api/endpoints')
  const { datos } = await wikiApi.crear(mesaId, {
    titulo: entrada.titulo,
    tipo: entrada.tipo || 'Nota',
    carpeta: entrada.carpeta || 'notas',
    resumen: entrada.resumen || '',
    visibilidad: (entrada.visibilidad || 'jugadores').toLowerCase(),
    cuerpo: entrada.cuerpo
      || (entrada.contenido || [])
        .filter((b) => b?.texto)
        .map((b) => b.texto)
        .join('\n\n')
  })
  return paginaApi(datos)
}

export async function actualizarPagina(mesaId, paginaId, cambios) {
  const { wikiApi } = await import('@/api/endpoints')
  const payload = {}
  for (const clave of ['titulo', 'carpeta', 'resumen']) {
    if (cambios[clave] !== undefined) payload[clave] = cambios[clave]
  }
  if (cambios.visibilidad !== undefined) payload.visibilidad = String(cambios.visibilidad).toLowerCase()
  if (cambios.tipo !== undefined) payload.tipo = cambios.tipo
  if (cambios.contenido !== undefined || cambios.cuerpo !== undefined) {
    payload.contenido = cambios.contenido
    payload.cuerpo = cambios.cuerpo
      ?? (cambios.contenido || []).filter((b) => b?.texto).map((b) => b.texto).join('\n\n')
  }
  const { datos } = await wikiApi.actualizar(paginaId, payload)
  return paginaApi(datos)
}

export async function eliminarPagina(mesaId, paginaId) {
  const { wikiApi } = await import('@/api/endpoints')
  await wikiApi.eliminar(paginaId)
  return true
}

export function clonarWiki(wiki) {
  return {
    carpetas: (wiki?.carpetas ?? []).map((c) => ({ ...c })),
    paginas: (wiki?.paginas ?? []).map((p) => ({
      ...p,
      contenido: Array.isArray(p.contenido) ? [...p.contenido] : p.contenido
    }))
  }
}