import assert from 'node:assert/strict';
import { mkdtemp, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';
import { hookPayload, setupCaddie } from '../opencode/runtime.mjs';

const root = fileURLToPath(new URL('../', import.meta.url));

const fixture = async () => {
  const directory = await mkdtemp(join(tmpdir(), 'caddie-opencode-unit-'));
  const skills = new Map();
  const agents = new Map();
  const commands = new Map();
  const hooks = new Map();
  const prompts = [];
  const context = {
    agent: {
      transform: async (callback) =>
        callback({
          update: (id, update) => {
            if (!agents.has(id)) agents.set(id, { id, permissions: [] });
            update(agents.get(id));
          },
        }),
    },
    command: {
      transform: async (callback) =>
        callback({ add: (command) => commands.set(command.name, command) }),
    },
    location: { directory },
    session: {
      hook: async (name, callback) => hooks.set(`session.${name}`, callback),
      prompt: async (input) => prompts.push(input),
    },
    skill: {
      transform: async (callback) =>
        callback({ add: (skill) => skills.set(skill.id, skill) }),
    },
    tool: { hook: async (name, callback) => hooks.set(name, callback) },
  };
  await setupCaddie(context, root);
  return { agents, commands, directory, hooks, prompts, skills };
};

test('registers shared skills with native explicit-only policy and real source paths', async (t) => {
  const f = await fixture();
  t.after(() => rm(f.directory, { force: true, recursive: true }));
  assert.ok(f.skills.size > 0);
  assert.equal(f.skills.get('caddie-how').autoinvoke, true);
  assert.equal(f.skills.get('caddie-recall').autoinvoke, false);
  assert.equal(f.skills.get('caddie-caddie-mode').autoinvoke, false);
  const skill = f.skills.get('caddie-how');
  assert.ok(
    skill.content.includes(
      (await readFile(skill.path, 'utf8')).split('---')[2].trim(),
    ),
  );
  assert.match(skill.content, /Running Caddie in OpenCode/);
});

test('registers native agents directly from shared bodies with host permissions', async (t) => {
  const f = await fixture();
  t.after(() => rm(f.directory, { force: true, recursive: true }));
  assert.equal(f.agents.size, 5);
  const reviewer = f.agents.get('caddie-code-reviewer');
  assert.equal(reviewer.mode, 'subagent');
  assert.match(reviewer.system, /# Code reviewer/);
  assert.match(reviewer.system, /Running Caddie in OpenCode/);
  assert.deepEqual(reviewer.permissions, [
    { action: 'edit', effect: 'deny', resource: '*' },
  ]);
  assert.equal(f.agents.get('caddie-code-simplifier').model, undefined);
});

test('explicit commands submit shared body and preserve attachments and delivery', async (t) => {
  const f = await fixture();
  t.after(() => rm(f.directory, { force: true, recursive: true }));
  const prompt = {
    files: [{ uri: 'file:///test.txt' }],
    text: 'target $(do-not-execute)',
  };
  await f.commands
    .get('caddie-recall')
    .execute({ delivery: 'queue', prompt, sessionID: 'ses_test' });
  assert.equal(f.prompts.length, 1);
  assert.equal(f.prompts[0].sessionID, 'ses_test');
  assert.equal(f.prompts[0].delivery, 'queue');
  assert.deepEqual(f.prompts[0].files, prompt.files);
  assert.deepEqual(f.prompts[0].skills, [{ id: 'caddie-recall' }]);
  assert.equal(f.prompts[0].text, prompt.text);
});

test('shell guard rejects destructive input before execution and permits ordinary commands', async (t) => {
  const f = await fixture();
  t.after(() => rm(f.directory, { force: true, recursive: true }));
  const before = f.hooks.get('execute.before');
  assert.throws(
    () => before({ input: { command: 'git stash' }, tool: 'shell' }),
    /Blocked/,
  );
  assert.throws(
    () =>
      before({
        input: { command: 'git push --force-with-lease' },
        tool: 'shell',
      }),
    /Blocked/,
  );
  before({ input: { command: 'git status --short' }, tool: 'shell' });
});

test('edit, write, and patch add correction feedback only after successful suppression additions', async (t) => {
  const f = await fixture();
  t.after(() => rm(f.directory, { force: true, recursive: true }));
  const after = f.hooks.get('execute.after');
  for (const [tool, input] of [
    ['edit', { newString: '// @ts-ignore\ncall()', path: 'edit.ts' }],
    ['write', { content: '// biome-ignore lint\ncall()', path: 'write.ts' }],
    [
      'patch',
      {
        patchText:
          '*** Begin Patch\n*** Add File: patch.ts\n+// @ts-expect-error\n*** End Patch',
      },
    ],
  ]) {
    const event = {
      input,
      result: { content: 'Written', output: { intact: true } },
      status: 'completed',
      tool,
    };
    after(event);
    assert.match(event.result.content, /fix the cause/);
    assert.deepEqual(event.result.output, { intact: true });
  }
  const clean = {
    input: { newString: 'call()', path: 'a.ts' },
    result: { content: 'Written' },
    status: 'completed',
    tool: 'edit',
  };
  after(clean);
  assert.equal(clean.result.content, 'Written');
  const failed = {
    error: { message: 'Denied' },
    input: { content: '// @ts-ignore', path: 'a.ts' },
    status: 'error',
    tool: 'write',
  };
  after(failed);
  assert.equal(failed.error.message, 'Denied');
  const removed = {
    input: {
      patchText:
        '*** Begin Patch\n*** Update File: a.ts\n@@\n-// @ts-ignore\n+call()\n*** End Patch',
    },
    result: { content: 'Written' },
    status: 'completed',
    tool: 'patch',
  };
  after(removed);
  assert.equal(removed.result.content, 'Written');
});

test('edits that break the JS/TS style get style feedback alongside suppression feedback', async (t) => {
  const f = await fixture();
  t.after(() => rm(f.directory, { force: true, recursive: true }));
  const after = f.hooks.get('execute.after');
  const style = {
    input: { content: 'var count = 0', path: 'a.ts' },
    result: { content: 'Written' },
    status: 'completed',
    tool: 'write',
  };
  after(style);
  assert.match(style.result.content, /Caddie style guard[\s\S]*a\.ts: var:/);
  assert.doesNotMatch(style.result.content, /suppression guard/);
  const both = {
    input: { newString: '// @ts-ignore\nitems.forEach(run)', path: 'b.ts' },
    result: { content: 'Written' },
    status: 'completed',
    tool: 'edit',
  };
  after(both);
  assert.match(
    both.result.content,
    /suppression guard[\s\S]*fix the cause[\s\S]*style guard[\s\S]*\.forEach:/,
  );
  const prose = {
    input: { content: 'var count = 0', path: 'notes.md' },
    result: { content: 'Written' },
    status: 'completed',
    tool: 'write',
  };
  after(prose);
  assert.equal(prose.result.content, 'Written');
});

test('structured tool content receives feedback without losing its original content', async (t) => {
  const f = await fixture();
  t.after(() => rm(f.directory, { force: true, recursive: true }));
  const event = {
    input: { content: '// @ts-ignore', path: 'a.ts' },
    result: { content: [{ text: 'Original', type: 'text' }] },
    status: 'completed',
    tool: 'write',
  };
  f.hooks.get('execute.after')(event);
  assert.equal(event.result.content[0].text, 'Original');
  assert.match(event.result.content[1].text, /fix the cause/);
});

test('unrelated tools are ignored and current session ID is available for history exclusion', async (t) => {
  const f = await fixture();
  t.after(() => rm(f.directory, { force: true, recursive: true }));
  assert.equal(hookPayload('custom_tool', {}), undefined);
  f.hooks.get('execute.before')({ input: {}, tool: 'custom_tool' });
  const event = { sessionID: 'ses_current', system: [] };
  f.hooks.get('session.context')(event);
  assert.match(event.system[0].text, /--exclude-session ses_current/);
});
