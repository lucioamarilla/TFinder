import { mesasApi } from '@/api/endpoints'

let ultimaMedicionMs = 0

export function ultimaMedicion() {
  return ultimaMedicionMs
}

function normalizar(m) {
  return {
    id: m.id,
    nombre: m.nombre,
    sistema: m.sistema ?? 'PF1e',
    descripcion: m.descripcion ?? '',
    tono: m.tono ?? '',
    horario: m.horario ?? '',
    estado: m.estado === 'abierta' ? 'Abierta' : 'Cerrada',
    estadoCategoria: m.estado === 'abierta' ? 'Abierta' : 'Cerrada',
    rangoNivel: m.nivel_inicial ? `Nivel ${m.nivel_inicial}` : '—',
    nivel: m.nivel_inicial,
    jugadores: m.jugadores_actuales ?? 0,
    plazas: m.jugadores_max ?? 0,
    vacante: (m.jugadores_actuales ?? 0) < (m.jugadores_max ?? 0),
    etiquetas: m.etiquetas ?? [],
    gm: 'Gestionada por el Cónclave',
    modalidad: 'Online',
    ubicacion: 'Discord',
    frecuencia: m.horario ?? 'A coordinar',
    proximaSesion: 'Por definir',
    lore: m.descripcion || 'Crónica activa de la comunidad.'
  }
}

export async function getMesas() {
  const t0 = performance.now()
  const { datos } = await mesasApi.listar()
  ultimaMedicionMs = Math.round(performance.now() - t0)
  return (datos ?? []).map(normalizar)
}

export async function getMesa(id) {
  const { datos } = await mesasApi.detalle(id)
  return normalizar(datos)
}

export async function crearMesa(entrada) {
  const { datos } = await mesasApi.crear(entrada)
  return normalizar(datos)
}

export async function actualizarMesa(id, cambios) {
  const { datos } = await mesasApi.actualizar(id, cambios)
  return normalizar(datos)
}

export async function eliminarMesa(id) {
  await mesasApi.eliminar(id)
  return { id }
}