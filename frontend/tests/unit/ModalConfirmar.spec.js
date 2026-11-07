import { mount } from '@vue/test-utils'
import ModalConfirmar from '@/components/modals/ModalConfirmar.vue'

function montar(open = false) {
  return mount(ModalConfirmar, {
    props: { open, titulo: '¿Cerrar sesión?', mensaje: 'msg', etiquetaOk: 'Cerrar sesión' }
  })
}

describe('ModalConfirmar', () => {
  it('emite accept al confirmar', async () => {
    const wrapper = montar(true)
    await wrapper.find('[data-test="confirmar-salir"]').trigger('click')
    expect(wrapper.emitted('accept')).toBeTruthy()
  })

  it('emite close al cancelar', async () => {
    const wrapper = montar(true)
    await wrapper.find('[data-test="cancelar-salir"]').trigger('click')
    expect(wrapper.emitted('close')).toBeTruthy()
  })
})