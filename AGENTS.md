# Codex Code Game Studios — Agent Instructions

> This file is the canonical entry point for OpenAI Codex CLI. The legacy
> `CLAUDE.md` points here too, so contributors using either tool see the
> same instructions.

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

See [.claude/docs/directory-structure.md](.claude/docs/directory-structure.md).

## Engine Version Reference

See [docs/engine-reference/godot/VERSION.md](docs/engine-reference/godot/VERSION.md).

## Technical Preferences

See [.claude/docs/technical-preferences.md](.claude/docs/technical-preferences.md).

## Coordination Rules

See [.claude/docs/coordination-rules.md](.claude/docs/coordination-rules.md).

## Collaboration Protocol

**User-driven collaboration, not autonomous execution.**
Every task follows: **Question -> Options -> Decision -> Draft -> Approval**

- Personas MUST ask "May I write this to [filepath]?" before writing files.
- Personas MUST show drafts or summaries before requesting approval.
- Multi-file changes require explicit approval for the full changeset.
- No commits without user instruction.

See [docs/COLLABORATIVE-DESIGN-PRINCIPLE.md](docs/COLLABORATIVE-DESIGN-PRINCIPLE.md)
for full protocol and examples.

> **First session?** If the project has no engine configured and no game
> concept, run `/start` to begin the guided onboarding flow.

## Coding Standards

See [.claude/docs/coding-standards.md](.claude/docs/coding-standards.md).

## Context Management

See [.claude/docs/context-management.md](.claude/docs/context-management.md).

## Codex-Specific Notes

- Custom slash-prompts live under `.codex/prompts/`. Type `/` in interactive
  mode to list them. Persona prompts use the `agent-<slug>` prefix
  (e.g. `/agent-game-designer`).
- The Codex config is `.codex/config.toml`. Per-user secrets belong in
  `~/.codex/config.toml`, not this file.
- See [docs/codex/README.md](docs/codex/README.md) for setup and hook
  semantics.
