// Builds (builds-api).
import { useAuth } from '@/composables/useAuth'

function normalizarFicha(f) {
  if (!f || typeof f !== 'object') return f ?? null
  const ataque = f.ataque && typeof f.ataque === 'object' ? f.ataque : {}
  const dosArmas = ataque.dosArmas && typeof ataque.dosArmas === 'object' ? ataque.dosArmas : {}
  const principal = dosArmas.principal && typeof dosArmas.principal === 'object' ? dosArmas.principal : {}
  const secundaria = dosArmas.secundaria && typeof dosArmas.secundaria === 'object' ? dosArmas.secundaria : {}
  const cuerpo = ataque.cuerpo && typeof ataque.cuerpo === 'object' ? ataque.cuerpo : {}
  const distancia = ataque.distancia && typeof ataque.distancia === 'object' ? ataque.distancia : {}
  const defensa = f.defensa && typeof f.defensa === 'object' ? f.defensa : {}
  const salvaciones = Array.isArray(defensa.salvaciones) ? defensa.salvaciones : []
  const estadisticas = f.estadisticas && typeof f.estadisticas === 'object' ? f.estadisticas : {}
  const magia = f.magia && typeof f.magia === 'object' ? f.magia : {}
  return {
    ...f,
    deidad: f.deidad || 'Sin deidad asignada',
    rasgos: Array.isArray(f.rasgos) ? f.rasgos : [],
    dotes: Array.isArray(f.dotes) ? f.dotes : [],
    equipo: Array.isArray(f.equipo) ? f.equipo : [],
    habilidades: Array.isArray(f.habilidades) ? f.habilidades : [],
    magia: {
      intro: magia.intro || '',
      items: Array.isArray(magia.items) ? magia.items : [],
      ...magia,
    },
    defensa: {
      ca: defensa.ca ?? '—',
      caDetalle: defensa.caDetalle ?? '',
      pg: defensa.pg ?? '—',
      pgDetalle: defensa.pgDetalle ?? '',
      salvaciones,
      capacidades: defensa.capacidades ?? '',
      ...defensa,
    },
    ataque: {
      velocidad: ataque.velocidad ?? '—',
      cuerpo: {
        arma: cuerpo.arma ?? '',
        bonificador: cuerpo.bonificador ?? '',
        daño: cuerpo.daño ?? '',
        ...cuerpo,
      },
      dosArmas: {
        principal: {
          arma: principal.arma ?? '',
          bonificador: principal.bonificador ?? '',
          daño: principal.daño ?? '',
          ...principal,
        },
        secundaria: {
          arma: secundaria.arma ?? '',
          bonificador: secundaria.bonificador ?? '',
          daño: secundaria.daño ?? '',
          ...secundaria,
        },
      },
      distancia: {
        arma: distancia.arma ?? '',
        bonificador: distancia.bonificador ?? '',
        daño: distancia.daño ?? '',
        ...distancia,
      },
      especiales: ataque.especiales ?? '',
      ...ataque,
    },
    estadisticas: {
      bab: estadisticas.bab ?? '—',
      bmc: estadisticas.bmc ?? '—',
      dmc: estadisticas.dmc ?? '—',
      iniciativa: estadisticas.iniciativa ?? '—',
      sentidos: estadisticas.sentidos ?? '—',
      idiomas: estadisticas.idiomas ?? '—',
      ...estadisticas,
    },
    pesoCarga: f.pesoCarga ?? '',
    riquezaLiquida: f.riquezaLiquida ?? '',
    valorTotal: f.valorTotal ?? '',
    rangos: f.rangos ?? '',
    penalizadorArmadura: f.penalizadorArmadura ?? '',
    estrategia: f.estrategia ?? '',
    idBuild: f.idBuild ?? '',
    campaña: f.campaña ?? null,
  }
}

function buildApi(b) {
  return {
    id: b.id, mesaId: b.mesaId ?? b.mesa_id ?? null, tipo: b.tipo ?? 'personaje', persona: b.persona, handle: b.handle,
    autor: b.autor, categoria: b.categoria ?? 'mio', nombre: b.nombre, display: b.display,
    clase: b.clase, raza: b.raza, arquetipo: b.arquetipo, nivel: b.nivel, rol: b.rol,
    alineamiento: b.alineamiento, alineamientoColor: b.alineamientoColor,
    privacidad: b.privacidad ?? 'borrador', actualizado: b.actualizado,
    protagonista: !!b.protagonista, detalle: b.detalle, favoritos: b.favoritos ?? 0,
    ficha: normalizarFicha(b.ficha), historial: Array.isArray(b.historial) ? b.historial : [],
    autorId: b.autorId ?? null,
  }
}

export async function getBuilds(mesaId, tipo = null) {
  const { buildsApi } = await import('@/api/endpoints')
  const params = { mesa_id: mesaId }
  if (tipo) params.tipo = tipo
  const { datos } = await buildsApi.listar(params)
  return (datos ?? []).map(buildApi)
}

export async function miBuildActivo() {
  const mis = await getMisBuilds()
  return mis.find((b) => b.protagonista) || mis[0] || null
}

export async function vincularBuild(buildId, mesaId) {
  const { buildsApi } = await import('@/api/endpoints')
  const { datos: salida } = await buildsApi.vincular(buildId, mesaId)
  return { build: buildApi(salida), mesaAnterior: null }
}

export async function getMisBuilds(tipo = null) {
  const { buildsApi } = await import('@/api/endpoints')
  const { useAuth } = await import('@/composables/useAuth')
  const sub = useAuth().user.value?.sub ?? useAuth().user.value?.id
  const params = { autor_id: sub, tipo }
  const { datos } = await buildsApi.listar(params)
  return (datos ?? []).map(buildApi)
}

export async function getBuildsPublicos(tipo = null) {
  const { buildsApi } = await import('@/api/endpoints')
  const params = { tipo }
  const { datos } = await buildsApi.listar(params)
  return (datos ?? []).filter((b) => b.privacidad === 'publico').map(buildApi)
}

export async function getBuild(id) {
  const { buildsApi } = await import('@/api/endpoints')
  const { datos } = await buildsApi.detallar(id)
  return buildApi(datos)
}

export async function getHistorial(id) {
  const build = await getBuild(id)
  return (build.historial || []).map((h) => ({ ...h, snapshot: { ...(h.snapshot || {}) } }))
}

export async function crearBuild(datos) {
  const { buildsApi } = await import('@/api/endpoints')
  const { datos: salida } = await buildsApi.crear({
    tipo: datos.tipo || 'personaje',
    titulo: datos.nombre || datos.titulo || 'Personaje',
    persona: datos.persona || 'Aventurero',
    nombre: datos.nombre || 'Personaje sin nombre',
    clase: datos.clase || 'Guerrero',
    raza: datos.raza,
    arquetipo: datos.arquetipo,
    nivel: datos.nivel,
    rol: datos.rol,
    alineamiento: datos.alineamiento,
    privacidad: datos.privacidad || 'borrador',
    detalle: datos.detalle,
    ficha: datos.ficha,
  })
  return buildApi(salida)
}

export async function actualizarBuild(id, cambios) {
  const { buildsApi } = await import('@/api/endpoints')
  const { datos: salida } = await buildsApi.actualizar(id, cambios)
  return buildApi(salida)
}

export async function restaurarVersion(id, version) {
  const { buildsApi } = await import('@/api/endpoints')
  const { datos: salida } = await buildsApi.restaurar(id, version)
  return buildApi(salida)
}

export async function forkBuild(id) {
  const original = await getBuild(id)
  const datos = {
    tipo: original.tipo || 'personaje',
    nombre: `${original.nombre || original.display || 'Copia'} (copia)`,
    clase: original.clase,
    raza: original.raza,
    arquetipo: original.arquetipo,
    nivel: original.nivel,
    rol: original.rol,
    alineamiento: original.alineamiento,
    privacidad: 'borrador',
    detalle: original.detalle,
    ficha: original.ficha ? JSON.parse(JSON.stringify(original.ficha)) : null,
  }
  return await crearBuild(datos)
}

export async function exportarHistorial(id) {
  const build = await getBuild(id)
  return {
    nombre: build.nombre || build.display,
    id,
    versiones: (build.historial || []).map((h) => ({ version: h.version, fecha: h.fecha, autor: h.autor, resumen: h.resumen }))
  }
}