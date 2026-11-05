<template>
  <nav class="nav-pill" aria-label="Principal">
    <a class="wordmark" href="#">Tfinder</a>
    <nav>
      <a href="#controles">Controles</a>
      <a href="#feed">Feed</a>
      <a href="#datos">Datos</a>
      <a href="#estados">Estados</a>
    </nav>
    <button class="btn btn--secondary">Crear mesa</button>
  </nav>

  <header class="wrap section" style="padding-top: 160px;">
    <h1 style="font-size: var(--text-display); max-width: 14ch;">Piezas de la mesa</h1>
    <p class="lead" style="margin-block: var(--space-md) var(--space-lg);">El set que arma cada pantalla de TFinder.</p>
    <div style="display: flex; gap: var(--space-md); flex-wrap: wrap;">
      <button class="btn">Armar una pantalla</button>
      <a class="btn btn--secondary" href="#controles">Ver controles</a>
    </div>

    <article class="card" style="margin-top: var(--space-xl); display: grid; grid-template-columns: 56px minmax(0, 1fr); max-width: 720px;">
      <div class="vote" style="padding: var(--space-sm); border-right: var(--rule-hair) solid var(--color-rule);">
        <button aria-label="Votar a favor"><svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M8 3l5 6H3z"/></svg></button>
        <span class="count">42</span>
        <button aria-label="Votar en contra"><svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M8 13L3 7h10z"/></svg></button>
      </div>
      <div style="padding: var(--space-sm) var(--space-md);">
        <p class="post-title">Crítico confirmado ante el Zorro Glacial: <span class="num" style="color: inherit;">20/×2</span></p>
        <p class="label" style="margin-bottom: var(--space-2xs);">Publicado por Ezren, hace 2 h</p>
        <p style="font-size: var(--text-sm); color: var(--color-ink-2); margin-bottom: var(--space-sm);">El filo rúnico destelló en el corredor húmedo. La bestia chilló cuando la escarcha se quebró.</p>
        <div class="well crt" style="padding: var(--space-sm); margin-bottom: var(--space-sm);">
          <p class="label">Registro de combate 44, turno 4</p>
          <p style="font-size: var(--text-sm);"><span class="num" style="color: var(--color-accent-2);">3/5</span> jugadores listos, la iniciativa espera</p>
          <div class="seats" style="margin-top: var(--space-2xs);" aria-label="3 de 5 asientos ocupados">
            <i></i><i></i><i></i><i class="off"></i><i class="off"></i>
          </div>
        </div>
        <div style="display: flex; gap: var(--space-md); font-size: var(--text-sm); color: var(--color-muted);">
          <a class="text-link" href="#">12 comentarios</a>
          <a class="text-link" href="#">Compartir</a>
          <a class="text-link" href="#">Guardar</a>
        </div>
      </div>
    </article>
  </header>

  <section class="section wrap" id="colores">
    <h2>Colores</h2>
    <p class="lead" style="margin-bottom: var(--space-lg);">El tema presta paleta, tipografía y superficies; la estructura social no se toca.</p>
    <div class="score-line" style="grid-template-columns: repeat(6, minmax(0, 1fr));">
      <div><div style="height: 48px; background: var(--color-paper); border: var(--rule-hair) solid var(--color-rule);"></div><p class="label">paper</p></div>
      <div><div style="height: 48px; background: var(--color-paper-2); border: var(--rule-hair) solid var(--color-rule);"></div><p class="label">paper 2</p></div>
      <div><div style="height: 48px; background: var(--color-paper-3); border: var(--rule-hair) solid var(--color-rule);"></div><p class="label">paper 3</p></div>
      <div><div style="height: 48px; background: var(--color-ink);"></div><p class="label">ink</p></div>
      <div><div style="height: 48px; background: var(--color-accent);"></div><p class="label">ember</p></div>
      <div><div style="height: 48px; background: var(--color-accent-2);"></div><p class="label">acid</p></div>
    </div>
  </section>

  <section class="section wrap" id="tipografia">
    <h2>Tipografía</h2>
    <p class="lead" style="margin-bottom: var(--space-lg);">Bungee para el grito, Chivo para lo que se lee, Silkscreen solo en cifras grandes.</p>
    <div class="well" style="padding: var(--space-lg); display: grid; gap: var(--space-md);">
      <p class="display" style="font-size: var(--text-2xl);">Bungee, títulos de grito</p>
      <p style="font-weight: 900; font-size: var(--text-xl); letter-spacing: -0.02em;">Chivo 900, títulos de sección</p>
      <p style="font-size: var(--text-md);">Chivo 400, cuerpo y prosa a 16 px. La lectura larga de la wiki también viaja en Chivo.</p>
      <p><span class="figure-lg acid">—</span> <span style="font-weight: 700;">mesas abiertas</span> &nbsp; <span class="figure-lg ember">—</span> <span style="font-weight: 700;">fichas vivas</span></p>
      <p class="label">Silkscreen nunca baja de 40 px: abajo de eso, Chivo 700 con cifras tabulares (<span class="num">3/5, 1.600 XP, DC 16</span>).</p>
    </div>
  </section>

  <section class="section wrap" id="controles">
    <h2>Controles</h2>
    <p class="lead" style="margin-bottom: var(--space-lg);">Ocho estados en cada control: default, hover, focus, active, disabled, loading, error, success.</p>
    <h3>Botones</h3>
    <div style="display: flex; gap: var(--space-md); flex-wrap: wrap; margin-bottom: var(--space-md);">
      <button class="btn">Unirse</button>
      <button class="btn btn--secondary">Ver mesa</button>
      <button class="btn btn--danger">Salir</button>
      <button class="btn" disabled>Completa</button>
      <button class="btn btn--loading">Unirse</button>
    </div>
    <h3>Campos</h3>
    <div class="grid-2" style="gap: var(--space-md);">
      <div class="field"><label class="label" for="f1">Nombre de la mesa</label><input class="input" id="f1" placeholder="La Cripta de Vellmar"></div>
      <div class="field"><label class="label" for="f2">Email</label><input class="input is-error" id="f2" value="no-es-email"><p style="font-size: var(--text-xs); color: var(--color-error);">Ese email no funciona.</p></div>
      <div class="field"><label class="label" for="f3">Sistema</label><select class="input" id="f3"><option>Pathfinder 1e</option><option>Otro</option></select></div>
      <div class="field"><label class="label" for="f4">Descripción</label><textarea class="input" id="f4" placeholder="Contá la campaña"></textarea></div>
    </div>
    <h3 style="margin-top: var(--space-lg);">Elección y búsqueda</h3>
    <div style="display: flex; gap: var(--space-lg); flex-wrap: wrap; align-items: center;">
      <label style="display: flex; gap: var(--space-2xs); align-items: center; font-size: var(--text-sm);"><input type="checkbox" checked> Acepto las reglas</label>
      <label style="display: flex; gap: var(--space-2xs); align-items: center; font-size: var(--text-sm);"><input type="radio" name="r" checked> Jugador</label>
      <label style="display: flex; gap: var(--space-2xs); align-items: center; font-size: var(--text-sm);"><input type="radio" name="r"> Director</label>
      <input class="input" style="max-width: 320px;" type="search" placeholder="Buscar mesas, campañas, reglas">
    </div>
  </section>

  <section class="section wrap" id="feed">
    <h2>Feed</h2>
    <p class="lead" style="margin-bottom: var(--space-lg);">Vote control, tarjeta de publicación, hilo anidado y etiquetas.</p>
    <div style="display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: var(--space-lg); align-items: start;">
      <div>
        <div style="display: flex; gap: var(--space-2xs); margin-bottom: var(--space-sm);">
          <span class="tag tag--acid">Abierta</span><span class="tag tag--ember">Completa</span><span class="tag tag--ink">PF1e, nivel 4-6</span>
        </div>
        <div class="card" style="display: grid; grid-template-columns: 56px minmax(0, 1fr);">
          <div class="vote" style="padding: var(--space-sm); border-right: var(--rule-hair) solid var(--color-rule);">
            <button aria-label="Votar a favor"><svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M8 3l5 6H3z"/></svg></button>
            <span class="count">89</span>
            <button aria-label="Votar en contra"><svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M8 13L3 7h10z"/></svg></button>
          </div>
          <div style="padding: var(--space-sm) var(--space-md);">
            <h3>Duda con Toque Vampírico y Conjurar en Combate</h3>
            <p class="label" style="margin-bottom: var(--space-2xs);">Publicado por Amiri, hace 5 h</p>
            <p style="font-size: var(--text-sm); color: var(--color-ink-2); margin-bottom: var(--space-sm);">¿Provoca ataque de oportunidad con el paso de 5 pies?</p>
            <div style="display: flex; gap: var(--space-md); font-size: var(--text-sm); color: var(--color-muted);">
              <a class="text-link" href="#">28 comentarios</a><a class="text-link" href="#">Compartir</a>
            </div>
          </div>
        </div>
      </div>
      <div class="card" style="padding: var(--space-md);">
        <p class="label">Hilo de campaña, sesión 04</p>
        <div class="thread">
          <div class="reply">
            <span class="num" style="font-size: var(--text-sm); color: var(--color-accent-2);">VA</span>
            <div><p style="font-size: var(--text-sm);"><strong>Valeros</strong> <span class="tag tag--ink">Director</span></p><p style="font-size: var(--text-sm); color: var(--color-ink-2);">El corredor colapsa: tirá Reflejo DC 16.</p></div>
          </div>
          <div class="reply level-2">
            <span class="num" style="font-size: var(--text-sm); color: var(--color-accent);">KY</span>
            <div><p style="font-size: var(--text-sm);"><strong>Kyra</strong> <span class="tag tag--ink">Clérigo</span></p><p style="font-size: var(--text-sm); color: var(--color-ink-2);">Reflejo 18. Canalizo energía positiva.</p></div>
          </div>
          <div class="reply level-3 cursor-row">
            <span class="num" style="font-size: var(--text-sm);">ME</span>
            <p style="font-size: var(--text-sm);"><strong>Merisiel</strong>: evasión mejorada, 0 de daño.</p>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="section wrap" id="mesas">
    <h2>Mesas</h2>
    <p class="lead" style="margin-bottom: var(--space-lg);">Tarjeta de mesa, fila de lista y seat meter.</p>
    <div class="grid-2">
      <div class="card">
        <div class="crt" style="height: 88px; background: var(--color-paper-3); border-bottom: var(--rule-bar) solid var(--color-accent);"></div>
        <div style="padding: var(--space-md);">
          <div style="display: flex; gap: var(--space-2xs); margin-bottom: var(--space-2xs);"><span class="tag tag--ink">PF1e</span><span class="tag tag--acid">Abierta</span></div>
          <h3>La Cripta de Vellmar</h3>
          <p style="font-size: var(--text-sm); color: var(--color-ink-2); margin-bottom: var(--space-sm);">Dirigida por Lucio Amarilla, viernes 21:00</p>
          <div style="display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: var(--space-2xs);"><span class="seats" aria-label="2 de 5"><i></i><i></i><i class="off"></i><i class="off"></i><i class="off"></i></span><span class="num" style="font-size: var(--text-sm);">2/5</span></div>
            <button class="btn">Unirse</button>
          </div>
        </div>
      </div>
      <div class="card" style="align-self: start;">
        <div class="mesa-row">
          <div class="crt" style="width: 48px; height: 48px; background: var(--color-paper-3); border: var(--rule-hair) solid var(--color-rule);"></div>
          <div><p style="font-weight: 700; font-size: var(--text-sm);">Sombras de Westcrown</p><p style="font-size: var(--text-xs); color: var(--color-muted);">GM Asmodeus, domingos 18:00</p></div>
          <div class="mesa-row-actions" style="display: flex; align-items: center; gap: var(--space-2xs);"><span class="num" style="font-size: var(--text-sm);">3/6</span><button class="btn btn--secondary">Ver</button></div>
        </div>
        <div class="mesa-row">
          <div class="crt" style="width: 48px; height: 48px; background: var(--color-paper-3); border: var(--rule-hair) solid var(--color-rule);"></div>
          <div><p style="font-weight: 700; font-size: var(--text-sm);">Ecos de Golarion</p><p style="font-size: var(--text-xs); color: var(--color-muted);">GM Starstone, viernes 22:00</p></div>
          <div class="mesa-row-actions" style="display: flex; align-items: center; gap: var(--space-2xs);"><span class="num" style="font-size: var(--text-sm);">6/6</span><span class="tag tag--ember">Completa</span></div>
        </div>
      </div>
    </div>
  </section>

  <section class="section wrap" id="datos">
    <h2>Datos de juego</h2>
    <p class="lead" style="margin-bottom: var(--space-lg);">Tablas con fila cursor, statblock y presupuesto de encuentro.</p>
    <div style="display: grid; grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr); gap: var(--space-lg); align-items: start;">
      <div class="well" style="overflow: hidden;">
        <table style="width: 100%; border-collapse: collapse;">
          <thead><tr><th style="text-align: left; padding: var(--space-2xs) var(--space-sm); font-size: var(--text-sm); color: var(--color-muted); border-bottom: var(--rule-bar) solid var(--color-rule);">Criatura</th><th style="text-align: left; padding: var(--space-2xs) var(--space-sm); font-size: var(--text-sm); color: var(--color-muted); border-bottom: var(--rule-bar) solid var(--color-rule);">CR</th><th style="text-align: left; padding: var(--space-2xs) var(--space-sm); font-size: var(--text-sm); color: var(--color-muted); border-bottom: var(--rule-bar) solid var(--color-rule);">XP</th></tr></thead>
          <tbody>
            <tr class="row-hover"><td style="padding: var(--space-2xs) var(--space-sm); font-size: var(--text-sm);">Goblin</td><td class="num" style="padding: var(--space-2xs) var(--space-sm); font-size: var(--text-sm);">1/3</td><td class="num" style="padding: var(--space-2xs) var(--space-sm); font-size: var(--text-sm);">135</td></tr>
            <tr class="cursor-row"><td style="padding: var(--space-2xs) var(--space-sm); font-size: var(--text-sm); font-weight: 700;">Zorro Glacial</td><td class="num" style="padding: var(--space-2xs) var(--space-sm); font-size: var(--text-sm);">3</td><td class="num" style="padding: var(--space-2xs) var(--space-sm); font-size: var(--text-sm);">800</td></tr>
            <tr class="row-hover"><td style="padding: var(--space-2xs) var(--space-sm); font-size: var(--text-sm);">Troll</td><td class="num" style="padding: var(--space-2xs) var(--space-sm); font-size: var(--text-sm);">5</td><td class="num" style="padding: var(--space-2xs) var(--space-sm); font-size: var(--text-sm);">1.600</td></tr>
          </tbody>
        </table>
      </div>
      <div class="well" style="padding: var(--space-md);">
        <h3>Zorro Glacial</h3>
        <p class="label" style="margin-bottom: var(--space-sm);">Bestia mágica</p>
        <div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--space-sm); text-align: center; margin-bottom: var(--space-md);">
          <div><p class="label">CA</p><p class="num">16</p></div>
          <div><p class="label">PV</p><p class="num" style="color: var(--color-accent);">34</p></div>
          <div><p class="label">Reflejo</p><p class="num">+5</p></div>
        </div>
        <div style="border-top: var(--rule-bar) solid var(--color-accent-2); padding-top: var(--space-md);">
          <p class="figure-lg">4</p>
          <p class="label">APL del grupo</p>
          <div style="height: 10px; background: var(--color-paper-3); margin-top: var(--space-2xs);"><div style="width: 64%; height: 100%; background: var(--color-accent-2);"></div></div>
          <p class="label" style="margin-top: var(--space-2xs);">640 de 1.000 XP</p>
        </div>
      </div>
    </div>
  </section>

  <section class="section wrap" id="estados">
    <h2>Estados</h2>
    <p class="lead" style="margin-bottom: var(--space-lg);">Cada región de datos tiene cuatro estados: cargando, vacío, error y lleno.</p>
    <div class="compare">
      <div class="well" style="padding: var(--space-md);">
        <p class="label" style="margin-bottom: var(--space-sm);">Cargando</p>
        <div style="display: grid; gap: var(--space-2xs);"><div style="height: 14px; width: 60%; background: var(--color-paper-3);"></div><div style="height: 14px; width: 40%; background: var(--color-paper-3);"></div></div>
      </div>
      <div class="well" style="padding: var(--space-md);">
        <p class="label" style="margin-bottom: var(--space-sm);">Vacío</p>
        <p style="font-size: var(--text-sm);">Nadie posteó todavía.</p>
        <button class="btn btn--secondary" style="margin-top: var(--space-sm);">Escribir el primer post</button>
      </div>
      <div class="well" style="padding: var(--space-md);">
        <p class="label" style="margin-bottom: var(--space-sm);">Error</p>
        <p style="font-size: var(--text-sm); color: var(--color-error);">No pudimos cargar las mesas.</p>
        <button class="btn btn--secondary" style="margin-top: var(--space-sm);">Reintentar</button>
      </div>
      <div class="well crt" style="padding: var(--space-md);">
        <p class="label" style="margin-bottom: var(--space-sm);">Pantalla 404</p>
        <p class="figure-lg">404</p>
        <p style="font-size: var(--text-sm);">Esta cripta no existe.</p>
        <button class="btn" style="margin-top: var(--space-sm);">Volver al inicio</button>
      </div>
    </div>
  </section>

  <footer class="colophon">
    <div class="wrap cols">
      <div>
        <p class="display" style="font-size: var(--text-md); color: var(--color-accent-2);">Tfinder</p>
        <p class="label">Encontrá tu mesa y tirá iniciativa</p>
      </div>
      <div>
        <p class="label" style="margin-bottom: var(--space-2xs);">Catálogo</p>
        <p style="font-size: var(--text-sm);"><a class="text-link" href="#controles">Controles</a>, <a class="text-link" href="#feed">feed</a>, <a class="text-link" href="#datos">datos</a>, <a class="text-link" href="#estados">estados</a></p>
      </div>
      <div>
        <p class="label" style="margin-bottom: var(--space-2xs);">Sistema</p>
        <p style="font-size: var(--text-sm); color: var(--color-muted);">Tema Arcade, deal 2/3, draw 4e5ee7. OGL 1.0a, Paizo Inc.</p>
      </div>
    </div>
  </footer>
</template>

<script setup></script>

<style>
.wrap { max-width: var(--container); margin-inline: auto; padding-inline: var(--gutter); }
.section { padding-block: var(--section-gap-s); }
.section + .section { border-top: var(--rule-hair) solid var(--color-rule); }
.display { font-family: var(--font-display); font-weight: var(--display-weight, 400); line-height: 1.02; text-transform: uppercase; letter-spacing: var(--tracking-display); text-shadow: -1.5px 0 0 var(--color-crt-r), 1.5px 0 0 var(--color-crt-c); }
h1, h2, h3 { margin: 0; }
h2 { font-family: var(--font-body); font-weight: 900; letter-spacing: -0.02em; line-height: 1; font-size: var(--text-section); margin: 0 0 var(--space-md); }
h3 { font-family: var(--font-body); font-weight: 900; letter-spacing: -0.02em; line-height: 1; font-size: var(--text-title); margin: 0 0 var(--space-sm); }
.lead { font-size: var(--text-lead); color: var(--color-ink-2); max-width: 56ch; }
.label { font-weight: 700; font-size: var(--text-sm); color: var(--color-muted); }
.figure-lg { font-family: var(--font-outlier); font-weight: 700; font-size: var(--text-display-s); line-height: 1; font-variant-numeric: tabular-nums; color: var(--color-ink); }
.figure-lg.acid { color: var(--color-accent-2); }
.figure-lg.ember { color: var(--color-accent); }
.post-title { font-weight: 900; letter-spacing: -0.02em; line-height: 1.1; font-size: var(--text-lg); margin: var(--space-2xs) 0; }
.thread { display: grid; gap: var(--space-sm); margin-top: var(--space-sm); }
.thread .reply { display: grid; grid-template-columns: 40px minmax(0, 1fr); gap: var(--space-sm); }
.thread .reply.level-2 { padding-left: var(--space-lg); border-left: var(--rule-hair) solid var(--color-rule); margin-left: var(--space-lg); }
.thread .reply.level-3 { padding: var(--space-3xs) var(--space-sm); margin-left: calc(var(--space-lg) * 2); }
.num { font-weight: 700; font-variant-numeric: tabular-nums; }
.nav-pill { position: fixed; top: var(--space-md); left: 50%; translate: -50% 0; z-index: var(--z-sticky-nav); display: flex; align-items: center; gap: var(--space-md); background: var(--color-paper-2); border: var(--rule-bar) solid var(--color-rule); border-radius: var(--radius-card); padding: var(--space-2xs) var(--space-sm); box-shadow: var(--shadow-card); }
.wordmark { font-family: var(--font-display); font-size: var(--text-sm); color: var(--color-accent-2); text-transform: uppercase; text-decoration: none; }
.nav-pill nav { display: flex; gap: var(--space-sm); }
.nav-pill a { color: var(--color-ink); text-decoration: none; font-weight: 700; font-size: var(--text-sm); border-bottom: 2px solid var(--color-accent-2); padding-bottom: 1px; }
.nav-pill a:hover { color: var(--color-accent-2); }
@media (max-width: 60rem) { .nav-pill { left: var(--space-sm); right: var(--space-sm); translate: 0; gap: var(--space-2xs); } .nav-pill nav { display: none; } }
.btn { display: inline-flex; align-items: center; justify-content: center; gap: var(--space-2xs); background: var(--color-accent); color: var(--color-accent-ink); border: var(--rule-bar) solid var(--color-ink); border-radius: var(--radius-card); padding: var(--space-xs) var(--space-lg); font-family: var(--font-body); font-weight: 700; font-size: var(--text-sm); white-space: nowrap; cursor: pointer; box-shadow: var(--shadow-card); transition: translate var(--dur-micro) var(--ease-out), box-shadow var(--dur-micro) var(--ease-out); }
.btn:hover { translate: -1px -1px; box-shadow: 7px 7px 0 var(--color-accent-2); }
.btn:active { translate: 3px 3px; box-shadow: 2px 2px 0 var(--color-accent-2); }
.btn--secondary { background: transparent; color: var(--color-ink); }
.btn--danger { background: transparent; color: var(--color-error); border-color: var(--color-error); }
.btn:disabled { opacity: 0.5; cursor: not-allowed; translate: none; }
.btn--loading { color: transparent; position: relative; }
.btn--loading::after { content: ""; position: absolute; width: 14px; height: 14px; border: 2px solid var(--color-accent-ink); border-top-color: transparent; border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
a.text-link { color: var(--color-ink); text-decoration: none; border-bottom: 2px solid var(--color-accent-2); white-space: nowrap; }
a.text-link:hover { color: var(--color-accent-2); }
.card { background: var(--color-paper-2); border: var(--rule-hair) solid var(--color-rule); border-radius: var(--radius-card); color: var(--color-ink); }
.well { background: var(--color-paper-2); border: var(--rule-bar) solid var(--color-rule); border-radius: var(--radius-card); }
.tag { display: inline-block; font-weight: 700; font-size: var(--text-xs); padding: var(--space-3xs) var(--space-2xs); border: var(--rule-bar) solid currentColor; border-radius: var(--radius-card); }
.tag--acid { color: var(--color-accent-2); }
.tag--ember { color: var(--color-accent); }
.tag--ink { color: var(--color-muted); }
.row-hover:hover { background: var(--color-paper-3); }
.cursor-row { background: var(--color-accent); color: var(--color-accent-ink); transition: background-color var(--dur-micro) steps(1); }
.field { display: flex; flex-direction: column; gap: var(--space-2xs); }
.input { height: 52px; padding: 0 var(--space-sm); background: var(--color-paper); border: var(--rule-bar) solid var(--color-muted); border-radius: var(--radius-card); color: var(--color-ink); font-family: var(--font-body); font-size: var(--text-md); width: 100%; }
.input::placeholder { color: var(--color-muted); }
.input:focus-visible { outline: 2px solid var(--color-focus); outline-offset: 2px; border-color: var(--color-focus); }
.input.is-error { border-color: var(--color-error); }
.input:disabled { background: var(--color-paper-3); color: var(--color-muted); border-style: dashed; cursor: not-allowed; }
textarea.input { height: auto; min-height: 120px; padding: var(--space-sm); resize: vertical; }
.vote { display: flex; flex-direction: column; align-items: center; gap: var(--space-3xs); }
.vote button { background: none; border: none; color: var(--color-muted); cursor: pointer; padding: var(--space-3xs); }
.vote button:hover { color: var(--color-accent-2); }
.vote .count { font-weight: 700; font-variant-numeric: tabular-nums; color: var(--color-ink); }
.seats { display: flex; gap: var(--space-2xs); align-items: center; }
.seats i { width: 10px; height: 10px; background: var(--color-accent-2); border: var(--rule-hair) solid var(--color-paper); }
.seats i.off { background: var(--color-paper-3); border-color: var(--color-rule); }
.grid-2 { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: var(--space-lg); align-items: start; }
@media (max-width: 60rem) { .grid-2 { grid-template-columns: minmax(0, 1fr); } .compare { grid-template-columns: minmax(0, 1fr); } }
.mesa-row { display: grid; grid-template-columns: 48px minmax(0, 1fr) auto; gap: var(--space-sm); align-items: center; padding: var(--space-sm); }
.mesa-row + .mesa-row { border-top: var(--rule-hair) solid var(--color-rule); }
@media (max-width: 60rem) { .mesa-row { grid-template-columns: 48px minmax(0, 1fr); } .mesa-row .mesa-row-actions { grid-column: 2; justify-self: start; } }
.crt { position: relative; isolation: isolate; }
.crt::after { content: ""; position: absolute; inset: 0; pointer-events: none; z-index: var(--z-base); background-image: repeating-linear-gradient(to right, color-mix(in oklab, var(--color-crt-r) 5%, transparent) 0 1px, color-mix(in oklab, var(--color-crt-g) 5%, transparent) 1px 2px, color-mix(in oklab, var(--color-crt-b) 5%, transparent) 2px 3px), repeating-linear-gradient(to bottom, transparent 0 2px, color-mix(in oklab, var(--color-shade) 16%, transparent) 2px 3px); }
.score-line { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); border-block: var(--rule-bar) solid var(--color-rule); }
.score-line > div { padding: var(--space-md); border-inline-start: var(--rule-bar) solid var(--color-rule); }
.score-line > div:first-child { border-inline-start: none; }
.compare { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: var(--space-md); }
.compare .well { border-top: var(--rule-bar) solid var(--color-accent); }
.compare .well.acid { border-top-color: var(--color-accent-2); }
@media (max-width: 60rem) { .compare { grid-template-columns: minmax(0, 1fr); } }
footer.colophon { border-top: var(--rule-bar) solid var(--color-rule); padding-block: var(--space-xl); }
footer.colophon .cols { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--space-lg); }
footer.colophon a { color: var(--color-ink-2); text-decoration: none; border-bottom: 2px solid var(--color-accent-2); }
@media (max-width: 60rem) { footer.colophon .cols { grid-template-columns: minmax(0, 1fr); } }
</style>