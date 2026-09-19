import { ref } from 'vue'
import { getMesas } from '@/services/mesas'

export function useMesas() {
  const mesas = ref([])
  const isLoading = ref(true)
  const error = ref(null)

  async function load() {
    isLoading.value = true
    error.value = null

    try {
      mesas.value = await getMesas()
    } catch (err) {
      mesas.value = []
      error.value =
        err instanceof Error ? err.message : 'Ocurrió un error inesperado.'
    } finally {
      isLoading.value = false
    }
  }

  function retry() {
    return load()
  }

  return { mesas, isLoading, error, load, retry }
}
