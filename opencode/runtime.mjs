import { readFile, readdir } from 'node:fs/promises'
import { join } from 'node:path'
import { spawnSync } from 'node:child_process'

const readMarkdown = async (path) => {
  const text = await readFile(path, 'utf8')
  const match = text.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/)
  if (!match) throw new Error(`Missing frontmatter: ${path}`)
  const fields = Object.fromEntries(match[1].split(/\r?\n/).flatMap((line) => {
    const field = line.match(/^([\w-]+):\s*(.*)$/)
    if (!field) return []
    const value = field[2].trim()
    return [[field[1], value.startsWith('"') ? JSON.parse(value) : value]]
  }))
  return { ...fields, body: match[2], path }
}

const loadSkills = async (root) => {
  const entries = await readdir(join(root, 'skills'), { withFileTypes: true })
  return Promise.all(entries.filter((entry) => entry.isDirectory()).map((entry) =>
    readMarkdown(join(root, 'skills', entry.name, 'SKILL.md'))))
}

const sourceContext = (path, adapter, adapterPath) =>
  `Running in OpenCode. Host adapter source: ${adapterPath}. Resolve the adapter's links from that file.\n\n${adapter}\n\nShared instruction source: ${path}. Resolve the following workflow's relative links from that file, not the working directory.\n\n`

export const hookPayload = (tool, args) => {
  switch (tool) {
    case 'shell': return { tool_name: 'Bash', tool_input: { command: args.command } }
    case 'edit': return { tool_name: 'Edit', tool_input: { file_path: args.path, new_string: args.newString } }
    case 'write': return { tool_name: 'Write', tool_input: { file_path: args.path, content: args.content } }
    case 'patch': return { tool_name: 'apply_patch', tool_input: { command: args.patchText } }
    case 'skill': return { tool_name: 'Skill', tool_input: { skill: args.id } }
    default: return undefined
  }
}

export const runGuard = (root, directory, script, payload) => {
  const result = spawnSync('bash', [join(root, 'hooks', script)], {
    cwd: directory,
    input: JSON.stringify(payload),
    encoding: 'utf8',
    timeout: 5000,
    maxBuffer: 1024 * 1024,
  })
  if (result.error) throw result.error
  if (result.status === 2) return result.stderr.trim()
  if (result.status !== 0) throw new Error(`Caddie ${script} failed: ${result.stderr}`)
  if (!result.stdout.trim()) return undefined
  const decision = JSON.parse(result.stdout).hookSpecificOutput
  if (decision?.permissionDecision === 'deny') return decision.permissionDecisionReason.trim()
  return undefined
}

const retiredNames = {
  unslop: 'caddie:unslop',
  'humanize-writing': 'anthropic-skills:humanize-writing',
  'cro-metrics-writing': 'anthropic-skills:cro-metrics-writing',
}

export const setupCaddie = async (ctx, root) => {
  for (const binary of ['bash', 'jq']) {
    const result = spawnSync(binary, ['--version'], { encoding: 'utf8', timeout: 5000 })
    if (result.error || result.status !== 0) throw new Error(`Caddie requires ${binary} on PATH`)
  }
  const directory = ctx.location.directory
  const adapterPath = join(root, 'references', 'opencode.md')
  const adapter = await readFile(adapterPath, 'utf8')
  const skills = await loadSkills(root)
  const agentFiles = (await readdir(join(root, 'agents'))).filter((name) => name.endsWith('.md'))
  const agents = await Promise.all(agentFiles.map((name) => readMarkdown(join(root, 'agents', name))))
  await ctx.agent.transform((editor) => {
    for (const agent of agents) {
      const id = agent.name === 'caddie-agent' ? agent.name : `caddie-${agent.name}`
      // OpenCode's update creates missing agents with the host's permission defaults.
      editor.update(id, (registered) => {
        registered.name = id
        registered.description = agent.description
        registered.mode = 'subagent'
        registered.hidden = false
        registered.system = sourceContext(agent.path, adapter, adapterPath) + agent.body
        if (['code-reviewer', 'issue-filer'].includes(agent.name)) {
          registered.permissions.push({ action: 'edit', resource: '*', effect: 'deny' })
        }
      })
    }
  })
  await ctx.skill.transform((editor) => {
    for (const skill of skills) {
      editor.add({
        id: `caddie-${skill.name}`,
        name: skill.name,
        description: skill.description,
        path: skill.path,
        content: sourceContext(skill.path, adapter, adapterPath) + skill.body,
        autoinvoke: skill['disable-model-invocation'] !== 'true',
      })
    }
  })
  await ctx.command.transform((editor) => {
    for (const skill of skills) {
      editor.add({
        name: `caddie-${skill.name}`,
        description: skill.description,
        execute: async ({ sessionID, prompt, delivery }) => {
          await ctx.session.prompt({
            ...prompt,
            sessionID,
            skills: [...(prompt.skills ?? []), { id: `caddie-${skill.name}` }],
            delivery,
          })
        },
      })
    }
  })
  await ctx.tool.hook('execute.before', (event) => {
    const payload = hookPayload(event.tool, event.input)
    if (!payload) return
    if (event.tool === 'shell') {
      const reason = runGuard(root, directory, 'destructive-git-guard.sh', payload)
      if (reason) throw new Error(reason)
    }
    if (event.tool === 'skill') {
      const name = event.input.id
      payload.tool_input.skill = retiredNames[name.replace(/^caddie-/, '')] ?? name
      const reason = runGuard(root, directory, 'retired-skill-redirect.sh', payload)
      if (reason) throw new Error(reason.replaceAll('caddie:ryan-voice-guide', 'caddie-ryan-voice-guide')
        .replaceAll('Skill tool', 'skill tool').replaceAll('skill:', 'id:'))
    }
  })
  await ctx.tool.hook('execute.after', (event) => {
    if (event.status !== 'completed' || !['edit', 'write', 'patch'].includes(event.tool)) return
    const reason = runGuard(root, directory, 'suppression-guard.sh', hookPayload(event.tool, event.input))
    if (!reason) return
    const feedback = `\n\nCaddie suppression guard (the edit already happened):\n${reason}`
    if (typeof event.result.content === 'string') event.result.content += feedback
    else event.result.content = [...(event.result.content ?? []), { type: 'text', text: feedback }]
  })
  await ctx.session.hook('context', (event) => {
    event.system.push({ type: 'text', text: `Caddie OpenCode session ID: ${event.sessionID}. When indexing history, pass --exclude-session ${event.sessionID}.` })
  })
}
