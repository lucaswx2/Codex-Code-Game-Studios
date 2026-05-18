# Codex Code Game Studios — Agent Instructions

> This file is the canonical entry point for OpenAI Codex CLI. The legacy
> `CLAUDE.md` points here too, so contributors using either tool see the
> same instructions.

> **🍴 Fork notice:** This repository is a **vibe-coded fork** of
> [Claude Code Game Studios](https://github.com/Donchitos/Claude-Code-Game-Studios)
> (original by Donchitos). The conversion from Claude Code → OpenAI Codex CLI
> was performed by Claude itself in a single coordinated migration session —
> see [`docs/superpowers/plans/2026-05-17-codex-migration.md`](docs/superpowers/plans/2026-05-17-codex-migration.md).
> Everything under `.codex/` was mechanically derived from `.claude/` via the
> converter at
> [`tools/migration/convert_claude_to_codex.py`](tools/migration/convert_claude_to_codex.py).
> The legacy `.claude/` tree is preserved for contributors who prefer Claude
> Code; Codex CLI is the primary supported runtime.

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

## Codex-Specific Notes

- Custom slash-prompts live under `.codex/prompts/`. Type `/` in interactive
  mode to list them. Persona prompts use the `agent-<slug>` prefix
  (e.g. `/agent-game-designer`).
- The Codex config is `.codex/config.toml`. Per-user secrets belong in
  `~/.codex/config.toml`, not this file.
- See [docs/codex/README.md](docs/codex/README.md) for setup and hook
  semantics.
