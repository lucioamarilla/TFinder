<template>
  <div class="app-grid">
    <main style="display: grid; grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr); gap: var(--space-lg); align-items: start;">
      <div class="well" style="padding: var(--space-lg);">
        <p class="label" style="margin-bottom: var(--space-2xs);">Presupuesto de encuentro</p>
        <p class="figure-lg" style="font-size: 64px;">{{ apl }}</p>
        <p class="label" style="margin-bottom: var(--space-md);">APL del grupo</p>
        <div style="display: grid; gap: var(--space-xs); margin-bottom: var(--space-lg);">
          <div class="paso"><span class="n">1</span><span>Nivel medio del grupo</span><span class="num" style="margin-left: auto;">{{ nivel }}</span></div>
          <div class="paso"><span class="n">2</span><span>Jugadores</span><span class="num" style="margin-left: auto;">{{ jug }}</span></div>
          <div class="paso"><span class="n">3</span><span>Multiplicador</span><span class="num" style="margin-left: auto;">×1.0</span></div>
        </div>
        <div style="display: flex; gap: var(--space-md); flex-wrap: wrap;">
          <div class="field" style="flex: 1; min-width: 120px;">
            <label class="label" for="nivel">Nivel medio</label>
            <input class="input" id="nivel" v-model.number="nivel" type="number" min="1" max="20" />
            <p class="hint-error" v-if="!nivelValido">{{ msgNivel }}</p>
          </div>
          <div class="field" style="flex: 1; min-width: 120px;">
            <label class="label" for="jug">Jugadores</label>
            <input class="input" id="jug" v-model.number="jug" type="number" min="1" max="8" />
            <p class="hint-error" v-if="!jugValido">{{ msgJug }}</p>
          </div>
        </div>
      </div>

      <div style="display: grid; gap: var(--space-md);">
        <div class="well" style="padding: var(--space-lg);">
          <p class="label" style="margin-bottom: var(--space-2xs);">Presupuesto gastado</p>
          <div class="barra"><i :style="{ transform: 'scaleX(' + pct/100 + ')', background: barColor }"></i></div>
          <p class="label" style="margin-top: var(--space-2xs);"><span class="num">{{ gastado.toLocaleString('es-ar') }} de {{ total.toLocaleString('es-ar') }} XP</span>, {{ pct }}% del encuentro</p>
        </div>
        <div class="well" style="overflow-x: auto;">
          <table class="tf-table">
            <thead><tr><th>Dificultad</th><th>XP</th><th>CR objetivo</th></tr></thead>
            <tbody>
              <tr v-for="r in filas" :key="r.nombre">
                <td>{{ r.nombre }}</td>
                <td class="num">{{ r.xp.toLocaleString('es-ar') }}</td>
                <td class="num">{{ crObjetivo }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const nivel = ref(4)
const jug = ref(5)

// Reglas de la demo (VAL-13/14-análogo): enteros positivos, sin valores silenciosos.
const nivelValido = computed(() => Number.isInteger(nivel.value) && nivel.value >= 1 && nivel.value <= 20)
const jugValido = computed(() => Number.isInteger(jug.value) && jug.value >= 1 && jug.value <= 8)
const msgNivel = 'El nivel medio debe ser un entero entre 1 y 20'
const msgJug = 'La cantidad de jugadores debe ser un entero entre 1 y 8'

const apl = computed(() => nivelValido.value ? Math.min(20, Math.max(1, nivel.value)) : 4)
const total = computed(() => apl.value * 400 * (jugValido.value ? Math.min(8, Math.max(1, jug.value)) : 1))
const gastado = computed(() => (jugValido.value ? Math.min(8, Math.max(1, jug.value)) : 1) * Math.round(apl.value * 160))
const pct = computed(() => Math.min(100, Math.round(gastado.value / total.value * 100)))
const barColor = computed(() => pct.value < 70 ? 'var(--color-success)' : pct.value <= 100 ? 'var(--color-accent)' : 'var(--color-error)')
const crObjetivo = computed(() => Math.max(1, apl.value - (apl.value > 6 ? 2 : 1)))
const baseXp = { 'Fácil': 0.6, 'Media': 1, 'Difícil': 1.5, 'Épica': 2 }
const filas = computed(() => Object.entries(baseXp).map(([n, m]) => ({ nombre: n, xp: Math.round(total.value * m) })))
</script>

<style scoped>
.app-grid { max-width: var(--container); margin-inline: auto; padding: 112px var(--gutter) var(--space-xl); display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--space-lg); align-items: start; }
.paso { display: flex; align-items: center; gap: var(--space-md); padding-block: var(--space-2xs); border-bottom: var(--rule-hair) solid var(--color-rule); font-size: var(--text-sm); }
.paso:last-child { border-bottom: none; }
.paso .n { width: 32px; height: 32px; flex: none; display: grid; place-items: center; background: var(--color-paper-3); border: var(--rule-hair) solid var(--color-rule); border-radius: var(--radius-card); font-size: var(--text-xs); font-weight: 700; color: var(--color-muted); }
.barra { height: 10px; background: var(--color-paper-3); border-radius: var(--radius-card); overflow: hidden; }
.barra i { display: block; height: 100%; width: 100%; background: var(--color-success); transform-origin: left; transition: transform var(--dur-long) var(--ease-out); }
@media (max-width: 60rem) { .app-grid { padding-top: 120px; } }
</style>