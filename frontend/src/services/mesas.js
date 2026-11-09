// Catálogo de mesas (mesas-api).
let ultimaMedicionMs = 0

export function ultimaMedicion() {
  return ultimaMedicionMs
}

// D-09: el literal del contrato es 'abierta'|'cerrada'; los normalizadores
// exponen 'Abierta'/'Cerrada' para la UI. Un único punto de comparación.
export function estadoCrudo(mesa) {
  return String(mesa?.estado ?? '').trim().toLowerCase()
}

export function esMesaAbierta(mesa) {
  return estadoCrudo(mesa) === 'abierta'
}

export function esMesaCerrada(mesa) {
  return estadoCrudo(mesa) === 'cerrada'
}

// D-10: cupo/plazas/jugadores_max son el mismo dato con tres nombres.
export function cupoDe(mesa) {
  return mesa?.plazas ?? mesa?.cupo ?? null
}

export function ocupacionDe(mesa) {
  return mesa?.jugadores ?? 0
}


export function normalizarMesa(m) {
  // MesaOut del backend → forma de pergamino del frontend.
  if (m && (m.gmId !== undefined || m.gm_id !== undefined || m.jugadoresActuales !== undefined || m.jugadores_actuales !== undefined || m.jugadoresMax !== undefined || m.jugadores_max !== undefined || m.plazas === undefined)) {
    const jugadores = m.jugadoresActuales ?? m.jugadores_actuales ?? 0
    const cupo = m.jugadoresMax ?? m.jugadores_max ?? null
    const abierta = (m.estado ?? 'abierta') === 'abierta'
    return {
      id: m.id,
      nombre: m.nombre,
      sistema: String(m.sistema ?? 'pf1e').toUpperCase(),
      descripcion: m.descripcion ?? '',
      tono: m.tono ?? '',
      horario: m.horario ?? '',
      estado: abierta ? 'Abierta' : 'Cerrada',
      estadoCategoria: abierta ? 'Abierta' : 'Cerrada',
      rangoNivel: m.nivelInicial ?? m.nivel_inicial ? `Nivel ${m.nivelInicial ?? m.nivel_inicial}` : '—',
      nivel: m.nivelInicial ?? m.nivel_inicial ?? null,
      jugadores,
      plazas: cupo,
      vacante: cupo === null ? abierta : jugadores < cupo && abierta,
      etiquetas: [],
      gm: m.gmNombre ?? m.gm_nombre ?? m.gm ?? '',
      gmId: m.gmId ?? m.gm_id ?? null,
      modalidad: 'Presencial u online',
      ubicacion: m.lugar ?? '',
      frecuencia: m.horario ?? 'A coordinar',
      proximaSesion: 'Por definir',
      lore: m.descripcion || 'Crónica activa de la comunidad.'
    }
  }
  // Forma demo/ya normalizada (compatibilidad).
  const jugadores = (typeof m?.jugadores === 'number') ? m.jugadores : 0
  return {
    id: m.id,
    nombre: m.nombre,
    sistema: m.sistema ?? 'PF1e',
    descripcion: m.descripcion ?? '',
    tono: m.tono ?? '',
    horario: m.horario ?? '',
    estado: m.estado === 'abierta' || m.estado === 'Abierta' ? 'Abierta' : 'Cerrada',
    estadoCategoria: m.estado === 'abierta' || m.estado === 'Abierta' ? 'Abierta' : 'Cerrada',
    rangoNivel: m.nivel ? `Nivel ${m.nivel}` : '—',
    nivel: m.nivel,
    jugadores,
    plazas: m.cupo ?? m.plazas,
    vacante: jugadores < (m.cupo ?? m.plazas ?? 0) && (m.estado === 'abierta' || m.estado === 'Abierta'),
    etiquetas: m.etiquetas ?? [],
    gm: m.gm ?? '',
    gmId: m.gmId ?? null,
    modalidad: 'Presencial u online',
    ubicacion: m.lugar ?? m.ubicacion ?? '',
    frecuencia: m.horario ?? 'A coordinar',
    proximaSesion: 'Por definir',
    lore: m.descripcion || 'Crónica activa de la comunidad.'
  }
}

export async function getMesas() {
  const t0 = performance.now()
  try {
    const { mesasApi } = await import('@/api/endpoints')
    const { datos } = await mesasApi.listar()
    return (datos ?? []).map(normalizarMesa)
  } finally {
    ultimaMedicionMs = Math.round(performance.now() - t0)
  }
}

export async function getMisMesas() {
  const { mesasApi } = await import('@/api/endpoints')
  const { datos } = await mesasApi.listarmias()
  return (datos ?? []).map((m) => ({ ...normalizarMesa(m), miRol: m.mi_rol ?? 'jugador' }))
}

export async function getMesa(id) {
  try {
    const { mesasApi } = await import('@/api/endpoints')
    const { datos } = await mesasApi.detalle(id)
    return normalizarMesa(datos)
  } catch (e) {
    if (String(e?.codigo) === '404') {
      const err = new Error(`No encontramos ninguna mesa con el identificador "${id}".`)
      err.codigo = '404'
      throw err
    }
    throw e
  }
}

export async function crearMesa(entrada, opciones = {}) {
  const { mesasApi } = await import('@/api/endpoints')
  const { datos } = await mesasApi.crear({
    nombre: entrada.nombre,
    sistema: 'pf1e',
    estado: (entrada.estado ?? 'abierta').toLowerCase(),
    descripcion: entrada.descripcion ?? '',
    tono: entrada.tono ?? '',
    // D-08: frecuencia y horario son dos nombres de vista para el mismo
    // dato del contrato; mapear ambos evita perder el horario al crear.
    horario: entrada.horario ?? entrada.frecuencia ?? '',
    nivel_inicial: (entrada.nivel_inicial ?? entrada.nivel) != null && (entrada.nivel_inicial ?? entrada.nivel) !== ''
      ? Number(entrada.nivel_inicial ?? entrada.nivel)
      : null,
    jugadores_max: entrada.jugadores_max ?? entrada.cupo ?? null
  })
  return normalizarMesa(datos)
}

export async function actualizarMesa(id, cambios, opciones = {}) {
  const { mesasApi } = await import('@/api/endpoints')
  const payload = {}
  if (cambios.nombre !== undefined) payload.nombre = cambios.nombre
  if (cambios.descripcion !== undefined) payload.descripcion = cambios.descripcion
  if (cambios.horario !== undefined) payload.horario = cambios.horario
  if (cambios.frecuencia !== undefined) payload.horario = cambios.frecuencia
  if (cambios.estado !== undefined) payload.estado = String(cambios.estado).toLowerCase()
  if (cambios.cupo !== undefined) payload.jugadores_max = cambios.cupo
  if (cambios.plazas !== undefined) payload.jugadores_max = cambios.plazas
  if (cambios.nivel !== undefined && cambios.nivel !== null && cambios.nivel !== '') payload.nivel_inicial = Number(cambios.nivel)
  if (cambios.tono !== undefined) payload.tono = cambios.tono
  const { datos } = await mesasApi.actualizar(id, payload)
  return normalizarMesa(datos)
}

export async function eliminarMesa(id, opciones = {}) {
  const { mesasApi } = await import('@/api/endpoints')
  await mesasApi.eliminar(id)
  return true
}
