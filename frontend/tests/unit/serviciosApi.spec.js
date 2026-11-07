import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

function jsonRes(status, body) {
  return {
    ok: status < 400,
    status,
    headers: Object.fromEntries([['content-type', 'application/json']]),
    json: async () => body,
  }
}

async function importarServicios(modo = 'api', path = '@/services') {
  vi.resetModules()
  if (modo) vi.stubEnv('VITE_API_MODE', modo)
  return await import(path)
}

describe('servicios · modo api (contrato FE↔BE P2)', () => {
  beforeEach(() => {
    localStorage.clear()
  })
  afterEach(() => {
    vi.unstubAllEnvs()
    vi.unstubAllGlobals()
  })

  it('mesas.getMesas: GET /api/v1/mesas y mapea MesaOut a pergamino', async () => {
    const f = vi.fn().mockResolvedValueOnce(
      jsonRes(200, [
        {
          id: 3,
          nombre: 'El Pérulo',
          sistema: 'pf1e',
          estado: 'abierta',
          jugadores_actuales: 2,
          jugadores_max: 4,
          gm_id: 7,
          descripcion: 'Campaña que se juega',
        },
      ]),
    )
    vi.stubGlobal('fetch', f)
    const mesas = await importarServicios('api', '@/services/mesas')
    const lista = await mesas.getMesas()
    expect(f.mock.calls[0][0]).toContain('/api/v1/mesas')
    const m = lista[0]
    expect(m.plazas).toBe(4)
    expect(m.jugadores).toBe(2)
    expect(m.vacante).toBe(true)
    expect(m.gmId).toBe(7)
  })

  it('jugadores.getSolicitudes: la bandeja del GM trae nombre y email', async () => {
    const f = vi.fn().mockResolvedValueOnce(
      jsonRes(200, [
        { id: 9, usuario_id: 41, estado: 'pendiente', nombre: 'Ana Votera', email: 'ana@tfinder.dev' },
      ]),
    )
    vi.stubGlobal('fetch', f)
    const jg = await importarServicios('api', '@/services/jugadores')
    const lista = await jg.getSolicitudes(3)
    expect(f.mock.calls[0][0]).toContain('/api/v1/mesas/3/solicitudes?estado=pendiente')
    expect(lista[0].nombre).toBe('Ana Votera')
    expect(lista[0].email).toBe('ana@tfinder.dev')
  })

  it('jugadores.aceptarSolicitud: POST .../aceptar (vertical RF-15)', async () => {
    const f = vi.fn().mockResolvedValueOnce(jsonRes(200, { id: 9, estado: 'aceptada' }))
    vi.stubGlobal('fetch', f)
    const jg = await importarServicios('api', '@/services/jugadores')
    const res = await jg.aceptarSolicitud(3, 9)
    expect(f.mock.calls[0][0]).toContain('/api/v1/mesas/3/solicitudes/9/aceptar')
    expect(res.ok).toBe(true)
  })

  it('votaciones.getVotaciones: fechas con facciones por nombre', async () => {
    const f = vi.fn().mockResolvedValueOnce(
      jsonRes(200, [
        {
          id: 12,
          propuesta: '2026-11-20T20:00:00',
          estado: 'propuesta',
          a_favor: 2,
          en_contra: 1,
          a_favor_nombres: 'Ana Votera, Beta Jugador',
          en_contra_nombres: 'Charlie Crítico',
        },
      ]),
    )
    vi.stubGlobal('fetch', f)
    const vt = await importarServicios('api', '@/services/votaciones')
    const lista = await vt.getVotaciones(3)
    expect(f.mock.calls[0][0]).toContain('/api/v1/mesas/3/fechas')
    expect(lista[0].favor).toEqual(['Ana Votera', 'Beta Jugador'])
    expect(lista[0].contra).toEqual(['Charlie Crítico'])
  })

  it('votaciones.votar: POST con valor a_favor/en_contra (RF-11)', async () => {
    const f = vi
      .fn()
      .mockResolvedValueOnce(jsonRes(200, { id: 12, valor: 'a_favor' }))
      .mockResolvedValueOnce(
        jsonRes(200, [
          { id: 12, propuesta: '2026-11-20T20:00:00', estado: 'propuesta', a_favor: 1, en_contra: 0, a_favor_nombres: 'Yo', en_contra_nombres: '' },
        ]),
      )
    vi.stubGlobal('fetch', f)
    const vt = await importarServicios('api', '@/services/votaciones')
    const res = await vt.votar(3, 12, 'favor')
    expect(f.mock.calls[0][0]).toContain('/api/v1/mesas/3/fechas/12/voto')
    expect(JSON.parse(f.mock.calls[0][1].body)).toEqual({ valor: 'a_favor' })
    expect(res.confirmada).toBe(false)
  })


  it('sesiones.getSesiones: sesiones del backend en snake→camel', async () => {
    const f = vi.fn().mockResolvedValueOnce(
      jsonRes(200, [
        { id: 5, mesa_id: 3, estado: 'abierta', fecha: '2026-11-09T20:00:00', confirmada_at: null },
      ]),
    )
    vi.stubGlobal('fetch', f)
    const sn = await importarServicios('api', '@/services/sesiones')
    const lista = await sn.getSesiones(3)
    expect(f.mock.calls[0][0]).toContain('/api/v1/mesas/3/sesiones')
    expect(lista[0].mesaId).toBe(3)
    expect(lista[0].confirmadaAt).toBeNull()
  })



})

