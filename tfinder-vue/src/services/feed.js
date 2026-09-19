import feedData from '@/data/feed.json'

const LATENCIA_SIMULADA_MS = 280

const latencia = (ms = LATENCIA_SIMULADA_MS) => new Promise((resolve) => setTimeout(resolve, ms))

const catalogo = feedData.posts.map((p) => ({
  ...p,
  miVoto: null,
  guardado: false,
  embed: p.embed ? { ...p.embed } : null,
  comentarios: clonarComentarios(p.comentarios)
}))

function clonarComentarios(lista = []) {
  return lista.map((c) => ({
    ...c,
    respuestas: clonarComentarios(c.respuestas)
  }))
}

function clonar(post) {
  return { ...post, embed: post.embed ? { ...post.embed } : null, comentarios: clonarComentarios(post.comentarios) }
}

function puntaje(post) {
  return post.votos * 1.4 - post.horas * 3
}

export async function getFeedPosts({ orden = 'hot', autorId } = {}) {
  await latencia()
  let lista = autorId ? catalogo.filter((p) => p.autorId === autorId) : catalogo
  lista = [...lista]
  if (orden === 'nuevo') lista.sort((a, b) => a.horas - b.horas)
  else if (orden === 'top') lista.sort((a, b) => b.votos - a.votos)
  else lista.sort((a, b) => puntaje(b) - puntaje(a))
  return lista.map(clonar)
}

export async function getPost(postId) {
  await latencia()
  const post = catalogo.find((p) => p.id === postId)
  if (!post) throw new Error('La publicación se perdió entre los pergaminos.')
  return clonar(post)
}

export async function votarPost(postId, direccion) {
  await latencia(180)
  const post = catalogo.find((p) => p.id === postId)
  if (!post) throw new Error('No encontramos la publicación a votar.')
  const delta = { up: 1, down: -1 }[direccion] || 0
  if (post.miVoto === direccion) {
    post.votos -= delta
    post.miVoto = null
    return clonar(post)
  }
  if (post.miVoto) post.votos -= { up: 1, down: -1 }[post.miVoto]
  post.votos += delta
  post.miVoto = direccion
  return clonar(post)
}

export async function toggleGuardarPost(postId) {
  await latencia(180)
  const post = catalogo.find((p) => p.id === postId)
  if (!post) throw new Error('No encontramos la publicación a guardar.')
  post.guardado = !post.guardado
  return clonar(post)
}

export async function crearPost({ titulo, cuerpo, etiqueta = 'Debate Táctico', tipo = 'post', embed = null, autor = {} }) {
  await latencia(450)
  const post = {
    id: `post-${Date.now()}`,
    tipo,
    autor: autor.handle || 'Valeros_ElTemerario',
    autorId: autor.id || 'aldren',
    autorNombre: autor.nombre || 'Valeros el Temerario',
    iniciales: autor.iniciales || 'AV',
    tono: autor.tono || 'oro',
    tiempo: 'hace unos segundos',
    horas: 0,
    etiqueta,
    titulo: titulo.trim(),
    cuerpo: (cuerpo || '').trim(),
    votos: 0,
    totalComentarios: 0,
    embed: embed ? { ...embed } : null,
    comentarios: []
  }
  catalogo.unshift(post)
  return clonar(post)
}
