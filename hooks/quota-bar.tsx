import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { QuotaCategory, QuotaContext, QuotaLimit, QuotaSnapshot } from '../types'

const snapshot = atom({ plugin: 'caddie', key: 'snapshot' } as const, null)
const isOn = atom({ plugin: 'caddie', key: 'isOn' } as const, true)

const PALETTE = ['#a78bfa', '#60a5fa', '#f472b6', '#34d399', '#fbbf24', '#fb923c', '#22d3ee', '#c084fc']
const MUTED = '#8b90a0'
const GREEN = '#4ade80'
const AMBER = '#fbbf24'
const RED = '#f87171'
const FREE = '#3f4452'
const BUFFER = '#6b7080'
const TRACK = '#2e3240'

const SEP = ' – '
const LIMIT_CELLS = 16
const GROW_SCALE = 1000
const LEGEND_MIN_SHARE = 0.003
const EARLY_SHARE = 0.03

const HOUR = 3_600_000
const DAY = 24 * HOUR
const WINDOWS: Record<string, { label: string; ms: number }> = {
  five_hour: { label: '5 hour', ms: 5 * HOUR },
  seven_day: { label: 'Weekly', ms: 7 * DAY },
}

type Severity = 'ok' | 'amber' | 'red'

type Forecast =
  | { state: 'unknown' }
  | { state: 'hit'; resetsAt: number }
  | { state: 'early'; resetsAt: number }
  | { state: 'track'; resetsAt: number; projected: number }
  | { state: 'out'; resetsAt: number; runOutAt: number; severity: Severity }

const COLOR: Record<Severity, string> = { ok: GREEN, amber: AMBER, red: RED }

function forecast(limit: QuotaLimit, now: number): Forecast {
  const window = WINDOWS[limit.kind]
  const resetsAt = limit.resetsAt === null ? NaN : Date.parse(limit.resetsAt)
  if (window === undefined || !Number.isFinite(resetsAt)) {
    return { state: 'unknown' }
  }
  const p = limit.percentUsed
  if (p >= 100) {
    return { state: 'hit', resetsAt }
  }
  const elapsed = window.ms - (resetsAt - now)
  if (elapsed < window.ms * EARLY_SHARE) {
    return { state: 'early', resetsAt }
  }
  const rate = p / elapsed
  const projected = p + rate * (resetsAt - now)
  if (projected < 100) {
    return { state: 'track', resetsAt, projected }
  }

  return {
    state: 'out',
    resetsAt,
    runOutAt: now + (100 - p) / rate,
    severity: projected > 130 ? 'red' : 'amber',
  }
}

function severityOf(f: Forecast): Severity {
  if (f.state === 'hit') return 'red'
  if (f.state === 'out') return f.severity

  return 'ok'
}

function duration(ms: number): string {
  const minutes = Math.max(0, Math.round(ms / 60_000))
  const days = Math.floor(minutes / 1440)
  const hours = Math.floor((minutes % 1440) / 60)
  const mins = minutes % 60
  if (days > 0) return `${days}d ${hours}h`
  if (hours > 0) return mins === 0 ? `${hours}h` : `${hours}h ${mins}m`

  return `${mins}m`
}

const TIME = new Intl.DateTimeFormat('en-US', { hour: 'numeric', minute: '2-digit' })
const WEEKDAY = new Intl.DateTimeFormat('en-US', { weekday: 'long' })
const DAY_KEY = new Intl.DateTimeFormat('en-US', { year: 'numeric', month: '2-digit', day: '2-digit' })

const isSameDay = (a: number, b: number) => DAY_KEY.format(a) === DAY_KEY.format(b)

function resetPhrase(at: number, now: number): string {
  return isSameDay(at, now) ? `the ${TIME.format(at)} reset` : `${WEEKDAY.format(at)}’s reset`
}

function resumePhrase(at: number, now: number): string {
  return isSameDay(at, now) ? TIME.format(at) : `${TIME.format(at)} on ${WEEKDAY.format(at)}`
}

function tokens(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 10_000) return `${Math.round(n / 1000)}k`
  if (n >= 1000) return `${(n / 1000).toFixed(1)}k`

  return `${Math.round(n)}`
}

function grow(share: number): number {
  return Math.min(GROW_SCALE, Math.max(1, Math.round(share * GROW_SCALE)))
}

type Headline = { text: string; color: string }

function headline(limits: QuotaLimit[], now: number): Headline | null {
  const rows = limits.map(limit => ({ limit, f: forecast(limit, now) }))
  const hit = rows.flatMap(({ f }) => (f.state === 'hit' ? [f.resetsAt] : []))
  if (hit.length > 0) {
    return { text: `Limit reached. Usage resumes at ${resumePhrase(Math.max(...hit), now)}.`, color: RED }
  }
  const out = rows
    .flatMap(({ f }) => (f.state === 'out' ? [f] : []))
    .sort((a, b) => a.runOutAt - b.runOutAt)[0]
  if (out !== undefined) {
    return {
      text: `At this pace you’ll run out before ${resetPhrase(out.resetsAt, now)}.`,
      color: COLOR[out.severity],
    }
  }
  const lead = rows.find(({ limit }) => limit.kind === 'seven_day') ?? rows[0]
  if (lead === undefined || lead.f.state === 'unknown') {
    return null
  }

  return {
    text: `On track. You should reach ${resetPhrase(lead.f.resetsAt, now)} with room to spare.`,
    color: GREEN,
  }
}

function limitNote(f: Forecast, now: number): string {
  switch (f.state) {
    case 'unknown':
      return ''
    case 'hit':
      return `limit reached${SEP}resets in ${duration(f.resetsAt - now)}`
    case 'early':
      return `on track${SEP}resets in ${duration(f.resetsAt - now)}`
    case 'track':
      return `about ${Math.round(f.projected)}% by reset${SEP}resets in ${duration(f.resetsAt - now)}`
    case 'out':
      return `${duration(f.resetsAt - f.runOutAt)} before reset${SEP}resets in ${duration(f.resetsAt - now)}`
  }
}

function fillColor(percent: number): string {
  if (percent >= 90) return RED
  if (percent >= 70) return AMBER

  return GREEN
}

async function measure($: EngineInterface): Promise<QuotaSnapshot> {
  const usage = await $.session.usage({ breakdown: 'summary' })
  const takenAt = await $.clock.now()
  const b = usage.context.breakdown
  let context: QuotaContext | null = null
  if (b !== undefined && b.rawMaxTokens > 0) {
    const categories: QuotaCategory[] = b.categories.flatMap(c =>
      c.kind === 'deferred' || c.tokens <= 0 ? [] : [{ name: c.name, tokens: c.tokens, kind: c.kind }],
    )
    context = {
      percent: b.percentage,
      window: b.rawMaxTokens,
      free: Math.max(0, b.rawMaxTokens - b.totalTokens),
      categories,
    }
  } else if (usage.context.tokens !== undefined && usage.context.window > 0) {
    const { tokens: used, window } = usage.context
    context = {
      percent: usage.context.percent ?? Math.round((used / window) * 100),
      window,
      free: Math.max(0, window - used),
      categories: [
        { name: 'Used', tokens: used, kind: 'used' },
        { name: 'Free space', tokens: Math.max(0, window - used), kind: 'free' },
      ],
    }
  }
  const rateLimits: QuotaLimit[] = usage.rateLimits.map(r => ({
    kind: r.kind,
    percentUsed: r.percentUsed,
    resetsAt: r.resetsAt ?? null,
  }))

  return { takenAt, context, rateLimits }
}

let hasError = false

function errorText(error: unknown): string {
  const message = error instanceof Error ? error.message : String(error)

  return `quota-bar: ${message.replace(/^caddie: /, '')}`
}

async function refresh($: EngineInterface): Promise<void> {
  if (!(await read($, isOn))) {
    return
  }
  try {
    const next = await measure($)
    await update($, snapshot, () => next)
    if (hasError) {
      hasError = false
      $.ui.status(undefined)
    }
  } catch (error) {
    hasError = true
    $.ui.status(errorText(error))
  }
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    try {
      await $.command.register({ name: 'quota', description: 'Show or hide the quota bar above the prompt' })
    } catch (error) {
      $.ui.status(errorText(error))
    }
    await refresh($)

    return next(e)
  })

  on('session.measure', async ($, e, next) => {
    await refresh($)

    return next(e)
  })

  on('turn.complete', async ($, e, next) => {
    const result = await next(e)
    await refresh($)

    return result
  })

  on('command.run', { command: 'quota' }, async $ => {
    const showing = !(await read($, isOn))
    await update($, isOn, () => showing)
    if (showing) {
      await refresh($)
    }

    return { text: showing ? 'Quota bar on.' : 'Quota bar off.' }
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (e.props.hasSurvey || !(await read($, isOn))) {
      return next(e)
    }
    const snap = await read($, snapshot)
    if (snap === null || (snap.context === null && snap.rateLimits.length === 0)) {
      return next(e)
    }
    const { Box, Text } = $.ui.resolve(e)
    const now = snap.takenAt
    const head = headline(snap.rateLimits, now)
    const ctx = snap.context
    let paletteIndex = 0
    const colored = (ctx?.categories ?? []).map(c => {
      const color =
        c.kind === 'free' ? FREE : c.kind === 'buffer' ? BUFFER : PALETTE[paletteIndex++ % PALETTE.length]!

      return { ...c, color }
    })
    const legend = ctx === null ? [] : colored.filter(c => c.tokens / ctx.window >= LEGEND_MIN_SHARE)

    return (
      <Box key="quota-bar" flexDirection="column" width={e.props.bodyColumns}>
        {head !== null && (
          <Text key="headline" bold color={head.color}>
            {head.text}
          </Text>
        )}
        {ctx !== null && (
          <Box key="context" flexDirection="row" justifyContent="space-between">
            <Text key="context-used" bold color={fillColor(ctx.percent)}>
              {`Context ${Math.round(ctx.percent)}% used`}
            </Text>
            <Text key="context-free" color={MUTED}>
              {`${tokens(ctx.free)} free of ${tokens(ctx.window)}`}
            </Text>
          </Box>
        )}
        {ctx !== null && (
          <Box key="context-bar" flexDirection="row">
            {colored.map((c, i) => (
              <Box key={`seg-${i}`} flexGrow={grow(c.tokens / ctx.window)} backgroundColor={c.color}>
                <Text> </Text>
              </Box>
            ))}
          </Box>
        )}
        {legend.length > 0 && (
          <Box key="legend" flexDirection="row" flexWrap="wrap" columnGap={2}>
            {legend.map((c, i) => (
              <Box key={`legend-${i}`} flexDirection="row" gap={1}>
                <Text color={c.color}>{c.name}</Text>
                <Text color={MUTED}>{tokens(c.tokens)}</Text>
              </Box>
            ))}
          </Box>
        )}
        {snap.rateLimits.map(limit => {
          const f = forecast(limit, now)
          const color = COLOR[severityOf(f)]
          const filled = Math.round((Math.min(100, Math.max(0, limit.percentUsed)) / 100) * LIMIT_CELLS)
          const label = WINDOWS[limit.kind]?.label ?? limit.kind
          const note = limitNote(f, now)

          return (
            <Box key={`limit-${limit.kind}`} flexDirection="row" gap={1}>
              <Box width={8}>
                <Text>{label}</Text>
              </Box>
              <Box width={LIMIT_CELLS} flexDirection="row">
                {filled > 0 && (
                  <Box flexGrow={filled} backgroundColor={color}>
                    <Text> </Text>
                  </Box>
                )}
                {filled < LIMIT_CELLS && (
                  <Box flexGrow={LIMIT_CELLS - filled} backgroundColor={TRACK}>
                    <Text> </Text>
                  </Box>
                )}
              </Box>
              <Text key={`limit-${limit.kind}-pct`} bold color={color}>
                {`${Math.round(limit.percentUsed)}%`}
              </Text>
              {note !== '' && (
                <Text key={`limit-${limit.kind}-note`} color={MUTED}>
                  {note}
                </Text>
              )}
            </Box>
          )
        })}
      </Box>
    )
  })
}
