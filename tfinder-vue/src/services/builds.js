import buildsData from '@/data/builds.json'
import { getMembresias } from '@/services/membresias.js'

const LATENCIA_SIMULADA_MS = 300

const latencia = () => new Promise((resolve) => setTimeout(resolve, LATENCIA_SIMULADA_MS))

const catalogo = buildsData.builds.map((b) => ({
  ...b,
  ficha: b.ficha ? JSON.parse(JSON.stringify(b.ficha)) : null,
  historial: (b.historial || []).map((h) => ({ ...h, snapshot: { ...h.snapshot } }))
}))

let contadorNuevos = catalogo.length

function clonar(build) {
  return {
    ...build,
    ficha: build.ficha ? JSON.parse(JSON.stringify(build.ficha)) : null,
    historial: (build.historial || []).map((h) => ({ ...h, snapshot: { ...h.snapshot } }))
  }
}

export async function getBuilds(mesaId) {
  await latencia()
  return catalogo.filter((b) => b.mesaId === mesaId).map(clonar)
}

export async function miBuildActivo() {
  await latencia()
  const misMesas = await getMembresias()
  const build = catalogo.find((b) => b.persona === 'Aldren Valeros' && b.mesaId)
  return clonar(build) || {
    id: 'bld-mio',
    persona: 'Aldren Valeros',
    handle: '@aldren_write',
    nombre: 'Valeros (Guerrero Nvl 4)',
    clase: 'Guerrero',
    nivel: 4,
    detalle: 'Especialista en Espada Larga y Escudo Pesado • OGL 3.5 / PF1e Core',
    protagonista: false,
    mesaId: null
  }
}

export async function vincularBuild(buildId, mesaId) {
  await latencia()
  const build = catalogo.find((b) => b.id === buildId)
  if (!build) throw new Error(`No encontramos el build a vincular.`)
  const anterior = build.mesaId
  build.mesaId = mesaId
  return { build: clonar(build), mesaAnterior: anterior }
}

export async function getMisBuilds() {
  await latencia()
  return catalogo.filter((b) => b.categoria === 'mio').map(clonar)
}

export async function getBuildsPublicos() {
  await latencia()
  return catalogo.filter((b) => b.privacidad === 'publico').map(clonar)
}

export async function getBuild(id) {
  await latencia(450)
  const build = catalogo.find((b) => b.id === id)
  if (!build) throw new Error(`No encontramos la ficha «${id}» en la biblioteca de builds.`)
  return clonar(build)
}

export async function getHistorial(id) {
  const build = await getBuild(id)
  return (build.historial || []).map((h) => ({ ...h, snapshot: { ...h.snapshot } }))
}

export async function crearBuild(datos) {
  await latencia(450)
  contadorNuevos += 1
  const nuevo = {
    id: `bld-nuevo-${contadorNuevos}`,
    mesaId: null,
    persona: datos.persona || 'Aldren Valeros',
    handle: datos.handle || '@aldren_write',
    autor: '@aldren_valeros',
    categoria: 'mio',
    nombre: datos.nombre || 'Personaje sin nombre',
    display: datos.nombre || 'Personaje sin nombre',
    clase: datos.clase || 'Guerrero',
    raza: datos.raza || 'Humano',
    arquetipo: datos.arquetipo || '',
    nivel: datos.nivel || 1,
    rol: datos.rol || 'Personalizable',
    alineamiento: datos.alineamiento || 'N',
    alineamientoColor: 'neutral',
    privacidad: datos.privacidad || 'borrador',
    actualizado: 'BORRADOR',
    protagonista: false,
    detalle: datos.detalle || 'Progresión diseñada desde cero.',
    favoritos: 0,
    ficha: datos.ficha ? JSON.parse(JSON.stringify(datos.ficha)) : null,
    historial: [
      {
        version: '1.0',
        fecha: 'recién creado',
        autor: 'Aldren Valeros',
        resumen: 'Creación inicial del build.',
        activa: true,
        snapshot: { nivel: datos.nivel || 1, dotes: 0, piezasEquipo: 0, valorTotal: '0 po' }
      }
    ]
  }
  catalogo.unshift(nuevo)
  return clonar(nuevo)
}

export async function actualizarBuild(id, cambios) {
  await latencia(450)
  const build = catalogo.find((b) => b.id === id)
  if (!build) throw new Error(`No encontramos el build a actualizar.`)

  const versionAnterior = build.historial && build.historial.length
  const clave = Object.keys(cambios)

  const ultima = versionAnterior ? build.historial[build.historial.length - 1] : null
  const base = ultima ? ultima.version : '1.0'
  const [baseMayor, baseMenor] = base.split('.').map(Number)
  let versionMayor = baseMayor || 1
  let versionMenor = (baseMenor || 0) + 1
  if (clave.includes('nivel')) {
    versionMayor = (baseMayor || 1) + 1
    versionMenor = 1
  }

  Object.assign(build, cambios)
  build.display = build.nombre || build.display

  if (!build.historial) build.historial = []
  build.historial.forEach((h) => { h.activa = false })
  build.historial.push({
    version: `${versionMayor}.${versionMenor}`,
    fecha: 'hace un momento',
    autor: 'Aldren Valeros',
    resumen: cambios.resumenCambio || `Actualización de ${clave.join(', ')}.`,
    activa: true,
    snapshot: {
      nivel: build.nivel,
      armaPrincipal: build.ficha?.ataque?.cuerpo?.arma || '',
      pg: build.ficha?.defensa?.pg || '',
      dotes: build.ficha?.dotes?.length || 0,
      piezasEquipo: build.ficha?.equipo?.length || 0,
      valorTotal: build.ficha?.valorTotal || '0 po'
    }
  })
  return clonar(build)
}

export async function restaurarVersion(id, version) {
  await latencia()
  const build = catalogo.find((b) => b.id === id)
  if (!build) throw new Error(`No encontramos el build a restaurar.`)
  const historial = build.historial || []
  const objetivo = historial.find((h) => h.version === version)
  if (!objetivo) throw new Error(`No existe la versión «${version}» en el historial.`)
  historial.forEach((h) => { h.activa = h.version === version })
  if (objetivo.snapshot?.nivel) build.nivel = objetivo.snapshot.nivel
  build.display = build.nombre || build.display
  return clonar(build)
}

export async function exportarHistorial(id) {
  const build = await getBuild(id)
  return {
    nombre: build.nombre || build.display,
    id,
    versiones: (build.historial || []).map((h) => ({ version: h.version, fecha: h.fecha, autor: h.autor, resumen: h.resumen }))
  }
}