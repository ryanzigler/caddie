# Caddie mode and personal modes

Source: the user requested adaptations of pstack's poteto-mode and automate-me,
and confirmed the names caddie-mode and automate-me.

Goal: one explicit engineering entry point, a delegated-agent wrapper using the same
instructions, and a guided personal-mode generator for Claude Code and Codex.
Use existing Caddie workflows; preserve host discovery and permission boundaries.

1. Add shared mode instructions and playbooks using shipped skill references, with
   conversation persistence and opt-out. Add caddie-agent and Codex adapter mapping.
   Accept when routes resolve and neither host depends on Cursor tools or models.
2. Add automate-me, project-scoped history mining, update semantics, interview, and
   a mode skeleton. Accept when unavailable history still permits interviewing,
   unsupported preferences need confirmation, and both invocation policies agree.
3. Update README and synchronized manifests, preserve upstream licenses. Run
   `python3 -m unittest discover -s tests -v` and `python3 tests/smoke_codex.py`.
   Review the diff and validate local links. Loader discovery is not behavior proof;
   a fresh installed session must exercise realistic mode and generator requests.

Progress: all three implementation tasks complete. Changes are uncommitted for review.

Validation:

- `python3 -m unittest discover -s tests -v`: all 16 tests passed. The independent
  reviewer reran the suite with the same result and found no actionable defects.
- `python3 tests/smoke_codex.py`: a temporary installation discovered all 35 skills
  with no loader errors, including both new explicit-only skills.
- `claude plugin validate . --strict`: passed.
- `claude plugin validate .claude-plugin/plugin.json`: passed with the expected
  existing warning about root CLAUDE.md not shipping as plugin context.
- Local link checks passed for the seven mode/agent/adapter documents;
  `git diff --check` passed. No Cursor tools, paths, or model slugs remain in the
  adapted instructions.
- Fresh Claude CLI sessions loaded the working plugin with `--plugin-dir` in an
  isolated `/tmp` fixture. A caddie-mode investigation answered from its README,
  respected read-only scope, and did not delegate. An automate-me request with
  explicit preferences and declined history created alex-mode at an explicit
  fixture destination. The generated file retained all four preferences, explicit
  invocation, and conversation opt-out.
- The first generator attempt could not write Claude's protected `.claude/skills`
  directory with noninteractive permission prompts disabled. It reported the denial
  accurately. The successful check used an ordinary explicit fixture destination;
  protected-directory installation was not tested.

Behavior limits: these fresh Claude sessions used session-local plugin loading,
not the installed marketplace cache. Multi-turn persistence, mined history,
interactive interview rounds, and Codex generator behavior were not exercised.
The transcript reader's scoping is covered by the compatibility suite. No normal
installed plugin cache was refreshed, and no publishing or integration was requested.
