<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()
</script>

<template>
  <section class="tf-placeholder">
    <div class="tf-container">
      <p class="sim-eyebrow">En portado — {{ route.name }}</p>
      <h1 class="tf-placeholder__ruta font-mason">{{ route.path }}</h1>
      <p>
        Esta pantalla del prototipo aún se está portando a Vue. El layout, los
        guards de rol y la navegación ya están activos para esta ruta.
      </p>
      <RouterLink class="btn-gold" :to="{ name: 'dashboard' }">Ir al dashboard</RouterLink>
    </div>
  </section>
</template>

<style scoped>
.tf-placeholder {
  padding: 4rem 0 6rem;
}
.tf-placeholder .tf-container {
  text-align: center;
  display: grid;
  gap: 1rem;
  justify-items: center;
}
.tf-placeholder__ruta {
  font-size: 2rem;
  color: var(--tf-ink);
  margin: 0;
}
.sim-eyebrow {
  font-family: var(--tf-labels);
  font-size: 12px;
  letter-spacing: .18em;
  text-transform: uppercase;
  color: var(--tf-copper);
  margin: 0;
}
</style>