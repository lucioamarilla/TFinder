// RED Fase 3 · Reglas de wiki (RN-05, VAL-25/26/28) y de sesión/diario (VAL-33, iniciativa)
import { validarPaginaWiki, puedeVerPaginaRegla, TIPOS_PAGINA, VISIBILIDADES } from '@/rules/wiki'
import { validarDiario, validarCombatiente, siguienteTurno } from '@/rules/sesiones'

describe('valiarPaginaWiki (VAL-25/26 + visibilidad)', () => {
  it('códigos de tipo cerrados a los cinco del doc: NPC, Lugar, Criatura, Nota, Sesión', () => {
    expect(TIPOS_PAGINA).toEqual(['NPC', 'Lugar', 'Criatura', 'Nota', 'Sesión'])
  })

  it('visibilidades cerradas a las tres de RN-05', () => {
    expect(VISIBILIDADES).toEqual(['privada', 'jugadores', 'publica'])
  })

  it('VAL-25 · título obligatorio', () => {
    expect(validarPaginaWiki({ titulo: '  ', tipo: 'NPC', visibilidad: 'publica' }))
      .toContainEqual(expect.objectContaining({ mensaje: 'El título de la página es obligatorio' }))
  })

  it('VAL-26 · tipo fuera de los permitidos → error listando los valores', () => {
    const errores = validarPaginaWiki({ titulo: 'X', tipo: 'SESION', visibilidad: 'publica' })
    expect(errores.some((e) => e.mensaje.includes('NPC') && e.mensaje.includes('Sesión'))).toBe(true)
  })

  it('visibilidad inválida se rechaza', () => {
    const errores = validarPaginaWiki({ titulo: 'X', tipo: 'NPC', visibilidad: 'todos' })
    expect(errores.some((e) => e.mensaje.includes('privada') && e.mensaje.includes('publica'))).toBe(true)
  })

  it('una página válida no tiene errores', () => {
    expect(validarPaginaWiki({ titulo: 'Zorro Glacial', tipo: 'Criatura', visibilidad: 'publica' })).toEqual([])
  })
})

describe('puedeVerPaginaRegla (RN-05 / CA-19/20)', () => {
  it('un invitado ve páginas públicas', () => {
    expect(puedeVerPaginaRegla({ visibilidad: 'publica' }, { esGM: false, esMiembro: false, conSesion: false })).toEqual({ ok: true })
  })

  it('CA-20 · un invitado no ve páginas de jugadores ni privadas (403 con el mensaje del backend)', () => {
    for (const visibilidad of ['jugadores', 'privada']) {
      expect(puedeVerPaginaRegla({ visibilidad }, { esGM: false, esMiembro: false, conSesion: false }))
        .toEqual({ ok: false, codigo: '403', mensaje: 'No tienes permisos para ver esta página' })
    }
  })

  it('CA-19 · un miembro ve una página de visibilidad "jugadores"', () => {
    expect(puedeVerPaginaRegla({ visibilidad: 'jugadores' }, { esGM: false, esMiembro: true, conSesion: true })).toEqual({ ok: true })
  })

  it('un miembro no ve una página privada (solo GM)', () => {
    expect(puedeVerPaginaRegla({ visibilidad: 'privada' }, { esGM: false, esMiembro: true, conSesion: true }))
      .toEqual({ ok: false, codigo: '403', mensaje: 'No tienes permisos para ver esta página' })
  })

  it('el GM ve todo (incluso lo privado)', () => {
    for (const visibilidad of ['privada', 'jugadores', 'publica']) {
      expect(puedeVerPaginaRegla({ visibilidad }, { esGM: true, esMiembro: false, conSesion: true })).toEqual({ ok: true })
    }
  })
})

describe('sesiones y diario', () => {
  it('VAL-33 · el resumen del diario es obligatorio', () => {
    expect(validarDiario('   ')).toBe('El resumen del diario es obligatorio')
    expect(validarDiario('Sesión 4: el corredor colapsa')).toBe(null)
  })

  it('el combatiente necesita nombre y iniciativa entera entre 1 y 20', () => {
    expect(validarCombatiente({ nombre: '', init: 12, pv: 6, pvMax: 6 })[0].mensaje).toBe('El nombre del combatiente es obligatorio')
    expect(validarCombatiente({ nombre: 'Zorro', init: 0, pv: 6, pvMax: 6 }).some((e) => e.mensaje.includes('iniciativa'))).toBe(true)
    expect(validarCombatiente({ nombre: 'Zorro', init: 21, pv: 6, pvMax: 6 }).some((e) => e.mensaje.includes('iniciativa'))).toBe(true)
    expect(validarCombatiente({ nombre: 'Zorro', init: 12.5, pv: 6, pvMax: 6 }).some((e) => e.mensaje.includes('iniciativa'))).toBe(true)
    expect(validarCombatiente({ nombre: 'Zorro', init: 12, pv: 6, pvMax: 6 })).toEqual([])
  })

  it('siguienteTurno no se rompe sin combatientes y envuelve al final', () => {
    expect(siguienteTurno(0, 0)).toBe(0)
    expect(siguienteTurno(3, 4)).toBe(0)
    expect(siguienteTurno(1, 4)).toBe(2)
  })
})
