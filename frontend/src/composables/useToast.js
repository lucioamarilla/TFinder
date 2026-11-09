import { reactive } from 'vue'

// Duración por tipo (ms): err queda hasta que el usuario lo cierra.
const DURACION = { ok: 3200, info: 5000, warn: 7000, err: 0 }
const MAX_TOASTS = 3

const state = reactive({ toasts: [] })
let nextId = 0

export function useToast() {
  function push(message, type = 'info', opts = {}) {
    const t = { id: ++nextId, message, type, duration: opts.duration ?? DURACION[type] ?? 3200 }
    state.toasts.push(t)
    // Tope de pila: fuera el más viejo para que la pila no crezca sin fin.
    if (state.toasts.length > MAX_TOASTS) state.toasts.shift()
    if (t.duration > 0) {
      setTimeout(() => dismiss(t.id), t.duration)
    }
  }

  function dismiss(id) {
    const i = state.toasts.findIndex((t) => t.id === id)
    if (i >= 0) state.toasts.splice(i, 1)
  }

  return {
    toasts: state.toasts,
    ok: (m, o) => push(m, 'ok', o),
    error: (m, o) => push(m, 'err', o),
    warn: (m, o) => push(m, 'warn', o),
    info: (m, o) => push(m, 'info', o),
    dismiss
  }
}
