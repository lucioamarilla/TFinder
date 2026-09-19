/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js}'],
  theme: {
    extend: {
      colors: {
        coal: '#1A1A1A',
        ink: '#2B1D11',
        copper: '#8B5A2B',
        gold: { DEFAULT: '#D4AF37', deep: '#B8860B' },
        olive: { DEFAULT: '#556B2F', bright: '#6B8E23' },
        garnet: '#8B1A1A',
        vellum: '#FDF8EE',
        parchment: '#C2A980',
        bronze: '#8B7D6B',
        canvas: '#E5D3B3'
      },
      fontFamily: {
        logo: ['"Cinzel Decorative"', 'Cinzel', 'Georgia', 'serif'],
        mason: ['"IM Fell English"', '"Cinzel"', 'Georgia', 'serif'],
        minion: ['"EB Garamond"', 'Garamond', 'Georgia', 'serif'],
        tarzana: ['"Barlow Condensed"', '"Fira Sans Condensed"', 'sans-serif']
      },
      borderRadius: {
        tf: '2px'
      },
      minHeight: {
        touch: '44px'
      },
      boxShadow: {
        ledger: '0 4px 22px rgba(0,0,0,.35)',
        modal: '8px 16px 32px rgba(0,0,0,.35)',
        toast: '0 8px 26px rgba(0,0,0,.5)'
      }
    }
  },
  plugins: []
}