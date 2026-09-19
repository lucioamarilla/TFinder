<script setup>
import { ref, reactive, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useToast } from '@/composables/useToast'

const route = useRoute()
const router = useRouter()
const { login } = useAuth()
const toast = useToast()

const form = reactive({ email: '', password: '' })
const recordarme = ref(true)
const mostrarPassword = ref(false)
const enviando = ref(false)
const errorGeneral = ref('')

const emailValido = computed(() => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.trim()))

function destino() {
  const redirect = route.query.redirect
  if (typeof redirect === 'string' && redirect.startsWith('/') && !redirect.startsWith('//')) {
    return redirect
  }
  return '/dashboard'
}

function enviar() {
  errorGeneral.value = ''
  if (!form.email.trim() || !form.password) {
    errorGeneral.value = 'Completa tu correo electrónico y contraseña para abrir tu grimorio.'
    return
  }
  if (!emailValido.value) {
    errorGeneral.value = 'El correo electrónico no parece válido.'
    return
  }
  enviando.value = true
  setTimeout(() => {
    const perfil = login({ email: form.email, remember: recordarme.value })
    toast.ok(`¡Bienvenido de vuelta, ${perfil.nombre}!`)
    router.push(destino())
  }, 600)
}
</script>

<template>
  <main class="relative z-10 flex-1 flex items-center justify-center p-6 my-6">
    <div class="vellum-card w-full max-w-[480px] p-8 md:p-10 relative">
      <div class="tome-corner top-2 left-2 border-t-2 border-l-2"></div>
      <div class="tome-corner top-2 right-2 border-t-2 border-r-2"></div>
      <div class="tome-corner bottom-2 left-2 border-b-2 border-l-2"></div>
      <div class="tome-corner bottom-2 right-2 border-b-2 border-r-2"></div>

      <div class="text-center mb-7">
        <div class="flex items-center justify-center gap-2 mb-1.5 text-[#D4AF37] text-xs opacity-90">
          <span>❖</span><span>✦</span><span>❖</span>
        </div>
        <h1 class="font-mason text-[30px] font-bold text-[#8B5A2B] leading-tight tracking-wide">
          Bienvenido de vuelta
        </h1>
        <p class="font-narrative italic text-[14px] text-[#1A1A1A]/80 mt-1">
          Abre tu grimorio y continúa tu crónica en Golarion
        </p>
        <div class="relative flex items-center justify-center mt-3 mb-1">
          <div class="h-[2px] bg-[#8B5A2B] w-full"></div>
          <span class="absolute bg-[#FDF8EE] px-2 text-[#8B5A2B] text-xs">🙣 ✤ 🙡</span>
        </div>
      </div>

      <form class="space-y-5" novalidate @submit.prevent="enviar">
        <div v-if="errorGeneral" class="p-3 rounded-sm border border-[#8B1A1A]/60 bg-[#8B1A1A]/10 text-[#8B1A1A] font-narrative text-sm flex items-center gap-2" role="alert">
          <svg class="w-4 h-4 shrink-0" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" /></svg>
          <span>{{ errorGeneral }}</span>
        </div>

        <div class="space-y-1.5">
          <label for="email" class="block font-narrative text-[15px] font-semibold text-[#1A1A1A]">
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
              name="email"
              placeholder="tu@email.com"
              required
              class="auth-input w-full h-[40px] pl-8 pr-3 text-[16px] font-narrative text-[#1A1A1A] placeholder-[#8B7D6B]/70"
            />
          </div>
        </div>

        <div class="space-y-1.5">
          <div class="flex items-center justify-between">
            <label for="password" class="block font-narrative text-[15px] font-semibold text-[#1A1A1A]">
              Contraseña <span class="text-[#8B1A1A]">*</span>
            </label>
          </div>
          <div class="relative flex items-center">
            <span class="absolute left-1 text-[#8B5A2B] pointer-events-none">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>
            </span>
            <input
              v-model="form.password"
              :type="mostrarPassword ? 'text' : 'password'"
              id="password"
              name="password"
              placeholder="••••••••••••"
              required
              class="auth-input w-full h-[40px] pl-8 pr-9 text-[16px] font-narrative text-[#1A1A1A] placeholder-[#8B7D6B]/70"
            />
            <button
              type="button"
              class="absolute right-1 text-[#8B5A2B] hover:text-[#D4AF37] focus:outline-none transition-colors"
              :title="mostrarPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'"
              aria-label="Mostrar u ocultar contraseña"
              @click="mostrarPassword = !mostrarPassword"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
            </button>
          </div>
        </div>

        <div class="flex items-center pt-1">
          <label class="flex items-center gap-2.5 cursor-pointer select-none">
            <input v-model="recordarme" type="checkbox" checked class="rune-checkbox" id="remember_me">
            <span class="font-narrative text-[15px] text-[#1A1A1A] hover:text-[#8B5A2B] transition-colors">
              Recuérdame en este sagrado códice
            </span>
          </label>
        </div>

        <div class="pt-2">
          <button
            type="submit"
            :disabled="enviando"
            class="gold-btn w-full h-[48px] font-statblock font-bold text-[17px] tracking-wider uppercase rounded-[2px] flex items-center justify-center gap-2"
          >
            <span>{{ enviando ? 'Abriendo el tomo...' : 'Iniciar sesión' }}</span>
            <span class="text-[14px]">✦</span>
          </button>
        </div>

        <div class="text-center pt-2">
          <RouterLink class="font-narrative text-[14.5px] text-[#8B5A2B] hover:text-[#D4AF37] hover:underline transition-colors font-medium" to="/recuperar">
            ¿Olvidaste tu contraseña?
          </RouterLink>
        </div>

        <div class="pt-2 flex items-center justify-center gap-3">
          <div class="h-[1px] bg-[#C2A980] flex-1"></div>
          <span class="text-[#8B7D6B] text-xs font-narrative italic">o si eres un nuevo aventurero</span>
          <div class="h-[1px] bg-[#C2A980] flex-1"></div>
        </div>

        <div class="text-center">
          <p class="font-narrative text-[14px] text-[#1A1A1A]">
            ¿Aún no tienes cuenta?
            <RouterLink class="text-[#8B5A2B] font-semibold hover:text-[#D4AF37] hover:underline ml-1" to="/registro">
              Inscríbete aquí →
            </RouterLink>
          </p>
        </div>
      </form>
    </div>
  </main>
</template>