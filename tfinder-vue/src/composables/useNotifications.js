import { ref } from 'vue'
import { getNotificaciones } from '@/services/notificaciones'

const unreadCount = ref(0)

export function useNotifications() {
  async function loadCount() {
    try {
      const list = await getNotificaciones()
      unreadCount.value = list.filter((n) => !n.leida).length
    } catch {
      unreadCount.value = 0
    }
  }

  function setUnread(value) {
    unreadCount.value = value
  }

  return { unreadCount, loadCount, setUnread }
}