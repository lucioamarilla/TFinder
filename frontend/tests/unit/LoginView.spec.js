// RED Fase 1 · Login valida reglas VAL-01/03, muestra error del backend y navega con sesión
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import LoginView from '@/views/LoginView.vue'
import {
  clearSession,
  currentRole,
  restaurarSemillas,
  login
} from '@/composables/useAuth'

const OTRA = { template: '<div />' }

async function montarLogin() {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/login', name: 'login', component: LoginView },
      { path: '/registro', name: 'registro', component: OTRA },
      { path: '/recuperar', name: 'recuperar', component: OTRA },
      { path: '/feed', name: 'feed', component: OTRA }
    ]
  })
  await router.push('/login')
  const wrapper = mount(LoginView, { global: { plugins: [router] } })
  return { wrapper, router }
}

async function enviar(wrapper) {
  await wrapper.find('form').trigger('submit')
  await flushPromises()
}

describe('LoginView', () => {
  beforeEach(() => {
    localStorage.clear()
    clearSession()
    restaurarSemillas()
  })

  it('VAL-03 · contraseña corta muestra el mensaje de la regla y no navega', async () => {
    const { wrapper, router } = await montarLogin()
    await wrapper.find('#email').setValue('valeros@tfinder.dev')
    await wrapper.find('#pass').setValue('corta')
    await enviar(wrapper)

    expect(wrapper.text()).toContain('La contraseña debe tener al menos 8 caracteres')
    expect(router.currentRoute.value.name).toBe('login')
    expect(currentRole()).toBe('guest')
  })

  it('CA-05 · credenciales inválidas muestran el mensaje estandarizado y no navegan', async () => {
    const { wrapper, router } = await montarLogin()
    await wrapper.find('#email').setValue('valeros@tfinder.dev')
    await wrapper.find('#pass').setValue('incorrecta1')
    await enviar(wrapper)

    expect(wrapper.text()).toContain('Credenciales inválidas')
    expect(router.currentRoute.value.name).toBe('login')
  })

  it('CA-04 · login válido crea sesión y navega a mesas', async () => {
    const { wrapper, router } = await montarLogin()
    await wrapper.find('#email').setValue('valeros@tfinder.dev')
    await wrapper.find('#pass').setValue('tfinder1234')
    await enviar(wrapper)

    expect(router.currentRoute.value.path).toBe('/mesas')
    expect(currentRole()).toBe('auth')
  })

  it('un usuario ya autenticado que visita /login es reenviado a /mesas (guard)', async () => {
    const { resolveGuard } = await import('@/router/guard')
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/login', name: 'login', component: LoginView, meta: { roles: ['guest'] } },
        { path: '/mesas', name: 'mesas', component: OTRA },
        { path: '/proximamente/:feature', name: 'proximamente', component: OTRA, props: true }
      ]
    })
    router.beforeEach((to) => resolveGuard(to, currentRole()))
    await login({ email: 'valeros@tfinder.dev', password: 'tfinder1234' })
    await router.push('/login')
    mount(LoginView, { global: { plugins: [router] } })
    expect(router.currentRoute.value.path).toBe('/mesas')
  })
})
