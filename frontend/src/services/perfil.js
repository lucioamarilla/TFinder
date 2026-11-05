// F5 · perfil real (nombre, avatar, bio).
import { perfilApi } from '@/api/endpoints'
import { useAuth } from '@/composables/useAuth'

export async function verPerfil() {
  const { datos } = await perfilApi.ver()
  return {
    email: datos.email,
    nombre: datos.nombre,
    bio: datos.bio || '',
    avatarUrl: datos.avatarUrl || null,
    rol: datos.rol,
  }
}

export async function editarPerfil({ nombre, bio, avatarUrl } = {}) {
  const { datos } = await perfilApi.editar({
    nombre,
    bio,
    avatarUrl: avatarUrl || undefined,
  })
  return {
    email: datos.email,
    nombre: datos.nombre,
    bio: datos.bio || '',
    avatarUrl: datos.avatarUrl || null,
    rol: datos.rol,
  }
}