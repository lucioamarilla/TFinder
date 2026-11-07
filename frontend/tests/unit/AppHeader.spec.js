// RED Fase 1 · El header reacciona a la sesión (bug reportado por el usuario)
import { mount } from '@vue/test-utils'
import { RouterLinkStub } from '@vue/test-utils'
import AppHeader from '@/components/AppHeader.vue'
import {
  login,
  logout,
  clearSession,
  currentRole,
  restaurarSemillas
} from '@/composables/useAuth'

const PLANTILLA = { template: '<div />' }

function montarHeader() {
  return mount(AppHeader, {
    global: {
      stubs: { RouterLink: RouterLinkStub }
    }
  })
}

describe('AppHeader según sesión', () => {
  beforeEach(() => {
    localStorage.clear()
    clearSession()
    restaurarSemillas()
  })

  it('un invitado ve Iniciar sesión y Crear cuenta, y NO ve avatar', () => {
    expect(currentRole()).toBe('guest')
    const wrapper = montarHeader()
    expect(wrapper.text()).toContain('Iniciar sesión')
    expect(wrapper.text()).toContain('Crear cuenta')
    expect(wrapper.find('.nav-avatar').exists()).toBe(false)
    expect(wrapper.find('[data-test="cerrar-sesion"]').exists()).toBe(false)
  })

  it('un usuario autenticado ve su avatar con iniciales y ya NO el acceso de iniciar sesión', async () => {
    await login({ email: 'valeros@tfinder.dev', password: 'tfinder1234' })
    const wrapper = montarHeader()
    expect(wrapper.find('.nav-avatar').exists()).toBe(true)
    expect(wrapper.text()).not.toContain('Iniciar sesión')
    expect(wrapper.find('[data-test="cerrar-sesion"]').exists()).toBe(true)
  })

  it('al cerrar sesión desde el menú, el header vuelve al estado invitado', async () => {
    await login({ email: 'valeros@tfinder.dev', password: 'tfinder1234' })
    const wrapper = montarHeader()

    const botonCerrar = wrapper.find('[data-test="cerrar-sesion"]')
    expect(botonCerrar.exists()).toBe(true)
    await botonCerrar.trigger('click')

    // El modal de confirmación se abre antes de cerrar sesión.
    const modal = wrapper.find('[data-test="modal-cerrar-sesion"]')
    expect(modal.exists()).toBe(true)

    // Cancelar mantiene la sesión.
    await wrapper.find('[data-test="cancelar-salir"]').trigger('click')
    expect(currentRole()).not.toBe('guest')

    // Volver a abrir y confirmar cierra la sesión.
    await wrapper.find('[data-test="cerrar-sesion"]').trigger('click')
    await wrapper.find('[data-test="confirmar-salir"]').trigger('click')

    expect(currentRole()).toBe('guest')
    expect(wrapper.text()).toContain('Iniciar sesión')
    expect(wrapper.find('.nav-avatar').exists()).toBe(false)
  })
})