<script setup>
</script>

<template>
  <footer class="colophon">
    <div class="wrap cols">
      <div>
        <p style="display:flex;align-items:center;gap:var(--space-2xs);margin:0 0 var(--space-2xs);">
          <img src="/assets/logo-tfinder.png" alt="Logo de TFinder" width="46" height="46" style="width:46px;height:46px;object-fit:contain;" />
          <span class="display" style="font-size:var(--text-md);color:var(--color-accent-2);">TFinder</span>
        </p>
        <p class="label">Encontrá tu mesa y tirá iniciativa</p>
      </div>
      <div>
        <p class="label" style="margin-bottom: var(--space-2xs);">Explorá</p>
        <p style="font-size: var(--text-sm);">
          <RouterLink class="text-link" to="/mesas">Mesas</RouterLink>          
        </p>
      </div>
      <div>
        <p class="label" style="margin-bottom: var(--space-2xs);">Sistema</p>
        <p style="font-size: var(--text-sm); color: var(--color-muted);">
          Tema Arcade, OGL 1.0a de Paizo Inc.
        </p>
      </div>
    </div>
  </footer>
</template>