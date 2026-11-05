import { reactive } from 'vue'

const state = reactive({ toasts: [] })
let nextId = 0

export function useToast() {
  function push(message, type = 'info', opts = {}) {
    const t = { id: ++nextId, message, type, duration: opts.duration ?? 3200 }
    state.toasts.push(t)
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
    info: (m, o) => push(m, 'info', o),
    dismiss
  }
}