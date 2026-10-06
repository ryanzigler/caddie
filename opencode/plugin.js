import { fileURLToPath } from 'node:url'
import { setupCaddie } from './runtime.mjs'

export default {
  id: 'caddie',
  setup: async (ctx) => setupCaddie(ctx, fileURLToPath(new URL('../', import.meta.url))),
}
