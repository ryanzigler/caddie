import { describe, expect, mock, test } from 'claude-code/testing'
import type { Engine } from 'claude-code/testing'
import type { On, SessionUsage } from 'claude-code'

// Monday 5 October 2026, 12:00 UTC. Resets sit at noon UTC so the weekday reads
// the same in every time zone from UTC-11 to UTC+11.
const NOW = Date.UTC(2026, 9, 5, 12, 0)
const HOUR = 3_600_000
const DAY = 24 * HOUR
const iso = (ms: number) => new Date(ms).toISOString()

const SURFACES = ['terminal', 'desktop'] as const

const BAND = {
  component: 'AbovePrompt',
  props: { hasSurvey: false, isWorking: false, maxRows: 20, bodyColumns: 100, scroll: { offset: 0, bodyRows: 20 } },
} as const

const BREAKDOWN = {
  categories: [
    { name: 'System prompt', tokens: 3_000, color: 'promptBorder', isDeferred: false, kind: 'used' },
    { name: 'System tools', tokens: 15_000, color: 'inactive', isDeferred: false, kind: 'used' },
    { name: 'Memory files', tokens: 1_000, color: 'claude', isDeferred: false, kind: 'used' },
    { name: 'Messages', tokens: 99_000, color: 'permission', isDeferred: false, kind: 'used' },
    { name: 'MCP tools', tokens: 20_000, color: 'warning', isDeferred: true, kind: 'deferred' },
    { name: 'Free space', tokens: 837_000, color: 'promptBorder', isDeferred: false, kind: 'free' },
    { name: 'Autocompact buffer', tokens: 45_000, color: 'inactive', isDeferred: false, kind: 'buffer' },
  ],
  totalTokens: 118_000,
  maxTokens: 1_000_000,
  rawMaxTokens: 1_000_000,
  autocompactSource: 'auto',
  percentage: 12,
  gridRows: [],
  model: 'claude-opus-5-5[1m]',
  memoryFiles: [],
  mcpTools: [],
  agents: [],
  isAutoCompactEnabled: true,
  apiUsage: null,
} as const

function usageWith(rateLimits: SessionUsage['rateLimits']): SessionUsage {
  return {
    startedAt: NOW - HOUR,
    context: { tokens: 118_000, window: 1_000_000, percent: 12, breakdown: BREAKDOWN },
    rateLimits,
  }
}

const ON_TRACK = usageWith([
  // 20% two hours into five: about 50% by reset.
  { kind: 'five_hour', percentUsed: 20, resetsAt: iso(NOW + 3 * HOUR) },
  // 50% five days into seven: about 70% by reset, on Wednesday.
  { kind: 'seven_day', percentUsed: 50, resetsAt: iso(NOW + 2 * DAY) },
])

type Answer = { value: SessionUsage } | { deny: string }

type World = { statuses: (string | undefined)[]; commands: string[] }

// Answers what lies beneath the plugin: the clock, the usage figures, and the
// engine's own ends of the events the plugin passes on.
function world(on: On, usage: () => SessionUsage | Answer): World {
  const seen: World = { statuses: [], commands: [] }
  mock.clock(on, { now: NOW })
  on('session.usage', () => {
    const u = usage()

    return 'deny' in u || 'value' in u ? u : { value: u }
  })
  on('session.start', ($, e) => ({ cwd: e.cwd }))
  on('command.register', ($, e) => {
    seen.commands.push(e.name)

    return { value: { command: e.name } }
  })
  on('ui.status', ($, e) => {
    seen.statuses.push(e.text)

    return { value: undefined }
  })
  on('ui.render', { component: 'AbovePrompt' }, ($, e) => {
    const { Text } = $.ui.resolve(e)

    return <Text key="engine">engine</Text>
  })

  return seen
}

async function start($: Engine) {
  await $.session.start({ cwd: '/work', surface: 'terminal', isInteractive: true })
}

async function texts($: Engine, surface: (typeof SURFACES)[number]) {
  const ui = await $.ui.mount({ plugin: 'caddie', surface, ...BAND })
  const all = (await ui.findAll({ type: 'Text' })).map(t => t.text)
  const boxes = await ui.findAll({ type: 'Box' })
  await ui.unmount()

  return { all, boxes }
}

describe('quota-bar band', () => {
  test('draws context and limits on track, on every surface', async ($, on) => {
    const seen = world(on, () => ON_TRACK)
    await start($)
    expect(seen.commands).toContain('quota')

    for (const surface of SURFACES) {
      const { all, boxes } = await texts($, surface)
      expect(all, surface).toContain('On track. You should reach Wednesday’s reset with room to spare.')
      expect(all, surface).toContain('Context 12% used')
      expect(all, surface).toContain('882k free of 1.0M')
      expect(all, surface).toContain('Messages')
      expect(all, surface).toContain('Autocompact buffer')
      expect(all, surface).not.toContain('Memory files')
      expect(all, surface).not.toContain('MCP tools')
      expect(all, surface).toContain('5 hour')
      expect(all, surface).toContain('Weekly')
      expect(all, surface).toContain('about 50% by reset – resets in 3h')
      expect(all, surface).toContain('about 70% by reset – resets in 2d 0h')
      expect(all.join('\n'), surface).not.toContain('·')
      expect(all.join('\n'), surface).not.toContain('█')

      for (const box of boxes) {
        const g = box.props.flexGrow
        if (g === undefined) continue
        expect(typeof g === 'number' && Number.isFinite(g) && g >= 1 && g <= 10_000, `flexGrow ${String(g)}`).toBe(true)
        expect(box.children.length, 'coloured Box has a Text child').toBeGreaterThan(0)
      }
    }
  })

  test('leads with the window that runs out', async ($, on) => {
    world(on, () =>
      usageWith([
        // 80% two hours into five: 200% projected, out 2h 30m before reset.
        { kind: 'five_hour', percentUsed: 80, resetsAt: iso(NOW + 3 * HOUR) },
        { kind: 'seven_day', percentUsed: 50, resetsAt: iso(NOW + 2 * DAY) },
      ]),
    )
    await start($)

    for (const surface of SURFACES) {
      const { all } = await texts($, surface)
      expect(all.some(t => /^At this pace you’ll run out before the \d{1,2}:\d{2} [AP]M reset\.$/.test(t)), surface).toBe(true)
      expect(all, surface).toContain('2h 30m before reset – resets in 3h')
    }
  })

  test('treats the first 3% of a window as on track', async ($, on) => {
    world(on, () => usageWith([{ kind: 'five_hour', percentUsed: 2, resetsAt: iso(NOW + 5 * HOUR - 60_000) }]))
    await start($)
    const { all } = await texts($, 'terminal')
    expect(all).toContain('on track – resets in 4h 59m')
    expect(all.some(t => t.startsWith('On track.'))).toBe(true)
  })

  test('says when a limit is reached', async ($, on) => {
    world(on, () =>
      usageWith([
        { kind: 'five_hour', percentUsed: 30, resetsAt: iso(NOW + 3 * HOUR) },
        { kind: 'seven_day', percentUsed: 100, resetsAt: iso(NOW + 2 * DAY) },
      ]),
    )
    await start($)

    for (const surface of SURFACES) {
      const { all } = await texts($, surface)
      expect(all.some(t => /^Limit reached\. Usage resumes at \d{1,2}:\d{2} [AP]M on Wednesday\.$/.test(t)), surface).toBe(true)
    }
  })

  test('/quota toggles the band and refreshes when turned on', async ($, on) => {
    let usage = ON_TRACK
    world(on, () => usage)
    await start($)
    const run = () =>
      $.command.run({
        command: 'quota',
        args: '',
        origin: { kind: 'composer' },
        presentation: { isFullscreen: false, columns: 100 },
      })

    expect((await run()).text).toBe('Quota bar off.')
    for (const surface of SURFACES) {
      const { all } = await texts($, surface)
      expect(all, surface).toEqual(['engine'])
    }

    usage = usageWith([{ kind: 'seven_day', percentUsed: 100, resetsAt: iso(NOW + 2 * DAY) }])
    expect((await run()).text).toBe('Quota bar on.')
    const { all } = await texts($, 'desktop')
    expect(all.some(t => t.startsWith('Limit reached.'))).toBe(true)
  })

  test('shows a failed refresh in the status line', async ($, on) => {
    const seen = world(on, () => ({ deny: 'usage unavailable' }))
    await start($)
    expect(seen.statuses).toContain('quota-bar: $.session.usage: usage unavailable')
    const { all } = await texts($, 'terminal')
    expect(all).toEqual(['engine'])
  })
})
