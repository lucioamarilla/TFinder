/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js}'],
  theme: {
    extend: {
      colors: {
        'tf-base': '#101820',
        'tf-raised': '#16212B',
        'tf-inset': '#0D161E',
        'tf-abyss': '#0B1015',
        'tf-ink': '#EAF6FF',
        'tf-ink-2': '#C9E2F5',
        'tf-muted': '#8FA6B8',
        'tf-inverse': '#0B1015',
        'tf-primary': '#38BDF8',
        'tf-primary-hover': '#6BC9FA',
        'tf-heal': '#4CC98A',
        'tf-damage': '#E07A5F',
        'tf-gold': '#C9A87C',
        'tf-arcane': '#9F7AEA',
        'tf-overlay': '#1C2A36'
      },
      fontFamily: {
        body: ['"Chivo"', 'ui-sans-serif', 'sans-serif'],
        lore: ['Newsreader', 'serif'],
        barlow: ['"Barlow Condensed"', 'sans-serif'],
        data: ['"DM Mono"', 'monospace'],
        logo: ['"Press Start 2P"', 'monospace'],
        // D-07: familias pergamino usadas por las vistas de gestión.
        mason: ['"Cinzel Decorative"', '"Algerian"', 'Georgia', 'serif'],
        tarzana: ['"Barlow Condensed"', '"Trebuchet MS"', 'sans-serif'],
        minion: ['"EB Garamond"', '"IM Fell English"', 'Georgia', 'serif']
      },
      borderRadius: {
        sm: '6px',
        md: '10px',
        lg: '14px',
        pill: '999px'
      }
    }
  },
  plugins: []
}