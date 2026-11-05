import { ref } from 'vue'

const mobileOpen = ref(false)

export function useShell() {
  function toggleMenu() {
    mobileOpen.value = !mobileOpen.value
  }

  function closeMenu() {
    mobileOpen.value = false
  }

  return { mobileOpen, toggleMenu, closeMenu }
}