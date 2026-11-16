import { spawnSync } from 'node:child_process';
import { readdir, readFile } from 'node:fs/promises';
import { join } from 'node:path';

const readMarkdown = async (path) => {
  const text = await readFile(path, 'utf8');
  const match = text.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/);

  if (!match) {
    throw new Error(`Missing frontmatter: ${path}`);
  }

  const fields = Object.fromEntries(
    match[1].split(/\r?\n/).flatMap((line) => {
      const field = line.match(/^([\w-]+):\s*(.*)$/);

      if (!field) return [];

      const value = field[2].trim();

      return [[field[1], value.startsWith('"') ? JSON.parse(value) : value]];
    }),
  );

  return { ...fields, body: match[2], path };
};

const loadSkills = async (root) => {
  const entries = await readdir(join(root, 'skills'), { withFileTypes: true });

  return Promise.all(
    entries
      .filter((entry) => entry.isDirectory())
      .map((entry) =>
        readMarkdown(join(root, 'skills', entry.name, 'SKILL.md')),
      ),
  );
};

const sourceContext = (path, adapter, adapterPath) =>
  `Running in OpenCode. Host adapter source: ${adapterPath}. Resolve the adapter's links from that file.\n\n${adapter}\n\nShared instruction source: ${path}. Resolve the following workflow's relative links from that file, not the working directory.\n\n`;

export const hookPayload = (tool, args) => {
  switch (tool) {
    case 'shell':
      return { tool_input: { command: args.command }, tool_name: 'Bash' };
    case 'edit':
      return {
        tool_input: { file_path: args.path, new_string: args.newString },
        tool_name: 'Edit',
      };
    case 'write':
      return {
        tool_input: { content: args.content, file_path: args.path },
        tool_name: 'Write',
      };
    case 'patch':
      return {
        tool_input: { command: args.patchText },
        tool_name: 'apply_patch',
      };
    case 'skill':
      return { tool_input: { skill: args.id }, tool_name: 'Skill' };
    default:
      return undefined;
  }
};

export const runGuard = (root, directory, script, payload) => {
  const result = spawnSync('bash', [join(root, 'hooks', script)], {
    cwd: directory,
    encoding: 'utf8',
    input: JSON.stringify(payload),
    maxBuffer: 1024 * 1024,
    timeout: 5000,
  });

  if (result.error) {
    throw result.error;
  }

  if (result.status === 2) {
    return result.stderr.trim();
  }

  if (result.status !== 0) {
    throw new Error(`Caddie ${script} failed: ${result.stderr}`);
  }

  if (!result.stdout.trim()) {
    return undefined;
  }

  const decision = JSON.parse(result.stdout).hookSpecificOutput;

  if (decision?.permissionDecision === 'deny') {
    return decision.permissionDecisionReason.trim();
  }

  return undefined;
};

export const setupCaddie = async (ctx, root) => {
  for (const binary of ['bash', 'jq']) {
    const result = spawnSync(binary, ['--version'], {
      encoding: 'utf8',
      timeout: 5000,
    });

    if (result.error || result.status !== 0) {
      throw new Error(`Caddie requires ${binary} on PATH`);
    }
  }

  const { directory } = ctx.location;
  const adapterPath = join(root, 'references', 'opencode.md');

  const adapter = await readFile(adapterPath, 'utf8');
  const skills = await loadSkills(root);

  const agentFiles = (await readdir(join(root, 'agents'))).filter((name) =>
    name.endsWith('.md'),
  );

  const agents = await Promise.all(
    agentFiles.map((name) => readMarkdown(join(root, 'agents', name))),
  );

  await ctx.agent.transform((editor) => {
    for (const { name, description, path, body } of agents) {
      const id = name === 'caddie-agent' ? name : `caddie-${name}`;

      // OpenCode's update creates missing agents with the host's permission defaults.
      editor.update(id, (registered) => {
        registered.name = id;
        registered.description = description;
        registered.mode = 'subagent';
        registered.hidden = false;
        registered.system = sourceContext(path, adapter, adapterPath) + body;

        if (['code-reviewer', 'issue-filer'].includes(name)) {
          registered.permissions.push({
            action: 'edit',
            effect: 'deny',
            resource: '*',
          });
        }
      });
    }
  });

  await ctx.skill.transform((editor) => {
    for (const {
      name,
      description,
      path,
      body,
      'disable-model-invocation': disableModelInvocation,
    } of skills) {
      editor.add({
        autoinvoke: disableModelInvocation !== 'true',
        content: sourceContext(path, adapter, adapterPath) + body,
        description,
        id: `caddie-${name}`,
        name,
        path,
      });
    }
  });

  await ctx.command.transform((editor) => {
    for (const { name, description } of skills) {
      editor.add({
        description,
        execute: async ({ sessionID, prompt, delivery }) => {
          await ctx.session.prompt({
            ...prompt,
            delivery,
            sessionID,
            skills: [...(prompt.skills ?? []), { id: `caddie-${name}` }],
          });
        },
        name: `caddie-${name}`,
      });
    }
  });

  await ctx.tool.hook('execute.before', ({ input, tool }) => {
    const payload = hookPayload(tool, input);

    if (!payload) {
      return;
    }

    if (tool === 'shell') {
      const reason = runGuard(
        root,
        directory,
        'destructive-git-guard.sh',
        payload,
      );

      if (reason) {
        throw new Error(reason);
      }
    }
  });

  await ctx.tool.hook('execute.after', (event) => {
    if (
      event.status !== 'completed'
      || !['edit', 'write', 'patch'].includes(event.tool)
    )
      return;
    const payload = hookPayload(event.tool, event.input);
    const reasons = [
      ['suppression guard', 'suppression-guard.sh'],
      ['style guard', 'js-style-guard.sh'],
    ].flatMap(([label, script]) => {
      const reason = runGuard(root, directory, script, payload);
      return reason
        ? [`Caddie ${label} (the edit already happened):\n${reason}`]
        : [];
    });
    if (reasons.length === 0) return;
    const feedback = `\n\n${reasons.join('\n\n')}`;
    if (typeof event.result.content === 'string')
      event.result.content += feedback;
    else
      event.result.content = [
        ...(event.result.content ?? []),
        { text: feedback, type: 'text' },
      ];
  });
  await ctx.session.hook('context', (event) => {
    event.system.push({
      text: `Caddie OpenCode session ID: ${event.sessionID}. When indexing history, pass --exclude-session ${event.sessionID}.`,
      type: 'text',
    });
  });
};
