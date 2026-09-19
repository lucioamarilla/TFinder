<script setup>
import { ref } from 'vue'
import { useToast } from '@/composables/useToast.js'

const toast = useToast()

const tags = ref([
  { nombre: 'DPS', usos: 24, verde: false },
  { nombre: 'Soporte', usos: 17, verde: false },
  { nombre: 'Tanque', usos: 11, verde: false },
  { nombre: 'Evocación', usos: 9, verde: false },
  { nombre: 'Hechicería', usos: 14, verde: false },
  { nombre: 'PF1e', usos: 46, verde: true }
])

const nuevoTag = ref('')

function crearTag() {
  const nombre = nuevoTag.value.trim().replace(/^#/, '')
  if (!nombre) {
    toast.error('Escribí un nombre para el tag.')
    return
  }
  if (tags.value.some((t) => t.nombre.toLowerCase() === nombre.toLowerCase())) {
    toast.info(`El tag «${nombre}» ya existe.`)
    return
  }
  tags.value.push({ nombre, usos: 0, verde: false })
  nuevoTag.value = ''
  toast.ok(`Tag «${nombre}» creado y disponible.`)
}

function aplicar(tag) {
  const aplicados = aplicadosSet.value
  if (aplicados.has(tag.nombre)) {
    aplicados.delete(tag.nombre)
    toast.info(`Tag «${tag.nombre}» retirado del build.`)
  } else {
    aplicados.add(tag.nombre)
    toast.ok(`Build etiquetada como «${tag.nombre}».`)
  }
}

const aplicadosSet = ref(new Set())
</script>

<template>
  <main class="tfinder-shell">
    <h1 class="font-mason text-3xl text-[#8B5A2B] font-bold mb-2">✦ Gestor de Tags</h1>
    <p class="font-minion italic text-[#5C4633] mb-6">Etiquetá builds y publicaciones del feed para que el cónclave encuentre lo que busca.</p>

    <section class="parchment-sheet relative border border-[#C2A980] rounded-sm p-6 mb-5 shadow-md">
      <div class="absolute top-0 left-0 w-3 h-3 border-t-2 border-l-2 border-[#8B5A2B]"></div>
      <div class="absolute bottom-0 right-0 w-3 h-3 border-b-2 border-r-2 border-[#8B5A2B]"></div>
      <h2 class="font-tarzana text-xs uppercase tracking-widest text-[#D4AF37] mb-3">Tags existentes</h2>
      <div class="flex flex-wrap gap-2">
        <span
          v-for="t in tags"
          :key="t.nombre"
          class="font-tarzana text-xs px-3 py-1 rounded-full border"
          :class="t.verde ? 'bg-[#6B8E23]/12 text-[#6B8E23] border-[#6B8E23]/25' : 'bg-[#8B5A2B]/12 text-[#8B5A2B] border-[#8B5A2B]/25'"
        >{{ t.nombre }} · {{ t.usos }}</span>
      </div>
    </section>

    <section class="parchment-sheet relative border border-[#C2A980] rounded-sm p-6 mb-5 shadow-md">
      <div class="absolute top-0 left-0 w-3 h-3 border-t-2 border-l-2 border-[#8B5A2B]"></div>
      <div class="absolute bottom-0 right-0 w-3 h-3 border-b-2 border-r-2 border-[#8B5A2B]"></div>
      <h2 class="font-tarzana text-xs uppercase tracking-widest text-[#D4AF37] mb-3">Crear tag</h2>
      <form class="flex gap-2 flex-wrap" @submit.prevent="crearTag">
        <input v-model="nuevoTag" type="text" placeholder="ej. Cazarrecompensas" class="flex-1 min-w-[180px] py-2 px-3 rounded-sm bg-[#F4EAD6] border border-[#C2A980] font-minion text-sm" />
        <button type="submit" class="px-5 py-2 bg-[#D4AF37] text-[#1A1A1A] font-tarzana text-xs font-bold rounded-sm hover:brightness-110">Crear tag</button>
      </form>
    </section>

    <section class="parchment-sheet relative border border-[#C2A980] rounded-sm p-6 shadow-md">
      <div class="absolute top-0 left-0 w-3 h-3 border-t-2 border-l-2 border-[#8B5A2B]"></div>
      <div class="absolute bottom-0 right-0 w-3 h-3 border-b-2 border-r-2 border-[#8B5A2B]"></div>
      <h2 class="font-tarzana text-xs uppercase tracking-widest text-[#D4AF37] mb-3">Aplicar a build</h2>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="t in tags.slice(0, 5)"
          :key="t.nombre"
          type="button"
          class="px-4 py-2 border font-tarzana text-xs font-bold rounded-sm"
          :class="aplicadosSet.has(t.nombre) ? 'bg-[#8B5A2B] text-[#FDF8EE] border-[#8B5A2B]' : 'border-[#8B5A2B] text-[#8B5A2B]'"
          @click="aplicar(t)"
        >
          {{ aplicadosSet.has(t.nombre) ? '✓ ' : '+ ' }}{{ t.nombre }}
        </button>
      </div>
      <p class="font-tarzana text-xs text-[#8B7D6B] italic mt-3">{{ aplicadosSet.size }} tags aplicados a este build.</p>
    </section>
  </main>
</template>