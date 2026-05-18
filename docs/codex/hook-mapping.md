# Claude→Codex Hook Mapping

Codex CLI v0.130.0 uses lifecycle hook events that map closely to Claude Code's
hooks. Project-local hook config in `.codex/config.toml` is honored when the
user trusts the project on first run. Event names use PascalCase
(`SessionStart`, `PreToolUse`, `PostToolUse`, `UserPromptSubmit`,
`PermissionRequest`, `Stop`).

| Original `.claude/` hook | Claude event | Codex destination | Status |
|---|---|---|---|
| `session-start.sh` | `SessionStart` | `.codex/hooks/session-start.sh`, wired via `[[hooks.SessionStart]]` in `.codex/config.toml` | ported |
| `detect-gaps.sh` | `SessionStart` (matcher 2) | `.codex/hooks/detect-gaps.sh`, chained from session-start | ported |
| `validate-commit.sh` | `PreToolUse(Bash)` | `.codex/hooks/validate-commit.sh`, wired via `[[hooks.PreToolUse]]` with `matcher = "^Bash$"`. Also installable as `.git/hooks/pre-commit` for users committing outside Codex. | ported (Codex + git) |
| `validate-push.sh` | `PreToolUse(Bash)` | `.codex/hooks/validate-push.sh`, wired via `[[hooks.PreToolUse]]` with `matcher = "^Bash$"`. Also installable as `.git/hooks/pre-push`. | ported (Codex + git) |
| `validate-assets.sh` | `PostToolUse(Write\|Edit)` | `.codex/hooks/validate-assets.sh`, wired via `[[hooks.PostToolUse]]` with `matcher = "^(Write\|Edit)$"`. Manual `/validate-assets` slash prompt available as backup. | ported |
| `validate-skill-change.sh` | `PostToolUse(Write\|Edit)` | `.codex/hooks/validate-skill-change.sh`, wired via `[[hooks.PostToolUse]]`. Manual `/validate-skill-change` slash prompt available as backup. | ported |
| `notify.sh` | `Notification` | `.codex/hooks/notify.sh`, user-level only (must be wired in `~/.codex/config.toml` with `notify = ["bash", ".codex/hooks/notify.sh"]`; project-local `notify` is ignored) | ported (user must opt in) |
| `pre-compact.sh` | `PreCompact` | not portable | Codex CLI v0.130.0 does not expose a `PreCompact` lifecycle hook; the file-backed session state in `production/session-state/active.md` captures the equivalent information |
| `post-compact.sh` | `PostCompact` | not portable | same reason as PreCompact |
| `session-stop.sh` | `Stop` | candidate (not yet wired) | Codex has a `Stop` event but the original script's logic is light; revisit if a stop-time use case appears |
| `log-agent.sh` | `SubagentStart` | not portable | Codex CLI has no first-class subagent dispatch (no `Task` tool); persona prompts are user-invoked via `/agent-<slug>` |
| `log-agent-stop.sh` | `SubagentStop` | not portable | same reason as SubagentStart |

## TOML Syntax Reference

Codex hooks are TOML **arrays of tables**, not plain strings. Event names use
PascalCase. Example pattern:

```toml
[hooks]

[[hooks.SessionStart]]
# optional matcher — regex over event-specific fields

[[hooks.SessionStart.hooks]]
type = "command"
command = "bash .codex/hooks/session-start.sh"
timeout = 10
```

See `.codex/config.toml` in this repo for the full wiring, and the official
Codex docs at <https://developers.openai.com/codex/config-reference> for the
authoritative schema.

## Rationale for non-portable hooks

- **Compaction lifecycle** — we rely on the file-backed state documented in
  `docs/codex/refs/context-management.md` for cross-compaction continuity.
- **Subagent audit trail** — without `Task`-tool dispatch, "subagents" are
  user-invoked persona prompts. Logging happens at the prompt level or in
  commit messages.

When Codex CLI adds new hook events (e.g. a future `PreCompact`), revisit this
table.
