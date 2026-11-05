// F5 · uploads (imágenes de perfil y adjuntos del foro).
import { apiUrl } from '@/config/api'
import { currentAccessToken } from '@/composables/useAuth'

export async function subirImagen(archivo) {
  const fd = new FormData()
  fd.append('upload', archivo)
  const r = await fetch(apiUrl('feed', '/api/v1/uploads'), {
    method: 'POST',
    headers: currentAccessToken() ? { Authorization: `Bearer ${currentAccessToken()}` } : {},
    body: fd,
  })
  if (!r.ok) {
    const e = await r.json().catch(() => ({}))
    throw new Error(e?.error?.mensaje || 'No se pudo subir la imagen.')
  }
  const datos = await r.json()
  return { id: datos.id, url: datos.url, mime: datos.mime, tamano: datos.tamano }
}

export async function obtenerImagenUrl(id) {
  return apiUrl('feed', `/api/v1/uploads/${id}`)
}