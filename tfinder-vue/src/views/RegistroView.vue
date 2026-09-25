<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useToast } from '@/composables/useToast'
import { authApi } from '@/api/endpoints'

const router = useRouter()
const { login } = useAuth()
const toast = useToast()

const form = reactive({ usuario: '', email: '', password: '', confirmacion: '' })
const acepta = ref(false)
const enviando = ref(false)
const errorGeneral = ref('')

const emailValido = computed(() => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.trim()))
const passwordsCoinciden = computed(() => form.password === form.confirmacion)
const passwordLarga = computed(() => form.password.length >= 8)

function validar() {
  if (!form.usuario.trim() || !form.email.trim() || !form.password || !form.confirmacion) {
    return 'Completa todos los campos para inscribirte en las crónicas.'
  }
  if (!emailValido.value) return 'El correo electrónico no parece válido.'
  if (!passwordLarga.value) return 'La contraseña debe tener al menos 8 caracteres.'
  if (!passwordsCoinciden.value) return 'Las contraseñas no coinciden. Comprueba los caracteres ingresados.'
  if (!acepta.value) return 'Debes aceptar las normas de la comunidad TFinder para registrarte.'
  return ''
}

async function enviar() {
  errorGeneral.value = validar()
  if (errorGeneral.value) return
  enviando.value = true
  try {
    await authApi.register({
      email: form.email.trim(),
      password: form.password,
      nombre: form.usuario.trim()
    })
    const perfil = await login({ email: form.email.trim(), password: form.password })
    toast.ok(`Tu nombre ya figura en las crónicas, ${perfil.nombre}.`)
    router.push(perfil.rol === 'admin' ? '/admin/moderacion' : '/dashboard')
  } catch (e) {
    errorGeneral.value =
      e?.codigo === 400
        ? 'Ese correo ya está registrado.'
        : (e?.mensaje ?? 'No pudimos inscribirte. Intentá de nuevo.')
  } finally {
    enviando.value = false
  }
}
</script>

<template>
  <main class="relative z-10 flex-1 flex items-center justify-center p-4 sm:p-6 md:py-10">
    <div class="w-full max-w-[480px] card-parchment rounded-sm p-7 sm:p-10 relative">
      <div class="corner-flourish top-2 left-2 border-t-2 border-l-2"></div>
      <div class="corner-flourish top-2 right-2 border-t-2 border-r-2"></div>
      <div class="corner-flourish bottom-2 left-2 border-b-2 border-l-2"></div>
      <div class="corner-flourish bottom-2 right-2 border-b-2 border-r-2"></div>

      <div class="text-center mb-6">
        <div class="flex items-center justify-center gap-2 mb-1">
          <span class="text-[#8B5A2B] text-xs opacity-75">❖</span>
          <span class="text-[#D4AF37] text-sm">✦</span>
          <span class="text-[#8B5A2B] text-xs opacity-75">❖</span>
        </div>
        <h1 class="font-mason text-[1.8rem] sm:text-[2rem] font-bold text-[#8B5A2B] leading-tight tracking-wide">
          Crear cuenta
        </h1>
        <p class="font-minion italic text-[0.88rem] text-[#8B7D6B] mt-1">
          Inscribe tu nombre en las crónicas de aventureros de TFinder
        </p>
        <div class="w-full h-[2px] bg-[#8B5A2B] mt-4 relative flex items-center justify-center">
          <span class="bg-[#FDF8EE] px-2 text-[10px] text-[#8B5A2B]">⚜</span>
        </div>
      </div>

      <form class="space-y-5" novalidate @submit.prevent="enviar">
        <div v-if="errorGeneral" class="p-3 rounded-sm border border-[#8B1A1A]/60 bg-[#8B1A1A]/10 text-[#8B1A1A] font-minion text-sm flex items-center gap-2" role="alert">
          <svg class="w-4 h-4 shrink-0" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" /></svg>
          <span>{{ errorGeneral }}</span>
        </div>

        <div class="space-y-1.5">
          <label for="username" class="block font-minion text-[0.9rem] font-semibold text-[#1A1A1A]">
            Nombre de usuario <span class="text-[#8B1A1A]">*</span>
          </label>
          <div class="relative flex items-center">
            <div class="absolute left-1 text-[#8B5A2B] pointer-events-none flex items-center">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" /></svg>
            </div>
            <input
              v-model="form.usuario"
              type="text"
              id="username"
              placeholder="Ej: GuerreroLegendario"
              class="w-full h-[40px] pl-8 pr-3 grimorio-input font-minion text-[1rem] text-[#1A1A1A] placeholder-[#8B7D6B]/60"
            />
          </div>
          <p class="text-[0.75rem] font-minion italic text-[#8B7D6B]">Visible para Directores de Juego y compañeros de mesa.</p>
        </div>

        <div class="space-y-1.5">
          <label for="email" class="block font-minion text-[0.9rem] font-semibold text-[#1A1A1A]">
            Correo electrónico <span class="text-[#8B1A1A]">*</span>
          </label>
          <div class="relative flex items-center">
            <div class="absolute left-1 text-[#8B5A2B] pointer-events-none flex items-center">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75" /></svg>
            </div>
            <input
              v-model="form.email"
              type="email"
              id="email"
              placeholder="tu@email.com"
              class="w-full h-[40px] pl-8 pr-3 grimorio-input font-minion text-[1rem] text-[#1A1A1A] placeholder-[#8B7D6B]/60"
            />
          </div>
        </div>

        <div class="space-y-1.5">
          <label for="password" class="block font-minion text-[0.9rem] font-semibold text-[#1A1A1A]">
            Contraseña <span class="text-[#8B1A1A]">*</span>
          </label>
          <div class="relative flex items-center">
            <div class="absolute left-1 text-[#8B5A2B] pointer-events-none flex items-center">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" /></svg>
            </div>
            <input
              v-model="form.password"
              type="password"
              id="password"
              placeholder="Mínimo 8 caracteres"
              :class="form.password && !passwordLarga ? 'error' : ''"
              class="w-full h-[40px] pl-8 pr-10 grimorio-input font-minion text-[1rem] text-[#1A1A1A] placeholder-[#8B7D6B]/60"
            />
          </div>
          <p v-if="form.password && !passwordLarga" class="flex items-center gap-1.5 text-[#8B1A1A] font-minion text-[0.8rem] pt-1" role="alert">
            <svg class="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" /></svg>
            <span>La contraseña debe tener al menos 8 caracteres.</span>
          </p>
        </div>

        <div class="space-y-1.5">
          <label for="confirm-password" class="block font-minion text-[0.9rem] font-semibold text-[#1A1A1A]">
            Confirmar contraseña <span class="text-[#8B1A1A]">*</span>
          </label>
          <div class="relative flex items-center">
            <div class="absolute left-1 text-[#8B5A2B] pointer-events-none flex items-center">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" /></svg>
            </div>
            <input
              v-model="form.confirmacion"
              type="password"
              id="confirm-password"
              placeholder="Repite tu contraseña"
              :class="form.confirmacion && !passwordsCoinciden ? 'error' : ''"
              class="w-full h-[40px] pl-8 pr-3 grimorio-input font-minion text-[1rem] text-[#1A1A1A] placeholder-[#8B7D6B]/60"
            />
          </div>
          <div v-if="form.confirmacion && !passwordsCoinciden" class="flex items-center gap-1.5 text-[#8B1A1A] font-minion text-[0.8rem] pt-1" role="alert">
            <svg class="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" /></svg>
            <span>Las contraseñas no coinciden. Comprueba los caracteres ingresados.</span>
          </div>
        </div>

        <div class="pt-1">
          <label class="flex items-start gap-2.5 cursor-pointer select-none">
            <input v-model="acepta" type="checkbox" class="mt-1 accent-[#8B5A2B] rounded-none cursor-pointer">
            <span class="font-minion text-[0.82rem] text-[#1A1A1A]/90 leading-snug">
              Acepto las normas de la comunidad TFinder y el tratamiento de mis datos de rol bajo las licencias OGL v1.0a.
            </span>
          </label>
        </div>

        <div class="pt-3">
          <button
            type="submit"
            :disabled="enviando"
            class="w-full h-[48px] btn-gold-relief font-tarzana font-bold text-[1.1rem] tracking-wider uppercase flex items-center justify-center gap-2 rounded-sm cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed"
          >
            <span>{{ enviando ? 'Inscribiendo...' : 'Registrarse' }}</span>
            <span class="text-sm">✦</span>
          </button>
        </div>
      </form>

      <div class="mt-7 pt-4 border-t border-[#C2A980]/50 text-center">
        <RouterLink class="font-minion text-[0.9rem] text-[#8B5A2B] hover:text-[#5C3A1A] hover:underline transition-all inline-flex items-center gap-1" to="/login">
          <span>¿Ya tienes cuenta?</span>
          <strong class="font-bold underline">Inicia sesión</strong>
          <span class="text-xs">→</span>
        </RouterLink>
      </div>
    </div>
  </main>
</template>