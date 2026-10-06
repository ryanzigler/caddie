import assert from 'node:assert/strict'
import { mkdtemp, readFile, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'
import test from 'node:test'
import { hookPayload, setupCaddie } from '../opencode/runtime.mjs'

const root = fileURLToPath(new URL('../', import.meta.url))

const fixture = async () => {
  const directory = await mkdtemp(join(tmpdir(), 'caddie-opencode-unit-'))
  const skills = new Map()
  const agents = new Map()
  const commands = new Map()
  const hooks = new Map()
  const prompts = []
  const context = {
    location: { directory },
    agent: { transform: async (callback) => callback({
      update: (id, update) => {
        if (!agents.has(id)) agents.set(id, { id, permissions: [] })
        update(agents.get(id))
      },
    }) },
    skill: { transform: async (callback) => callback({ add: (skill) => skills.set(skill.id, skill) }) },
    command: { transform: async (callback) => callback({ add: (command) => commands.set(command.name, command) }) },
    tool: { hook: async (name, callback) => hooks.set(name, callback) },
    session: {
      prompt: async (input) => prompts.push(input),
      hook: async (name, callback) => hooks.set(`session.${name}`, callback),
    },
  }
  await setupCaddie(context, root)
  return { directory, skills, agents, commands, hooks, prompts }
}

test('registers shared skills with native explicit-only policy and real source paths', async (t) => {
  const f = await fixture()
  t.after(() => rm(f.directory, { recursive: true, force: true }))
  assert.ok(f.skills.size > 0)
  assert.equal(f.skills.get('caddie-how').autoinvoke, true)
  assert.equal(f.skills.get('caddie-recall').autoinvoke, false)
  assert.equal(f.skills.get('caddie-caddie-mode').autoinvoke, false)
  const skill = f.skills.get('caddie-how')
  assert.ok(skill.content.includes((await readFile(skill.path, 'utf8')).split('---')[2].trim()))
  assert.match(skill.content, /Running Caddie in OpenCode/)
})

test('registers native agents directly from shared bodies with host permissions', async (t) => {
  const f = await fixture()
  t.after(() => rm(f.directory, { recursive: true, force: true }))
  assert.equal(f.agents.size, 5)
  const reviewer = f.agents.get('caddie-code-reviewer')
  assert.equal(reviewer.mode, 'subagent')
  assert.match(reviewer.system, /# Code reviewer/)
  assert.match(reviewer.system, /Running Caddie in OpenCode/)
  assert.deepEqual(reviewer.permissions, [{ action: 'edit', resource: '*', effect: 'deny' }])
  assert.equal(f.agents.get('caddie-code-simplifier').model, undefined)
})

test('explicit commands submit shared body and preserve attachments and delivery', async (t) => {
  const f = await fixture()
  t.after(() => rm(f.directory, { recursive: true, force: true }))
  const prompt = { text: 'target $(do-not-execute)', files: [{ uri: 'file:///test.txt' }] }
  await f.commands.get('caddie-recall').execute({ sessionID: 'ses_test', prompt, delivery: 'queue' })
  assert.equal(f.prompts.length, 1)
  assert.equal(f.prompts[0].sessionID, 'ses_test')
  assert.equal(f.prompts[0].delivery, 'queue')
  assert.deepEqual(f.prompts[0].files, prompt.files)
  assert.deepEqual(f.prompts[0].skills, [{ id: 'caddie-recall' }])
  assert.equal(f.prompts[0].text, prompt.text)
})

test('shell guard rejects destructive input before execution and permits ordinary commands', async (t) => {
  const f = await fixture()
  t.after(() => rm(f.directory, { recursive: true, force: true }))
  const before = f.hooks.get('execute.before')
  assert.throws(() => before({ tool: 'shell', input: { command: 'git stash' } }), /Blocked/)
  assert.throws(() => before({ tool: 'shell', input: { command: 'git push --force-with-lease' } }), /Blocked/)
  before({ tool: 'shell', input: { command: 'git status --short' } })
})

test('edit, write, and patch add correction feedback only after successful suppression additions', async (t) => {
  const f = await fixture()
  t.after(() => rm(f.directory, { recursive: true, force: true }))
  const after = f.hooks.get('execute.after')
  for (const [tool, input] of [
    ['edit', { path: 'edit.ts', newString: '// @ts-ignore\ncall()' }],
    ['write', { path: 'write.ts', content: '// biome-ignore lint\ncall()' }],
    ['patch', { patchText: '*** Begin Patch\n*** Add File: patch.ts\n+// @ts-expect-error\n*** End Patch' }],
  ]) {
    const event = { tool, input, status: 'completed', result: { content: 'Written', output: { intact: true } } }
    after(event)
    assert.match(event.result.content, /fix the cause/)
    assert.deepEqual(event.result.output, { intact: true })
  }
  const clean = { tool: 'edit', input: { path: 'a.ts', newString: 'call()' }, status: 'completed', result: { content: 'Written' } }
  after(clean)
  assert.equal(clean.result.content, 'Written')
  const failed = { tool: 'write', input: { path: 'a.ts', content: '// @ts-ignore' }, status: 'error', error: { message: 'Denied' } }
  after(failed)
  assert.equal(failed.error.message, 'Denied')
  const removed = { tool: 'patch', input: { patchText: '*** Begin Patch\n*** Update File: a.ts\n@@\n-// @ts-ignore\n+call()\n*** End Patch' }, status: 'completed', result: { content: 'Written' } }
  after(removed)
  assert.equal(removed.result.content, 'Written')
})

test('structured tool content receives feedback without losing its original content', async (t) => {
  const f = await fixture()
  t.after(() => rm(f.directory, { recursive: true, force: true }))
  const event = { tool: 'write', input: { path: 'a.ts', content: '// @ts-ignore' }, status: 'completed', result: { content: [{ type: 'text', text: 'Original' }] } }
  f.hooks.get('execute.after')(event)
  assert.equal(event.result.content[0].text, 'Original')
  assert.match(event.result.content[1].text, /fix the cause/)
})

test('retired skill routing uses the OpenCode replacement ID', async (t) => {
  const f = await fixture()
  t.after(() => rm(f.directory, { recursive: true, force: true }))
  const before = f.hooks.get('execute.before')
  for (const id of ['caddie-unslop', 'humanize-writing', 'anthropic-skills:cro-metrics-writing']) {
    assert.throws(() => before({ tool: 'skill', input: { id } }), /caddie-ryan-voice-guide/)
  }
  before({ tool: 'skill', input: { id: 'caddie-how' } })
})

test('unrelated tools are ignored and current session ID is available for history exclusion', async (t) => {
  const f = await fixture()
  t.after(() => rm(f.directory, { recursive: true, force: true }))
  assert.equal(hookPayload('custom_tool', {}), undefined)
  f.hooks.get('execute.before')({ tool: 'custom_tool', input: {} })
  const event = { sessionID: 'ses_current', system: [] }
  f.hooks.get('session.context')(event)
  assert.match(event.system[0].text, /--exclude-session ses_current/)
})
