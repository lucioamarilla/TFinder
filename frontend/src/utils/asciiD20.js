// Registra el custom element <ascii-d20> y el cableado del hero de la landing.
// Portado desde 01_landing_arcade.html

export function registerAsciiD20() {
  if (customElements.get('ascii-d20')) return
  // (clase completa portada)
  class AsciiD20 extends HTMLElement {
    static observedAttributes = ['fg', 'bg', 'accent', 'result', 'cols', 'scroll-height', 'progress']
    constructor() {
      super()
      const r = this.attachShadow({ mode: 'open' })
      r.innerHTML = `<style>:host { display:block; height:400vh; position:relative; } .stage { position:sticky; top:-57px; height:100vh; height:100dvh; overflow:hidden; } canvas { width:100%; height:100%; display:block; }</style><div class="stage"><canvas></canvas></div>`
      this.cv = r.querySelector('canvas')
      this.ctx = this.cv.getContext('2d')
      this.cur = 0; this.target = 0; this.dirty = true
      const t = (1 + Math.sqrt(5)) / 2
      this.V = [[-1,t,0],[1,t,0],[-1,-t,0],[1,-t,0],[0,-1,t],[0,1,t],[0,-1,-t],[0,1,-t],[t,0,-1],[t,0,1],[-t,0,-1],[-t,0,1]].map(v => { const l = Math.hypot(...v); return v.map(c => c / l) })
      this.F = [[0,11,5],[0,5,1],[0,1,7],[0,7,10],[0,10,11],[1,5,9],[5,11,4],[11,10,2],[10,7,6],[7,1,8],[3,9,4],[3,4,2],[3,2,6],[3,6,8],[3,8,9],[4,9,5],[2,4,11],[6,2,10],[8,6,7],[9,8,1]]
      this.N = this.F.map(f => { const c = [0,1,2].map(k => (this.V[f[0]][k]+this.V[f[1]][k]+this.V[f[2]][k])/3); const l = Math.hypot(...c); return c.map(x => x/l) })
      this.B = [0,8,2,10,12,4,14,6,3,11,1,9,15,7,13,5]
      const cr = (a,b) => [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]
      this.CEN = []; this.UP = []; this.RT = []
      this.F.forEach((f,i) => {
        const c = [0,1,2].map(k => (this.V[f[0]][k]+this.V[f[1]][k]+this.V[f[2]][k])/3)
        const u = this.V[f[0]].map((x,k) => x - c[k]), l = Math.hypot(...u), up = u.map(x => x/l)
        this.CEN.push(c); this.UP.push(up); this.RT.push(cr(up, this.N[i]))
      })
      this.masks = [null]
      const mc = document.createElement('canvas'); mc.width = 96; mc.height = 64
      const mx = mc.getContext('2d', { willReadFrequently: true })
      for (let n = 1; n <= 20; n++) {
        mx.clearRect(0,0,96,64); mx.fillStyle = '#fff'
        mx.font = 'bold 60px ui-monospace, Menlo, Consolas, monospace'; mx.textAlign = 'center'; mx.textBaseline = 'middle'
        mx.fillText(String(n), 48, 34)
        const dd = mx.getImageData(0,0,96,64).data, m = new Uint8Array(96*64)
        for (let i = 0; i < m.length; i++) m[i] = dd[i*4+3]
        this.masks.push(m)
      }
      this.onScroll = () => { this.target = this.pinned ? (parseFloat(this.getAttribute('progress')) || 0) : this.progress() }
      this.onResize = () => { this.resize(); this.onScroll() }
    }
    get pinned() { return this.hasAttribute('pinned') }
    connectedCallback() {
      if (!this.hasAttribute('result') || this.getAttribute('result') === 'random') this.pickResult(Math.ceil(Math.random()*20))
      else this.pickResult(+this.getAttribute('result'))
      this.applyHeight(); this.readColors(); this.resize(); this.onScroll()
      if (matchMedia('(prefers-reduced-motion: reduce)').matches) { this.cur = this.target = 1 }
      else this.cur = this.target
      addEventListener('scroll', this.onScroll, { passive: true })
      addEventListener('resize', this.onResize)
      const loop = () => {
        const d = this.target - this.cur
        if (Math.abs(d) > 0.0002) { this.cur += d * 0.14; this.dirty = true }
        if (this.dirty) { this.draw(this.cur); this.dirty = false }
        this.raf = requestAnimationFrame(loop)
      }
      loop()
    }
    disconnectedCallback() { cancelAnimationFrame(this.raf); removeEventListener('scroll', this.onScroll); removeEventListener('resize', this.onResize) }
    attributeChangedCallback(n, _, v) {
      if (!this.isConnected) return
      if (n === 'result') this.pickResult(+v)
      if (n === 'scroll-height') this.applyHeight()
      if (n === 'cols') this.resize()
      if (n === 'progress' && this.pinned) this.target = parseFloat(v) || 0
      this.readColors(); this.dirty = true
    }
    get result() { return this.value }
    set result(v) { this.setAttribute('result', v) }
    pickResult(n) {
      this.value = Math.min(20, Math.max(1, Math.round(n) || 20))
      const n0 = this.N[this.value-1], c = n0[2]
      const a = [n0[1], -n0[0], 0], s = Math.hypot(a[0], a[1])
      if (s < 1e-6) { this.Rf = c > 0 ? [1,0,0,0,1,0,0,0,1] : [1,0,0,0,-1,0,0,0,-1] }
      else {
        const [x,y,z] = [a[0]/s, a[1]/s, 0], k = 1 - c
        this.Rf = [c+x*x*k, x*y*k-z, x*z*k+y, y*x*k+z, c+y*y*k, y*z*k-x, z*x*k-y, z*y*k+x, c+z*z*k]
      }
      const up = this.UP[this.value-1], R = this.Rf
      const ux = R[0]*up[0]+R[1]*up[1]+R[2]*up[2], uy = R[3]*up[0]+R[4]*up[1]+R[5]*up[2]
      const rl = Math.PI/2 - Math.atan2(uy, ux), cs = Math.cos(rl), sn = Math.sin(rl), Z = [cs,-sn,0,sn,cs,0,0,0,1], O = []
      for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) O.push(Z[i*3]*R[j] + Z[i*3+1]*R[3+j] + Z[i*3+2]*R[6+j])
      this.Rf = O
      this.dirty = true
    }
    applyHeight() { this.style.height = this.getAttribute('scroll-height') || '400vh' }
    readColors() {
      const cs = getComputedStyle(this), g = (a,v,d) => this.getAttribute(a) || cs.getPropertyValue(v).trim() || d
      this.cFg = g('fg','--d20-fg','#B7F5C0')
      this.cBg = g('bg','--d20-bg','#151222')
      this.cAc = g('accent','--d20-accent','#F2EEFA')
      this.dirty = true
    }
    progress() { const r = this.getBoundingClientRect(), span = r.height - innerHeight; return span > 0 ? Math.min(1, Math.max(0, -r.top/span)) : 0 }
    resize() {
      const dpr = Math.min(2, devicePixelRatio||1), w = this.cv.clientWidth, h = this.cv.clientHeight
      this.cv.width = w*dpr; this.cv.height = h*dpr; this.dpr = dpr; this.W = w; this.H = h
      const colsAttr = +this.getAttribute('cols')
      this.cols = colsAttr || Math.max(60, Math.min(320, Math.round(w/3.6)))
      this.cw = w / this.cols
      this.rows = Math.max(4, Math.floor(h/(this.cw*2)))
      this.dirty = true
    }
    draw(p) {
      const { cols, rows, V, F, N, B, ctx, cw } = this, ramp = ' .:-=+*#%@'
      const ch = new Array(cols*rows).fill(' '), kind = new Uint8Array(cols*rows), zb = new Float32Array(cols*rows).fill(-1e9)
      const e = 1 - Math.pow(1-p, 2), k = 1 - e
      const mul = (a,b) => { const o=[]; for (let i=0;i<3;i++) for (let j=0;j<3;j++) o.push(a[i*3]*b[j]+a[i*3+1]*b[3+j]+a[i*3+2]*b[6+j]); return o }
      const rx = a => [1,0,0,0,Math.cos(a),-Math.sin(a),0,Math.sin(a),Math.cos(a)]
      const ry = a => [Math.cos(a),0,Math.sin(a),0,1,0,-Math.sin(a),0,Math.cos(a)]
      const rz = a => [Math.cos(a),-Math.sin(a),0,Math.sin(a),Math.cos(a),0,0,0,1]
      const M = mul(rz(k*6.283), mul(rx(k*14.1), mul(ry(k*22), this.Rf)))
      const ap = (m,v) => [m[0]*v[0]+m[1]*v[1]+m[2]*v[2], m[3]*v[0]+m[4]*v[1]+m[5]*v[2], m[6]*v[0]+m[7]*v[1]+m[8]*v[2]]
      const hgt = Math.abs(Math.sin(k*8))*k*k*0.6
      const dx = Math.sin(k*9)*k*0.55
      const Wu = cols, Hu = rows*2, S = Math.min(Wu,Hu)*0.27, cx = Wu*(parseFloat(this.getAttribute('cx'))||0.5), cy = Hu*(parseFloat(this.getAttribute('cy'))||0.46)
      const proj = v => { const f = 5/(5-v[2]); return [cx+(v[0]+dx)*f*S, cy-(v[1]+hgt)*f*S, v[2]] }
      const P = V.map(v => proj(ap(M,v)))
      const L = [-0.45,0.65,0.62]
      const sx = cx + dx*S, sy = cy + 1.25*S, sr = S*(1.0 - Math.min(0.5, hgt*0.35)), si = 0.62 - Math.min(0.4, hgt*0.3)
      for (let j=0;j<rows;j++) for (let i=0;i<cols;i++) {
        const u = (i+0.5-sx)/sr, v = ((j+0.5)*2 - sy)/(sr*0.32), d = u*u+v*v
        if (d < 1) { const val = si*(1-d) + (B[(j&3)*4+(i&3)]/16 - 0.5)*0.4; const idx = Math.floor(val*ramp.length); if (idx > 0) { ch[j*cols+i] = ramp[Math.min(idx,4)]; kind[j*cols+i] = 2 } }
      }
      F.forEach((f, fi) => {
        const nf = ap(M, N[fi]); if (nf[2] <= 0.02) return
        const a = P[f[0]], b = P[f[1]], c = P[f[2]]
        const area = (b[0]-a[0])*(c[1]-a[1]) - (c[0]-a[0])*(b[1]-a[1]); if (Math.abs(area) < 1e-6) return
        const lens = [Math.hypot(c[0]-b[0], c[1]-b[1]), Math.hypot(a[0]-c[0], a[1]-c[1]), Math.hypot(b[0]-a[0], b[1]-a[1])]
        const shade = 0.14 + 0.86*Math.max(0, nf[0]*L[0]+nf[1]*L[1]+nf[2]*L[2])
        const qf = [5/(5-a[2]), 5/(5-b[2]), 5/(5-c[2])], cen = this.CEN[fi], upv = this.UP[fi], rt = this.RT[fi], mk = this.masks[fi+1]
        const Va = V[f[0]], Vb = V[f[1]], Vc = V[f[2]]
        const x0 = Math.max(0, Math.floor(Math.min(a[0],b[0],c[0]))), x1 = Math.min(cols-1, Math.ceil(Math.max(a[0],b[0],c[0])))
        const y0 = Math.max(0, Math.floor(Math.min(a[1],b[1],c[1])/2)), y1 = Math.min(rows-1, Math.ceil(Math.max(a[1],b[1],c[1])/2))
        for (let j = y0; j <= y1; j++) for (let i = x0; i <= x1; i++) {
          const px = i+0.5, py = (j+0.5)*2
          const w0 = ((b[0]-px)*(c[1]-py) - (c[0]-px)*(b[1]-py))/area
          const w1 = ((c[0]-px)*(a[1]-py) - (a[0]-px)*(c[1]-py))/area
          const w2 = 1 - w0 - w1
          if (w0 < 0 || w1 < 0 || w2 < 0) continue
          const z = w0*a[2]+w1*b[2]+w2*c[2], o = j*cols+i; if (z < zb[o]) continue; zb[o] = z
          const dEdge = Math.min(w0*Math.abs(area)/lens[0], w1*Math.abs(area)/lens[1], w2*Math.abs(area)/lens[2])
          if (dEdge < 0.9) { ch[o] = '#'; kind[o] = 1; continue }
          {
            const dn = w0*qf[0]+w1*qf[1]+w2*qf[2], b0 = w0*qf[0]/dn, b1 = w1*qf[1]/dn, b2 = 1-b0-b1
            let u = 0, v = 0
            for (let m = 0; m < 3; m++) { const r = b0*Va[m]+b1*Vb[m]+b2*Vc[m] - cen[m]; u += r*rt[m]; v += r*upv[m] }
            const mu = Math.floor((u+0.22)/0.44*96), mv = Math.floor((0.12-v)/0.34*64)
            if (mu >= 0 && mu < 96 && mv >= 0 && mv < 64 && mk[mv*96+mu] > 110) { ch[o] = '@'; kind[o] = 1; continue }
          }
          const val = shade + (B[(j&3)*4+(i&3)]/16 - 0.47)*0.4
          ch[o] = ramp[Math.max(1, Math.min(ramp.length-1, Math.floor(val*ramp.length)))]; kind[o] = 0
        }
      })
      const d = this.dpr; ctx.setTransform(d,0,0,d,0,0)
      ctx.fillStyle = this.cBg; ctx.fillRect(0,0,this.W,this.H)
      ctx.font = `${(cw/0.6).toFixed(1)}px ui-monospace, Menlo, Consolas, monospace`
      ctx.textAlign = 'center'; ctx.textBaseline = 'middle'
      const oy = (this.H - rows*cw*2)/2
      for (const pass of [2,0,1]) {
        ctx.fillStyle = pass === 1 ? this.cAc : this.cFg; ctx.globalAlpha = pass === 2 ? 0.45 : 1
        for (let j=0;j<rows;j++) for (let i=0;i<cols;i++) {
          const o = j*cols+i; if (ch[o] !== ' ' && kind[o] === pass) ctx.fillText(ch[o], (i+0.5)*cw, oy + (j+0.5)*cw*2)
        }
      }
      ctx.globalAlpha = 1
      const done = p > 0.985
      this.dispatchEvent(new CustomEvent('d20-progress', { detail: { progress: p, value: done ? this.value : null } }))
    }
  }
  customElements.define('ascii-d20', AsciiD20)
}

export function initLandingWiring() {
  const main = document.getElementById('dado')
  const overlay = document.querySelector('.hero-overlay')
  if (!main) return
  // Activa las reglas de ocultamiento (.js .hero-overlay / .js .nav-pill)
  // antes del primer paint para que el texto no aparezca antes del dado.
  document.documentElement.classList.add('js')
  const toRgb = (str) => { const c = document.createElement('canvas'); c.width = c.height = 1; const x = c.getContext('2d'); x.fillStyle = str; x.fillRect(0,0,1,1); const d = x.getImageData(0,0,1,1).data; return `rgb(${d[0]} ${d[1]} ${d[2]} / ${d[3]/255})` }
  const cs = getComputedStyle(document.documentElement)
  const tok = (n, f) => { const v = cs.getPropertyValue(n).trim(); return v ? toRgb(v) : f }
  main.setAttribute('fg', tok('--color-accent-2', '#B7F5C0'))
  main.setAttribute('bg', tok('--color-paper', '#151222'))
  main.setAttribute('accent', tok('--color-ink', '#F2EEFA'))
  main.setAttribute('cx', matchMedia('(max-width: 60rem)').matches ? '0.5' : '0.66')
  const nav = document.querySelector('.nav-pill')

  const mostrarChrome = () => {
    overlay?.classList.add('show')
    nav?.classList.add('show')
  }

  // Reduce motion: el dado ya está "caído" desde el primer frame.
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) {
    mostrarChrome()
    return
  }

  // El texto y el header aparecen recién cuando el dado termina de caer.
  let mostrado = false
  const onProgress = (e) => {
    if (mostrado) return
    if ((e.detail?.progress ?? 0) >= 0.88) {
      mostrado = true
      mostrarChrome()
      main.removeEventListener('d20-progress', onProgress)
    }
  }
  main.addEventListener('d20-progress', onProgress)
  // Si ya está al final (p. ej. scroll restaurado), mostrar de inmediato.
  if (main.progress && main.progress() >= 0.88) {
    mostrado = true
    mostrarChrome()
  }
}