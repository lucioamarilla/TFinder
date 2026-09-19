<script setup>
import { ref, reactive, computed } from 'vue'
import { useToast } from '@/composables/useToast'

const toast = useToast()
const form = reactive({ email: '' })
const enviado = ref(false)
const enviando = ref(false)
const errorGeneral = ref('')

const emailValido = computed(() => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.trim()))

function enviar() {
  errorGeneral.value = ''
  if (!form.email.trim()) {
    errorGeneral.value = 'Indica el correo con el que forjaste tu cuenta en TFinder.'
    return
  }
  if (!emailValido.value) {
    errorGeneral.value = 'El correo electrónico no parece válido.'
    return
  }
  enviando.value = true
  setTimeout(() => {
    enviado.value = true
    enviando.value = false
    toast.ok('Mensajero enviado con éxito.')
  }, 600)
}
</script>

<template>
  <main class="flex-grow flex items-center justify-center py-10 px-4 z-10 relative">
    <div class="w-full max-w-[480px] bg-[#FDF8EE]/95 rounded-sm border border-[#C2A980] shadow-[0_8px_32px_rgba(0,0,0,0.4)] p-10 parchment-box">
      <div class="corner-top-right"></div>
      <div class="corner-bottom-left"></div>

      <div class="flex justify-center items-center gap-2 mb-2">
        <span class="text-[#8B5A2B] text-xs">❖</span>
        <span class="text-[#D4AF37] text-sm font-bold">✦</span>
        <span class="text-[#8B5A2B] text-xs">❖</span>
      </div>

      <h1 class="font-mason text-[1.8rem] text-center font-bold text-[#8B5A2B] leading-tight">
        Restablecer contraseña
      </h1>

      <p class="font-minion italic text-[1rem] text-[#1A1A1A] text-center mt-1.5 mb-5">
        Te enviaremos un enlace a tu correo
      </p>

      <div class="relative flex items-center justify-center mb-6">
        <div class="w-full h-[2px] bg-[#8B5A2B]/40"></div>
        <div class="absolute bg-[#FDF8EE] px-2 flex gap-1 items-center">
          <span class="w-1.5 h-1.5 rotate-45 border border-[#8B5A2B]"></span>
          <span class="w-2 h-2 rotate-45 bg-[#8B5A2B]"></span>
          <span class="w-1.5 h-1.5 rotate-45 border border-[#8B5A2B]"></span>
        </div>
      </div>

      <form class="space-y-6" novalidate @submit.prevent="enviar">
        <div v-if="errorGeneral" class="p-3 rounded-sm border border-[#8B1A1A]/60 bg-[#8B1A1A]/10 text-[#8B1A1A] font-minion text-sm flex items-center gap-2" role="alert">
          <svg class="w-4 h-4 shrink-0" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" /></svg>
          <span>{{ errorGeneral }}</span>
        </div>

        <div class="space-y-1.5">
          <label for="email" class="block font-minion text-[0.95rem] font-semibold text-[#1A1A1A]">
            Correo electrónico <span class="text-[#8B1A1A]">*</span>
          </label>
          <div class="relative flex items-center">
            <span class="absolute left-1 text-[#8B5A2B] pointer-events-none">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
            </span>
            <input
              v-model="form.email"
              type="email"
              id="email"
              required
              placeholder="tu@email.com"
              class="auth-input w-full h-[42px] pl-9 pr-3 bg-[#FDF8EE] border-b-2 border-[#8B7D6B] font-minion text-[1.05rem] text-[#1A1A1A] placeholder-[#8B7D6B]/70 transition-colors"
            />
          </div>
          <p class="font-minion text-[0.8rem] text-[#8B7D6B] italic">
            Introduce el correo con el que forjaste tu cuenta en TFinder.
          </p>
        </div>

        <button type="submit" :disabled="enviando" class="gold-emboss-button w-full h-[48px] rounded-sm font-tarzana font-bold text-[1rem] uppercase flex items-center justify-center gap-2 mt-4 tracking-wider disabled:opacity-60 disabled:cursor-not-allowed">
          <span>{{ enviando ? 'Enviando pergamino...' : 'Enviar enlace' }}</span>
          <span class="text-[13px]">✦</span>
        </button>
      </form>

      <div v-if="enviado" class="mt-6 p-4 rounded-sm border border-[#6B8E23] bg-[#6B8E23]/10 flex items-start gap-3 transition-all duration-300" role="status">
        <div class="text-[#6B8E23] flex-shrink-0 mt-0.5">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
        </div>
        <div>
          <h4 class="font-mason text-[0.95rem] font-bold text-[#6B8E23] uppercase tracking-wide">
            Mensajero enviado con éxito
          </h4>
          <p class="font-minion text-[1rem] text-[#6B8E23] leading-snug mt-0.5">
            Revisa tu bandeja de entrada. Si la dirección coincide con nuestros registros, recibirás un pergamino digital con instrucciones para restablecer tu llave de acceso.
          </p>
        </div>
      </div>

      <div class="mt-8 pt-4 border-t border-[#8B7D6B]/30 text-center">
        <p class="font-minion text-[0.9rem] text-[#8B7D6B]">
          ¿Recordaste tu contraseña?
          <RouterLink class="text-[#8B5A2B] hover:text-[#D4AF37] font-semibold underline underline-offset-2 ml-1 transition-colors" to="/login">
            Volver a Iniciar sesión →
          </RouterLink>
        </p>
      </div>
    </div>
  </main>
</template>