# Codex Operator's Guide

This repository runs on [OpenAI Codex CLI](https://github.com/openai/codex).
For the Claude Code version, see the upstream [Donchitos repo](https://github.com/Donchitos/Claude-Code-Game-Studios)
— this fork does not retain Claude Code retrocompatibility.

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

> **⚠ First-run hook approval is required.** On the very first launch in
> this repo, Codex prints `⚠ 5 hooks need review before they can run.`
> This is the security gate: Codex will not execute project-local hooks
> until you explicitly approve them.
>
> Inside the Codex session, run `/hooks` and approve each of the 5
> lifecycle hooks (1× `SessionStart`, 2× `PreToolUse`, 2× `PostToolUse`).
> Then exit (`Ctrl+D` or `/quit`) and re-launch `codex` so the SessionStart
> banner kicks in.

On startup (after hooks are approved), Codex:

1. Reads `AGENTS.md` for project instructions.
2. Loads `.codex/config.toml` (sandbox, approval policy, hook wiring).
3. Runs `.codex/hooks/session-start.sh` which prints branch/sprint/milestone
   context and chains `detect-gaps.sh`.
4. Exposes 73 workflow slash-prompts (`/start`, `/brainstorm`, `/dev-story`, …)
   and 49 persona wrappers (`/agent-game-designer`, `/agent-godot-specialist`, …).

Type `/` to browse the prompt catalogue. See [hooks.md](hooks.md) for the
full lifecycle-hook reference.

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

## Hooks

See [hooks.md](hooks.md) for the lifecycle-hook reference and TOML syntax.

## When something is missing

If a workflow that worked under Claude Code does not work under Codex:

1. Check `hooks.md` — the event may not be supported.
2. Edit the prompt directly at `.codex/prompts/<slug>.md`.
3. File an issue.
