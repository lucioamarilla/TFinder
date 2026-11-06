<script setup>
// F09/D-15: pestañas de la consola admin sobre AppShell.
const tabs = [
  { to: '/admin', label: 'Panel' },
  { to: '/admin/eventos', label: 'Eventos' },
  { to: '/admin/dlq', label: 'DLQ' },
  { to: '/admin/emails', label: 'Emails' }
]
</script>

<template>
  <AppShell>
    <nav class="admin-tabs" aria-label="Consola admin">
      <RouterLink v-for="t in tabs" :key="t.to" :to="t.to">{{ t.label }}</RouterLink>
    </nav>
    <RouterView />
  </AppShell>
</template>

<style scoped>
.admin-tabs { max-width: var(--container); margin: var(--space-md) auto 0; padding-inline: var(--gutter); display: flex; gap: var(--space-2xs); flex-wrap: wrap; }
.admin-tabs a { padding: var(--space-2xs) var(--space-md); border: var(--rule-hair) solid var(--color-rule); background: var(--color-paper); font-weight: 700; font-size: var(--text-sm); text-decoration: none; color: var(--color-ink); }
.admin-tabs a.router-link-active { background: var(--color-accent-2); color: var(--color-paper); border-color: var(--color-accent-2); }
</style>
