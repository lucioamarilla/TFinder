// Bloqueo de paleta: ningún literal de color vivirá fuera de tokens.css.
// La identidad es única (Tema Arcade): todo tono deriva de los tokens vía
// color-mix; así ninguna pantalla puede volver a inventar colores propios.
import { readFileSync, readdirSync } from 'node:fs'
import { join, relative } from 'node:path'

const raiz = join(__dirname, '..', '..')
const src = join(raiz, 'src')
const PATRON_COLOR = /#[0-9a-fA-F]{3,8}\b|oklch\(|\brgba?\(|\bhsla?\(/

describe('sistema visual · un solo lugar para los colores', () => {
  it('tokens.css es la única hoja con literales de color', () => {
    const ofensovas = leerRecursivo(src)
      .filter((f) => /\.css$|\.vue$/.test(f))
      .filter((f) => !f.includes('tokens.css'))
      .map((f) => ({ f, codigo: readFileSync(f, 'utf8') }))
      .filter(({ codigo }) => PATRON_COLOR.test(codigo))
    const rutas = ofensovas.map(({ f }) => relative(raiz, f))
    expect(rutas).toEqual([])
  })
})

function leerRecursivo(dir) {
  let salida = []
  for (const entrar of readdirSync(dir, { withFileTypes: true })) {
    const ruta = join(dir, entrar.name)
    if (entrar.isDirectory()) salida = salida.concat(leerRecursivo(ruta))
    else salida.push(ruta)
  }
  return salida
}
