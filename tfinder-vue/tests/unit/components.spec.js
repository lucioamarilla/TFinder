import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import EmptyState from '../../src/components/EmptyState.vue'
import ErrorState from '../../src/components/ErrorState.vue'
import LoadingState from '../../src/components/LoadingState.vue'
import MesaCard from '../../src/components/MesaCard.vue'
import BaseModal from '../../src/components/modals/BaseModal.vue'

const routerStubs = {
  RouterLink: {
    props: ['to'],
    template: '<a :href="to"><slot /></a>'
  }
}

describe('componentes de estado', () => {
  it('muestra estado vacío y slot de acción', () => {
    const wrapper = mount(EmptyState, {
      global: { stubs: routerStubs },
      slots: { default: '<button>Crear mesa</button>' }
    })
    expect(wrapper.text()).toContain('Todavía no hay mesas publicadas')
    expect(wrapper.text()).toContain('Crear mesa')
  })

  it('muestra error y reintenta mediante evento', async () => {
    const wrapper = mount(ErrorState, {
      global: { stubs: routerStubs }
    })
    await wrapper.get('button').trigger('click')
    expect(wrapper.emitted('retry')).toHaveLength(1)
  })

  it('muestra mensaje de carga', () => {
    const wrapper = mount(LoadingState, {
      props: { message: 'Cargando mesas' }
    })
    expect(wrapper.text()).toContain('Cargando mesas')
    expect(wrapper.attributes('role')).toBe('status')
  })
})

describe('componentes de mesa y modal', () => {
  it('renderiza los datos de una mesa', () => {
    const wrapper = mount(MesaCard, {
      global: { stubs: routerStubs },
      props: {
        mesa: {
          id: 1,
          nombre: 'Mesa Alpha',
          sistema: 'PF1e',
          estado: 'Abierta',
          gm: 'Ana',
          lore: 'Una campaña de prueba',
          jugadores: 2,
          plazas: 4
        }
      }
    })
    expect(wrapper.text()).toContain('Mesa Alpha')
    expect(wrapper.text()).toContain('2/4 Jugadores')
    expect(wrapper.text()).toContain('Ver detalles')
  })

  it('expone el slot de BaseModal', () => {
    const wrapper = mount(BaseModal, {
      props: { open: false },
      slots: { default: '<p>Contenido</p>' }
    })
    expect(wrapper.text()).toContain('Contenido')
  })
})
