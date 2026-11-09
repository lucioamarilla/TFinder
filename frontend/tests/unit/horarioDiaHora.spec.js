// Ciclo · D-11: el horario de las mesas se compone desde los pickers día/hora
// con formato canónico ISO ("YYYY-MM-DD", "HH:MM", "YYYY-MM-DD HH:MM") y se
// guarda en el campo de texto `horario` del contrato (sin cambios de backend).
import { describe, expect, it } from 'vitest'
import { componerHorario, descomponerHorario } from '@/rules/fechas'

describe('componerHorario (D-11)', () => {
  it('día + hora devuelven el ISO canónico separado por espacio', () => {
    expect(componerHorario('2026-11-12', '21:00')).toBe('2026-11-12 21:00')
  })

  it('acepta solo día o solo hora (ambos campos son opcionales)', () => {
    expect(componerHorario('2026-11-12', '')).toBe('2026-11-12')
    expect(componerHorario('', '21:00')).toBe('21:00')
  })

  it('sin datos devuelve vacío (fallback "Horario a definir")', () => {
    expect(componerHorario('', '')).toBe('')
    expect(componerHorario(null, undefined)).toBe('')
  })

  it('descarta lo que no calza con el formato canónico', () => {
    expect(componerHorario('jueves', 'texto')).toBe('')
  })

  it('normaliza H:MM a HH:MM', () => {
    expect(componerHorario('2026-11-12', '9:30')).toBe('2026-11-12 09:30')
  })
})

describe('descomponerHorario (D-11)', () => {
  it('desarma el ISO compuesto', () => {
    expect(descomponerHorario('2026-11-12 21:00')).toEqual({ dia: '2026-11-12', hora: '21:00' })
    expect(descomponerHorario('2026-11-12')).toEqual({ dia: '2026-11-12', hora: '' })
    expect(descomponerHorario('21:00')).toEqual({ dia: '', hora: '21:00' })
  })

  it('horario heredado tipo texto aporta al menos la hora', () => {
    expect(descomponerHorario('Jueves 21:00')).toEqual({ dia: '', hora: '21:00' })
    expect(descomponerHorario('Sábados 18:00 - 22:00')).toEqual({ dia: '', hora: '18:00' })
  })

  it('texto ajeno vuelve vacío (los pickers quedan en --)', () => {
    expect(descomponerHorario('V')).toEqual({ dia: '', hora: '' })
    expect(descomponerHorario('')).toEqual({ dia: '', hora: '' })
  })

  it('ida y vuelta: descomponer(componer) restaura los pickers', () => {
    expect(descomponerHorario(componerHorario('2026-11-12', '9:30'))).toEqual({ dia: '2026-11-12', hora: '09:30' })
  })
})
