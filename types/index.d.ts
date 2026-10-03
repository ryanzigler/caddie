export type QuotaCategoryKind = 'used' | 'free' | 'buffer'

export type QuotaCategory = {
  name: string
  tokens: number
  kind: QuotaCategoryKind
}

export type QuotaContext = {
  percent: number
  window: number
  free: number
  categories: QuotaCategory[]
}

export type QuotaLimit = {
  kind: string
  percentUsed: number
  resetsAt: string | null
}

export type QuotaSnapshot = {
  takenAt: number
  context: QuotaContext | null
  rateLimits: QuotaLimit[]
}

declare module 'claude-code' {
  interface PluginState {
    caddie: { snapshot: QuotaSnapshot | null; isOn: boolean }
  }
}
