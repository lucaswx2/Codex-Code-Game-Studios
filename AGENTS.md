# Codex Code Game Studios — Agent Instructions

> This file is the canonical entry point for OpenAI Codex CLI.

Indie game development managed through 49 coordinated AI personas and 73
custom slash-prompts. Each persona owns a specific domain, enforcing
separation of concerns and quality.

## Technology Stack

- **Engine**: [CHOOSE: Godot 4 / Unity / Unreal Engine 5]
- **Language**: [CHOOSE: GDScript / C# / C++ / Blueprint]
- **Version Control**: Git with trunk-based development
- **Build System**: [SPECIFY after choosing engine]
- **Asset Pipeline**: [SPECIFY after choosing engine]

> **Note**: Engine-specialist personas exist for Godot, Unity, and Unreal
> with dedicated sub-specialists. Use the set matching your engine.

## Project Structure

See [docs/codex/refs/directory-structure.md](docs/codex/refs/directory-structure.md).

## Engine Version Reference

See [docs/engine-reference/godot/VERSION.md](docs/engine-reference/godot/VERSION.md).

## Technical Preferences

See [docs/codex/refs/technical-preferences.md](docs/codex/refs/technical-preferences.md).

## Coordination Rules

See [docs/codex/refs/coordination-rules.md](docs/codex/refs/coordination-rules.md).

## Collaboration Protocol

**User-driven collaboration, not autonomous execution.**
Every task follows: **Question -> Options -> Decision -> Draft -> Approval**

- Personas MUST ask "May I write this to [filepath]?" before writing files.
- Personas MUST show drafts or summaries before requesting approval.
- Multi-file changes require explicit approval for the full changeset.
- No commits without user instruction.

See [docs/codex/refs/COLLABORATIVE-DESIGN-PRINCIPLE.md](docs/codex/refs/COLLABORATIVE-DESIGN-PRINCIPLE.md)
for full protocol and examples.

> **First session?** If the project has no engine configured and no game
> concept, run `/start` to begin the guided onboarding flow.

## Coding Standards

See [docs/codex/refs/coding-standards.md](docs/codex/refs/coding-standards.md).

## Context Management

See [docs/codex/refs/context-management.md](docs/codex/refs/context-management.md).

## Path-Scoped Rules

Codex CLI auto-loads only the nearest `AGENTS.md`. The rule files below contain
coding standards that apply when editing specific kinds of files — the model
must consult these manually when relevant:

| When editing                              | Read                                  |
|-------------------------------------------|---------------------------------------|
| AI code (state machines, behavior trees)  | `.codex/rules/ai-code.md`             |
| Data files (JSON, YAML, balance tables)   | `.codex/rules/data-files.md`          |
| Design docs (GDDs, narrative, levels)     | `.codex/rules/design-docs.md`         |
| Engine code (core systems, framework)     | `.codex/rules/engine-code.md`         |
| Gameplay code (mechanics, player systems) | `.codex/rules/gameplay-code.md`       |
| Narrative content (dialogue, lore)        | `.codex/rules/narrative.md`           |
| Network code (replication, RPCs)          | `.codex/rules/network-code.md`        |
| Prototype code (throwaway builds)         | `.codex/rules/prototype-code.md`      |
| Shader code (HLSL, GLSL)                  | `.codex/rules/shader-code.md`         |
| Tests (unit, integration)                 | `.codex/rules/test-standards.md`      |
| UI code (menus, HUD)                      | `.codex/rules/ui-code.md`             |

## Persona Memory

Long-lived persona notes live under `.codex/persona-memory/<persona>/MEMORY.md`.
Personas should read their own memory file at session start and append new
durable observations as they accrue.

## Codex-Specific Notes

- Skills live under `.agents/skills/<name>/SKILL.md` (Codex CLI's
  conventional location). Invoke them with the `$` prefix
  (e.g. `$start`, `$agent-game-designer`) or describe the task and let
  Codex auto-select. The `/` prefix is reserved for built-in Codex
  commands (`/hooks`, `/model`, `/review`, `/quit`).
- The Codex config is `.codex/config.toml`. Per-user secrets belong in
  `~/.codex/config.toml`, not this file.
- See [docs/codex/README.md](docs/codex/README.md) for setup and hook
  semantics.

---

## Attribution

This repository originated as a fork of
[Donchitos's Claude Code Game Studios](https://github.com/Donchitos/Claude-Code-Game-Studios)
and is now a standalone Codex CLI project. Conversion was performed in a
single migration session, recorded at
[`docs/superpowers/plans/2026-05-17-codex-migration.md`](docs/superpowers/plans/2026-05-17-codex-migration.md).
For the Claude Code version, use the upstream repo directly.
