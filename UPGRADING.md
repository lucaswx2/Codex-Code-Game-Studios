# Upgrading Codex Code Game Studios

This document tracks upgrade notes for major versions of this Codex CLI
project. Pre-fork upgrade history (Claude Code era) lives in the upstream
[Donchitos repository](https://github.com/Donchitos/Claude-Code-Game-Studios).

## v1.0.0 — initial Codex CLI release (2026-05)

First release as a standalone OpenAI Codex CLI project. Derived in a single
migration session from Donchitos's Claude Code Game Studios; details at
[`docs/superpowers/plans/2026-05-17-codex-migration.md`](docs/superpowers/plans/2026-05-17-codex-migration.md).

### Highlights

- Project instructions in `AGENTS.md` (Codex auto-loads it on session start).
- 73 workflow slash-prompts under `.codex/prompts/` (e.g. `/start`,
  `/brainstorm`, `/dev-story`, `/architecture-review`).
- 49 agent personas invokable as `/agent-<slug>` (e.g. `/agent-game-designer`,
  `/agent-godot-shader-specialist`).
- 11 path-scoped coding rules under `.codex/rules/`, referenced from the
  Path-Scoped Rules table in `AGENTS.md`.
- 5 lifecycle hooks wired via `.codex/config.toml` (`SessionStart`, two
  `PreToolUse` for git commit/push validation, two `PostToolUse` for asset
  and skill-change validation). Codex prompts you to approve them on first
  run via `/hooks`.

### Install

```bash
npm install -g @openai/codex
export OPENAI_API_KEY=sk-...
cd <repo>
codex
```

See [`docs/codex/README.md`](docs/codex/README.md) for the full operator's
guide and [`docs/codex/hooks.md`](docs/codex/hooks.md) for hook semantics.
