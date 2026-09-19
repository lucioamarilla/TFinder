<script setup>
import { useAuth } from '@/composables/useAuth'

const { role } = useAuth()
const home = role.value === 'admin' ? '/admin/moderacion' : role.value === 'auth' ? '/dashboard' : '/'
</script>

<template>
  <section class="tf-404">
    <div class="tf-container tf-404__box">
      <p class="font-tarzana tf-404__eyebrow">Error · 404</p>
      <h1 class="font-mason tf-404__title">Este tomo se perdió en la pila de grimorios</h1>
      <p class="tf-404__text">
        La ruta que buscás no existe en el Codex de la plataforma. Quizás fue
        renombrada, o jamás fue escrita. Volvé a tierras conocidas.
      </p>
      <div class="tf-404__actions">
        <RouterLink class="btn-gold" :to="home">Ir al inicio</RouterLink>
        <RouterLink class="btn-copper-outline" to="/mesas">Explorar mesas</RouterLink>
      </div>
    </div>
  </section>
</template>

<style scoped>
.tf-404 {
  padding: 5rem 0 7rem;
}
.tf-404__box {
  text-align: center;
  display: grid;
  gap: 1rem;
  justify-items: center;
  max-width: 620px;
}
.tf-404__eyebrow {
  font-size: 13px;
  letter-spacing: .24em;
  text-transform: uppercase;
  color: var(--tf-garnet);
  margin: 0;
}
.tf-404__title {
  font-size: 2.4rem;
  line-height: 1.1;
  color: var(--tf-ink);
  margin: 0;
}
.tf-404__text {
  margin: 0;
}
.tf-404__actions {
  display: flex;
  flex-wrap: wrap;
  gap: .75rem;
  justify-content: center;
  margin-top: .5rem;
}
.tf-404__actions .btn-gold,
.tf-404__actions .btn-copper-outline {
  padding: 12px 20px;
  text-decoration: none;
}
</style>