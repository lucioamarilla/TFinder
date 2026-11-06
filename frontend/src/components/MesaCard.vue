<script setup>
defineProps({ mesa: { type: Object, required: true } })
</script>

<template>
  <article class="card lomo">
    <div>
      <div class="cabecera">
        <h3 class="nombre">{{ mesa.nombre }}</h3>
        <div class="chips">
          <span class="tag tag--ink">{{ mesa.sistema }}</span>
          <span class="tag" :class="mesa.estado === 'Abierta' ? 'tag--acid' : 'tag--ember'">{{ mesa.estado }}</span>
        </div>
      </div>

      <p class="gm">
        Dirigida por <strong>{{ mesa.gm }}</strong>
      </p>

      <div class="regla"></div>

      <p class="lore">{{ mesa.lore }}</p>
    </div>

    <div class="pie">
      <span class="label plazas">
        <span aria-hidden="true">⚔</span> {{ mesa.jugadores }}/{{ mesa.plazas }} Jugadores
      </span>
      <RouterLink class="text-link" :to="`/mesas/${mesa.id}`">
        Ver detalles →
      </RouterLink>
    </div>
  </article>
</template>

<style scoped>
.lomo { padding: var(--space-md); display: flex; flex-direction: column; justify-content: space-between; border-left: var(--rule-bar) solid var(--color-accent-2); gap: var(--space-sm); }
.cabecera { display: flex; align-items: flex-start; justify-content: space-between; gap: var(--space-2xs); margin-bottom: var(--space-2xs); }
.nombre { margin: 0; font-size: var(--text-title); color: var(--color-ink); line-height: 1.1; }
.chips { display: flex; align-items: center; gap: var(--space-3xs); flex-shrink: 0; }
.gm { margin: 0 0 var(--space-2xs); font-size: var(--text-sm); color: var(--color-ink); font-style: italic; }
.gm strong { color: var(--color-accent-2); font-style: normal; }
.regla { height: 1px; background: var(--color-rule); width: 100%; margin-bottom: var(--space-2xs); }
.lore { margin: 0 0 var(--space-sm); font-size: var(--text-sm); color: var(--color-ink-2); line-height: 1.55; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
.pie { padding-top: var(--space-2xs); border-top: var(--rule-hair) solid var(--color-rule); display: flex; align-items: center; justify-content: space-between; gap: var(--space-2xs); }
.plazas { display: inline-flex; align-items: center; gap: var(--space-3xs); color: var(--color-ink-2); }
</style>
