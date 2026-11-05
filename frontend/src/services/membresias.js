// F2 · membresías (roles contextuales).
import { getMisMesas } from './mesas'

export async function getMembresias() {
  const mias = await getMisMesas()
  return mias.map((m) => ({
    ...m,
    id: m.id,
    mesaId: m.id,
    rol: m.miRol, // 'master' | 'jugador'
    ocupacion: `${m.jugadores ?? 0}/${m.plazas ?? 0} Jugadores`,
    estado: m.estado,
  }))
}