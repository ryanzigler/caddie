import type { EngineInterface, Register } from 'claude-code';
import { atom, read, update } from 'claude-code';
import type {
  QuotaCategory,
  QuotaContext,
  QuotaLimit,
  QuotaSnapshot,
} from '../types';

const snapshot = atom({ key: 'snapshot', plugin: 'caddie' } as const, null);
const isOn = atom({ key: 'isOn', plugin: 'caddie' } as const, true);

const PALETTE = [
  '#a78bfa',
  '#60a5fa',
  '#f472b6',
  '#34d399',
  '#fbbf24',
  '#fb923c',
  '#22d3ee',
  '#c084fc',
];
const MUTED = '#8b90a0';
const GREEN = '#4ade80';
const AMBER = '#fbbf24';
const RED = '#f87171';
const FREE = '#3f4452';
const BUFFER = '#6b7080';
const TRACK = '#2e3240';

const SEP = ' – ';
const LIMIT_CELLS = 16;
const GROW_SCALE = 1000;
const LEGEND_MIN_SHARE = 0.003;
const EARLY_SHARE = 0.03;

const HOUR = 3_600_000;
const DAY = 24 * HOUR;

const WINDOWS: Record<string, { label: string; ms: number }> = {
  five_hour: { label: '5 hour', ms: 5 * HOUR },
  seven_day: { label: 'Weekly', ms: 7 * DAY },
};

type Severity = 'ok' | 'amber' | 'red';

type Forecast =
  | { state: 'unknown' }
  | { state: 'hit'; resetsAt: number }
  | { state: 'early'; resetsAt: number }
  | { state: 'track'; resetsAt: number; projected: number }
  | { state: 'out'; resetsAt: number; runOutAt: number; severity: Severity };

const COLOR: Record<Severity, string> = { amber: AMBER, ok: GREEN, red: RED };

function forecast(
  { kind, resetsAt, percentUsed }: QuotaLimit,
  now: number,
): Forecast {
  const window = WINDOWS[kind];
  const resetsAtDate = resetsAt === null ? NaN : Date.parse(resetsAt);

  if (window === undefined || !Number.isFinite(resetsAtDate)) {
    return { state: 'unknown' };
  }

  if (percentUsed >= 100) {
    return { resetsAt: resetsAtDate, state: 'hit' };
  }

  const elapsed = window.ms - (resetsAtDate - now);

  if (elapsed < window.ms * EARLY_SHARE) {
    return { resetsAt: resetsAtDate, state: 'early' };
  }

  const rate = percentUsed / elapsed;
  const projected = percentUsed + rate * (resetsAtDate - now);

  if (projected < 100) {
    return { projected, resetsAt: resetsAtDate, state: 'track' };
  }

  return {
    resetsAt: resetsAtDate,
    runOutAt: now + (100 - percentUsed) / rate,
    severity: projected > 130 ? 'red' : 'amber',
    state: 'out',
  };
}

function severityOf(forecast: Forecast): Severity {
  if (forecast.state === 'hit') {
    return 'red';
  }

  return forecast.state === 'out' ? forecast.severity : 'ok';
}

const duration = (ms: number) => {
  const minutes = Math.max(0, Math.round(ms / 60_000));
  const days = Math.floor(minutes / 1440);
  const hours = Math.floor((minutes % 1440) / 60);
  const mins = minutes % 60;

  if (days > 0) {
    return `${days}d ${hours}h`;
  }

  if (hours > 0) {
    return mins === 0 ? `${hours}h` : `${hours}h ${mins}m`;
  }

  return `${mins}m`;
};

const TIME = new Intl.DateTimeFormat('en-US', {
  hour: 'numeric',
  minute: '2-digit',
});

const WEEKDAY = new Intl.DateTimeFormat('en-US', { weekday: 'long' });

const DAY_KEY = new Intl.DateTimeFormat('en-US', {
  day: '2-digit',
  month: '2-digit',
  year: 'numeric',
});

const isSameDay = (a: number, b: number) =>
  DAY_KEY.format(a) === DAY_KEY.format(b);

const resetPhrase = (at: number, now: number) =>
  isSameDay(at, now)
    ? `the ${TIME.format(at)} reset`
    : `${WEEKDAY.format(at)}'s reset`;

const resumePhrase = (at: number, now: number) =>
  isSameDay(at, now)
    ? TIME.format(at)
    : `${TIME.format(at)} on ${WEEKDAY.format(at)}`;

function tokens(n: number): string {
  if (n >= 1_000_000) {
    return `${(n / 1_000_000).toFixed(1)}M`;
  }

  if (n >= 10_000) {
    return `${Math.round(n / 1000)}k`;
  }

  if (n >= 1000) {
    return `${(n / 1000).toFixed(1)}k`;
  }

  return String(Math.round(n));
}

const grow = (share: number) =>
  Math.min(GROW_SCALE, Math.max(1, Math.round(share * GROW_SCALE)));

interface Headline {
  color: string;
  text: string;
}

function headline(limits: QuotaLimit[], now: number): Headline | null {
  const rows = limits.map((limit) => ({
    forecast: forecast(limit, now),
    limit,
  }));

  const hit = rows.flatMap(({ forecast }) =>
    forecast.state === 'hit' ? [forecast.resetsAt] : [],
  );

  if (hit.length > 0) {
    return {
      color: RED,
      text: `Limit reached. Usage resumes at ${resumePhrase(Math.max(...hit), now)}.`,
    };
  }

  const [out] = rows
    .flatMap(({ forecast }) => (forecast.state === 'out' ? [forecast] : []))
    .sort((a, b) => a.runOutAt - b.runOutAt);

  if (out !== undefined) {
    return {
      color: COLOR[out.severity],
      text: `At this pace you'll run out before ${resetPhrase(out.resetsAt, now)}.`,
    };
  }
  const lead =
    rows.find(({ limit: { kind } }) => kind === 'seven_day') ?? rows[0];

  if (lead === undefined || lead.forecast.state === 'unknown') {
    return null;
  }

  return {
    color: GREEN,
    text: `On track. You should reach ${resetPhrase(lead.forecast.resetsAt, now)} with room to spare.`,
  };
}

function limitNote(forecast: Forecast, now: number) {
  switch (forecast.state) {
    case 'unknown':
      return '';
    case 'hit':
      return `limit reached${SEP}resets in ${duration(forecast.resetsAt - now)}`;
    case 'early':
      return `on track${SEP}resets in ${duration(forecast.resetsAt - now)}`;
    case 'track':
      return `about ${Math.round(forecast.projected)}% by reset${SEP}resets in ${duration(forecast.resetsAt - now)}`;
    case 'out':
      return `${duration(forecast.resetsAt - forecast.runOutAt)} before reset${SEP}resets in ${duration(forecast.resetsAt - now)}`;
  }
}

function fillColor(percent: number) {
  if (percent >= 90) {
    return RED;
  }

  return percent >= 70 ? AMBER : GREEN;
}

async function measure($: EngineInterface): Promise<QuotaSnapshot> {
  const usage = await $.session.usage({ breakdown: 'summary' });
  const takenAt = await $.clock.now();
  const { breakdown } = usage.context;

  let context: QuotaContext | null = null;

  if (breakdown !== undefined && breakdown.rawMaxTokens > 0) {
    const categories: QuotaCategory[] = breakdown.categories.flatMap(
      ({ kind, name, tokens }) =>
        kind === 'deferred' || tokens <= 0 ? [] : [{ kind, name, tokens }],
    );

    context = {
      categories,
      free: Math.max(0, breakdown.rawMaxTokens - breakdown.totalTokens),
      percent: breakdown.percentage,
      window: breakdown.rawMaxTokens,
    };
  } else if (usage.context.tokens !== undefined && usage.context.window > 0) {
    const { tokens: used, window } = usage.context;

    context = {
      categories: [
        { kind: 'used', name: 'Used', tokens: used },
        {
          kind: 'free',
          name: 'Free space',
          tokens: Math.max(0, window - used),
        },
      ],
      free: Math.max(0, window - used),
      percent: usage.context.percent ?? Math.round((used / window) * 100),
      window,
    };
  }
  const rateLimits: QuotaLimit[] = usage.rateLimits.map(
    ({ kind, percentUsed, resetsAt }) => ({
      kind,
      percentUsed,
      resetsAt: resetsAt ?? null,
    }),
  );

  return { context, rateLimits, takenAt };
}

let hasError = false;

function errorText(error: unknown): string {
  const message = error instanceof Error ? error.message : String(error);

  return `quota-bar: ${message.replace(/^caddie: /, '')}`;
}

async function refresh($: EngineInterface): Promise<void> {
  if (!(await read($, isOn))) {
    return;
  }

  try {
    const next = await measure($);
    await update($, snapshot, () => next);

    if (hasError) {
      hasError = false;
      $.ui.status(undefined);
    }
  } catch (error) {
    hasError = true;
    $.ui.status(errorText(error));
  }
}

export const register: Register = (on) => {
  on('session.start', async ($, e, next) => {
    try {
      await $.command.register({
        description: 'Show or hide the quota bar above the prompt',
        name: 'quota',
      });
    } catch (error) {
      $.ui.status(errorText(error));
    }

    await refresh($);

    return next(e);
  });

  on('session.measure', async ($, e, next) => {
    await refresh($);

    return next(e);
  });

  on('turn.complete', async ($, e, next) => {
    const result = await next(e);
    await refresh($);

    return result;
  });

  on('command.run', { command: 'quota' }, async ($) => {
    const showing = !(await read($, isOn));

    await update($, isOn, () => showing);

    if (showing) {
      await refresh($);
    }

    return { text: showing ? 'Quota bar on.' : 'Quota bar off.' };
  });

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (e.props.hasSurvey || !(await read($, isOn))) {
      return next(e);
    }

    const snap = await read($, snapshot);

    if (
      snap === null
      || (snap.context === null && snap.rateLimits.length === 0)
    ) {
      return next(e);
    }

    const { Box, Text } = $.ui.resolve(e);
    const now = snap.takenAt;
    const head = headline(snap.rateLimits, now);
    const ctx = snap.context;

    let paletteIndex = 0;

    const colored = (ctx?.categories ?? []).map((category) => {
      const color =
        category.kind === 'free'
          ? FREE
          : category.kind === 'buffer'
            ? BUFFER
            : PALETTE[paletteIndex++ % PALETTE.length];

      return { ...category, color };
    });

    const legend =
      ctx === null
        ? []
        : colored.filter(
            ({ tokens }) => tokens / ctx.window >= LEGEND_MIN_SHARE,
          );

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
              <Box
                key={`seg-${i}`}
                flexGrow={grow(c.tokens / ctx.window)}
                backgroundColor={c.color}
              >
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
        {snap.rateLimits.map((limit) => {
          const forecastedLimit = forecast(limit, now);
          const color = COLOR[severityOf(forecastedLimit)];

          const filled = Math.round(
            (Math.min(100, Math.max(0, limit.percentUsed)) / 100) * LIMIT_CELLS,
          );

          const label = WINDOWS[limit.kind]?.label ?? limit.kind;
          const note = limitNote(forecastedLimit, now);

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
          );
        })}
      </Box>
    );
  });
};
