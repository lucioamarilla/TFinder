import usuariosData from '@/data/usuarios.json'

const LATENCIA_SIMULADA_MS = 300

const latencia = () => new Promise((resolve) => setTimeout(resolve, LATENCIA_SIMULADA_MS))

const catalogo = usuariosData.usuarios.map((u) => ({
  ...u,
  stats: u.stats.map((s) => ({ ...s })),
  builds: u.builds.map((b) => ({ ...b }))
}))

function clonar(usuario) {
  return { ...usuario, stats: usuario.stats.map((s) => ({ ...s })), builds: usuario.builds.map((b) => ({ ...b })) }
}

export async function getUsuarios() {
  await latencia()
  return catalogo.map(clonar)
}

export async function getUsuario(id) {
  await latencia()
  const usuario = catalogo.find((u) => u.id === id)
  if (!usuario) throw new Error('No encontramos a ese aventurero en el registro del gremio.')
  return clonar(usuario)
}
