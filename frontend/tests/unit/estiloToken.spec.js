// Estilo global intacto (regresión del ciclo 7): el arranque no debe cargar
// las hojas pergamino ni el preflight de Tailwind; el look de la app proviene
// de tokens/base/app definido por el proyecto. La zona de gestion se expresa
// con clases del sistema de tokens (sin familias pergamino).
import { readFileSync, readdirSync } from 'node:fs'
import { join } from 'node:path'

const raiz = join(__dirname, '..', '..')

describe('sistema visual global · pergamino fuera (D-07 corregido)', () => {
  it('main.js solo importa tokens/base/app (y tailwind para utilidades)', () => {
    const fuente = readFileSync(join(raiz, 'src/main.js'), 'utf8')
    expect(fuente).toContain('@/styles/tokens.css')
    expect(fuente).toContain('@/styles/base.css')
    expect(fuente).toContain('@/styles/app.css')
    expect(fuente).not.toContain('crono.css')
    expect(fuente).not.toContain('harness.css')
  })

  it('el arranque no incluye el preflight de Tailwind (look global intacto)', () => {
    const fuente = readFileSync(join(raiz, 'src/styles/tailwind.css'), 'utf8')
    expect(fuente).not.toContain('@tailwind base')
    expect(fuente).not.toContain('@tailwind components')
    expect(fuente).toContain('@tailwind utilities')
  })

  it('la zona de gestion no usa paleta pergamino (classes arbitrarias de Tailwind)', () => {
    const gestion = join(raiz, 'src')
    const archivos = leerVueRecursivo(gestion)
    const ofensivos = archivos.filter((f) => {
      // el shell de gestion y vistas hijas: nada de bg-[#FDF8EE]/text-[#8B5A2B]
      const codigo = readFileSync(f, 'utf8')
      return /\b(bg|text)-\[#/.test(codigo)
    })
    expect(ofensivos).toEqual([])
  })
})

function leerVueRecursivo(dir) {
  let salida = []
  for (const entrar of readdirSync(dir, { withFileTypes: true })) {
    const ruta = join(dir, entrar.name)
    if (entrar.isDirectory()) salida = salida.concat(leerVueRecursivo(ruta))
    else if (entrar.name.endsWith('.vue')) salida.push(ruta)
  }
  return salida
}
