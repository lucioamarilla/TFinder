import vue from 'eslint-plugin-vue'
import vueParser from 'vue-eslint-parser'

export default [
  {
    files: ['src/**/*.js', 'tests/**/*.js'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module'
    }
  },
  {
    files: ['src/**/*.vue'],
    plugins: { vue },
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      parser: vueParser
    },
    rules: {
      'vue/multi-word-component-names': 'off'
    }
  }
]
