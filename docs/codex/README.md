# Codex Operator's Guide

> **🍴 Fork notice:** This repository is a **vibe-coded fork** of
> [Claude Code Game Studios](https://github.com/Donchitos/Claude-Code-Game-Studios)
> (original by Donchitos). The conversion from Claude Code → OpenAI Codex CLI
> was performed by Claude itself in a single migration session — see
> [`../superpowers/plans/2026-05-17-codex-migration.md`](../superpowers/plans/2026-05-17-codex-migration.md).
> Everything under `.codex/` was mechanically derived from the original
> `.claude/` tree via [`../../tools/migration/convert_claude_to_codex.py`](../../tools/migration/convert_claude_to_codex.py).

This repository was originally built for Claude Code and is now primarily
supported under [OpenAI Codex CLI](https://github.com/openai/codex). Codex is
the recommended path going forward; the legacy `.claude/` tree still works for
contributors who prefer Claude Code.

## Install

```bash
npm install -g @openai/codex
# or, on macOS:
brew install --cask codex
```

You also need an OpenAI API key with Codex access:

```bash
export OPENAI_API_KEY=sk-...
```

## First run

```bash
cd Codex-Code-Game-Studios
codex
```

On startup, Codex:

1. Reads `AGENTS.md` for project instructions.
2. Loads `.codex/config.toml` (sandbox, approval policy, project prompts).
3. Runs `.codex/hooks/session-start.sh` which prints branch/sprint/milestone
   context and chains `detect-gaps.sh`.
4. Exposes 73 skill prompts (`/start`, `/brainstorm`, `/dev-story`, …) and
   49 persona wrappers (`/agent-game-designer`, `/agent-godot-specialist`, …).

Type `/` to browse the prompt catalogue.

## Git hooks (one-time, per clone)

The pre-commit and pre-push validators are not auto-installed — symlink them:

```bash
ln -s ../../.codex/hooks/validate-commit.sh .git/hooks/pre-commit
ln -s ../../.codex/hooks/validate-push.sh   .git/hooks/pre-push
chmod +x .git/hooks/pre-commit .git/hooks/pre-push
```

On Windows, create thin `.bat`/`bash` wrappers under `.git/hooks/` that call
the scripts; symlinks may not work without developer mode.

## Personas vs prompts

- **Slash prompts** under `.codex/prompts/<slug>.md` are workflow tools
  (`/dev-story`, `/architecture-review`, …). They drive a step-by-step process.
- **Persona wrappers** under `.codex/prompts/agent-<slug>.md` instruct Codex
  to adopt the persona body from `.codex/personas/<slug>.md`. Use them when
  you want domain expertise (e.g. `/agent-game-designer` for mechanics design,
  `/agent-godot-shader-specialist` for GLSL questions).

## Hook mapping

See [hook-mapping.md](hook-mapping.md) for the full event-by-event mapping
from the Claude version to the Codex version.

## When something is missing

If a workflow that worked under Claude Code does not work under Codex:

1. Check `hook-mapping.md` — the event may not be supported.
2. Check `.codex/prompts/<slug>.md` — the prompt may need a refresh after
   editing `.claude/skills/<slug>/SKILL.md`. Re-run
   `python tools/migration/convert_claude_to_codex.py skills .claude/skills .codex/prompts`.
3. File an issue tagged `codex-parity`.
