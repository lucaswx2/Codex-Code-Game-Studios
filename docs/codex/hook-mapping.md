# Claude→Codex Hook Mapping

| Original `.claude/` hook | Claude event | Codex destination | Status |
|---|---|---|---|
| `session-start.sh` | `SessionStart` | `.codex/hooks/session-start.sh`, wired via `[hooks].session_start` in `.codex/config.toml` | ported |
| `detect-gaps.sh` | `SessionStart` (matcher 2) | `.codex/hooks/detect-gaps.sh`, chained from session-start | ported |
| `validate-commit.sh` | `PreToolUse(Bash)` | `.codex/hooks/validate-commit.sh`, called from `.git/hooks/pre-commit` | ported (contract changed) |
| `validate-push.sh` | `PreToolUse(Bash)` | `.codex/hooks/validate-push.sh`, called from `.git/hooks/pre-push` | ported (contract changed) |
| `validate-assets.sh` | `PostToolUse(Write\|Edit)` | `/validate-assets` slash prompt | ported (manual invocation) |
| `validate-skill-change.sh` | `PostToolUse(Write\|Edit)` | `/validate-skill-change` slash prompt | ported (manual invocation) |
| `notify.sh` | `Notification` | `.codex/hooks/notify.sh`, wired via `notify = [...]` in `.codex/config.toml` | ported |
| `pre-compact.sh` | `PreCompact` | not portable | Codex has no PreCompact event; session-state file already captures the equivalent information |
| `post-compact.sh` | `PostCompact` | not portable | same reason as PreCompact |
| `session-stop.sh` | `Stop` | not portable | Codex has no Stop event; the operator typically closes the shell, which runs the user's own profile cleanup |
| `log-agent.sh` | `SubagentStart` | not portable | Codex has no first-class subagent dispatch; persona prompts are user-invoked, so logging happens at the prompt level |
| `log-agent-stop.sh` | `SubagentStop` | not portable | same reason as SubagentStart |

## Rationale

Codex CLI's hook surface is intentionally narrower than Claude Code's. The
features we lose are:

- **Compaction lifecycle** — we mitigate by relying on the file-backed state
  documented in `.claude/docs/context-management.md` (still loaded by AGENTS.md).
- **Subagent audit trail** — without `Task`-tool dispatch, "subagents" are
  user-invoked persona prompts. Logging belongs in the operator's shell
  history or in commit messages.
- **Generic Stop hook** — operators who want a Stop equivalent can use their
  shell's `EXIT` trap or terminal exit handler.

When Codex CLI adds new hook events, revisit this table.
