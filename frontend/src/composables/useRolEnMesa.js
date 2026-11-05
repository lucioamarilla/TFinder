// F2 · rol contextual por mesa (principio 2.1).
// Fuente única: GET /mesas/mias (mi_rol master|jugador).
import { ref } from 'vue'
import { getMisMesas } from '@/services/mesas'

export function useRolEnMesa() {
  const cargando = ref(false)

  async function misMesas() {
    try {
      return await getMisMesas()
    } catch {
      return []
    }
  }

  async function rolEn(mesaId) {
    cargando.value = true
    try {
      const lista = await misMesas()
      const mia = lista.find((m) => String(m.id) === String(mesaId))
      return mia ? mia.miRol : null
    } finally {
      cargando.value = false
    }
  }

  return { rolEn, misMesas, cargando }
}