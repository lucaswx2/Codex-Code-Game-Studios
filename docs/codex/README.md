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
4. Discovers skills under `.agents/skills/`: 73 workflow skills
   (`$start`, `$brainstorm`, `$dev-story`, …) and 49 persona-adopting
   skills (`$agent-game-designer`, `$agent-godot-specialist`, …).

Invoke skills with the `$` prefix or describe your task in natural language
and Codex auto-selects. `/` is reserved for built-in CLI commands. See
[hooks.md](hooks.md) for the lifecycle-hook reference.

## Git hooks (one-time, per clone)

The pre-commit and pre-push validators are not auto-installed — symlink them:

```bash
ln -s ../../.codex/hooks/validate-commit.sh .git/hooks/pre-commit
ln -s ../../.codex/hooks/validate-push.sh   .git/hooks/pre-push
chmod +x .git/hooks/pre-commit .git/hooks/pre-push
```

On Windows, create thin `.bat`/`bash` wrappers under `.git/hooks/` that call
the scripts; symlinks may not work without developer mode.

## Skills

All skills live at `.agents/skills/<name>/SKILL.md`. Two categories:

- **Workflow skills** (`$start`, `$dev-story`, `$architecture-review`, …)
  drive step-by-step processes. The skill body is the SKILL.md itself.
- **Persona-adopting skills** (`$agent-game-designer`,
  `$agent-godot-shader-specialist`, …) consist of two collocated files
  per skill: `SKILL.md` (the wrapper that tells Codex to adopt the
  persona) and `persona.md` (the persona body — voice, constraints,
  collaboration protocol). Use them when you want domain expertise.

## Hooks

See [hooks.md](hooks.md) for the lifecycle-hook reference and TOML syntax.

## Status — what is and isn't tested

The framework structure (AGENTS.md loading, `.codex/config.toml`, lifecycle
hooks, `.agents/skills/<name>/SKILL.md` discovery and frontmatter parsing)
has been validated against Codex CLI v0.130.0. The 124 skill bodies were
mechanically rewritten from the upstream Claude Code template and are
**only spot-tested**, not exhaustively validated. Expect some skills to
need polish or have broken cross-references when first invoked — especially
ones that reference other skills, templates, or paths that may have
shifted during the migration.

## When something is broken

If a skill misbehaves, has stale path references, or its YAML frontmatter
won't parse:

1. Check `hooks.md` — the event may not be supported.
2. Open `.agents/skills/<name>/SKILL.md` and read the frontmatter +
   first body lines. Common issues:
   - Missing or mis-indented YAML fields
   - References to `.codex/prompts/` or `.codex/personas/` (old paths)
   - References to other skills by `/skill-name` instead of `$skill-name`
3. Fix it locally and **submit a PR** to this repo. Even one-line fixes
   are welcome — see [`../../CONTRIBUTING.md`](../../CONTRIBUTING.md).

If you cannot fix it yourself, open an issue with the skill name, the
error Codex printed, and steps to reproduce.
