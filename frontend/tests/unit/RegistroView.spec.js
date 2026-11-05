// RED Fase 1 · Registro valida VAL-05/01/03/02 y deja sesión activa
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import RegistroView from '@/views/RegistroView.vue'
import {
  clearSession,
  currentRole,
  restaurarSemillas
} from '@/composables/useAuth'

const OTRA = { template: '<div />' }

async function montarRegistro() {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/registro', name: 'registro', component: RegistroView },
      { path: '/feed', name: 'feed', component: OTRA }
    ]
  })
  await router.push('/registro')
  const wrapper = mount(RegistroView, {
    global: { plugins: [router] },
    data: () => ({}) // views usan setup; data ignorado
  })
  return { wrapper, router }
}

async function enviar(wrapper) {
  await wrapper.find('form').trigger('submit')
  await flushPromises()
}

describe('RegistroView', () => {
  beforeEach(() => {
    localStorage.clear()
    clearSession()
    restaurarSemillas()
  })

  async function completar(wrapper, { nombre, email, pass, rolInput, aceptar = true }) {
    await wrapper.find('#usuario').setValue(nombre)
    await wrapper.find('#email').setValue(email)
    await wrapper.find('#pass').setValue(pass)
    if (rolInput !== undefined) {
      const value = rolInput === 'gm' ? 'director' : rolInput
      await wrapper.find(`input[name="rol"][value="${value}"]`).setValue()
      await wrapper.find(`input[name="rol"][value="${value}"]`).trigger('change')
    }
    if (aceptar) {
      await wrapper.find('#terminos').setValue(true)
    }
  }

  it('VAL-05/01/03 · campos vacíos muestran los mensajes de las reglas y no crean sesión', async () => {
    const { wrapper, router } = await montarRegistro()
    await enviar(wrapper)

    expect(wrapper.text()).toContain('El nombre de usuario es obligatorio')
    expect(wrapper.text()).toContain('El correo electrónico no tiene un formato válido')
    expect(wrapper.text()).toContain('La contraseña debe tener al menos 8 caracteres')
    expect(router.currentRoute.value.name).toBe('registro')
    expect(currentRole()).toBe('guest')
  })

  it('VAL-02 · correo duplicado muestra el 409 con el mensaje estandarizado', async () => {
    const { wrapper } = await montarRegistro()
    await completar(wrapper, { nombre: 'Duplicado', email: 'valeros@tfinder.dev', pass: 'contraseña8', rolInput: 'jugador' })
    await enviar(wrapper)

    expect(wrapper.text()).toContain('El correo electrónico ya está registrado')
    expect(currentRole()).toBe('guest')
  })

  it('CA-01 · registro válido crea la cuenta, inicia sesión y navega al feed', async () => {
    const { wrapper, router } = await montarRegistro()
    await completar(wrapper, { nombre: 'Aldric', email: 'aldric@tfinder.dev', pass: 'contraseña8', rolInput: 'jugador' })
    await enviar(wrapper)

    expect(router.currentRoute.value.path).toBe('/feed')
    expect(currentRole()).toBe('auth')
  })
})
