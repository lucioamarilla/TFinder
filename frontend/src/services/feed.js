// Feed y comunidades (feed-api).
import { useAuth } from '@/composables/useAuth'

function postApi(p) {
  return {
    id: p.id,
    comunidad: p.comunidad ? `t/${p.comunidad}` : null,
    tipo: p.tipo || 'post',
    autor: p.autor || (p.autorNombre || '').replace(/ /g, '_'),
    autorId: p.autorId ?? null,
    autorNombre: p.autorNombre || 'Aventurero',
    iniciales: p.iniciales || 'AV',
    tono: p.tono || 'oro',
    tiempo: p.tiempo || 'ahora',
    horas: p.horas ?? 0,
    etiqueta: p.etiqueta || '',
    titulo: p.titulo,
    cuerpo: p.cuerpo || '',
    votos: p.votos ?? 0,
    totalComentarios: p.totalComentarios ?? 0,
    embed: p.embed ?? null,
    comentarios: Array.isArray(p.comentarios) ? p.comentarios : [],
    miVoto: null
  }
}

export async function getFeedPosts({ orden = 'hot', autorId, comunidad, soloMesas = false } = {}) {
  const { feedApi } = await import('@/api/endpoints')
  const mapeo = { hot: 'votos', nuevo: 'recientes', top: 'votos' }
  const { datos } = await feedApi.listar({
    orden: mapeo[orden] ?? 'id',
    autor_id: autorId,
    comunidad
  })
  const lista = (datos ?? []).map(postApi)
  return soloMesas ? [] : lista
}

export async function getComunidades() {
  const { feedApi } = await import('@/api/endpoints')
  const { datos } = await feedApi.comunidades()
  return (datos ?? []).map((c) => ({ id: `t/${c.comunidad}`, nombre: c.comunidad, cantidad: c.cantidad }))
}

export async function getPost(postId) {
  const { feedApi } = await import('@/api/endpoints')
  const { datos } = await feedApi.listar({})
  const encontrada = (datos ?? []).find((p) => String(p.id) === String(postId))
  if (!encontrada) throw new Error('La publicación se perdió entre los pergaminos.')
  return postApi(encontrada)
}

export async function votarPost(postId, direccion) {
  const { feedApi } = await import('@/api/endpoints')
  const { datos } = await feedApi.like(postId)
  return { id: postId, votos: datos.votos, miVoto: datos.megusta ? 'up' : null }
}

export async function toggleGuardarPost(postId) {
  return getPost(postId)
}

export async function crearPost({ titulo, cuerpo, etiqueta = 'Debate Táctico', tipo = 'post', embed = null, comunidad, autor = {} }) {
  const { feedApi } = await import('@/api/endpoints')
  const { datos } = await feedApi.crear({
    titulo: (titulo || '').trim(),
    cuerpo: (cuerpo || '').trim(),
    etiqueta,
    tipo,
    embed,
    comunidad: comunidad ? String(comunidad).replace(/^t\//, '') : undefined,
    autorNombre: autor.nombre || autor.nombre
  })
  return postApi(datos)
}