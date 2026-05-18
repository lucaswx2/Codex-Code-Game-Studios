# Known Codex parity gaps

Tracked here while no `codex-parity` GitHub label exists. Each item names the
Claude Code capability we lost in the migration, the workaround in use today,
and the trigger that would let us close the gap.

- **PreCompact / PostCompact hooks** — Codex CLI has no compaction lifecycle
  event. Workaround: rely on the file-backed session state at
  `production/session-state/active.md`, written incrementally per the
  context-management protocol. Revisit when Codex CLI ships a compaction
  event.

- **SubagentStart / SubagentStop hooks** — Codex CLI has no first-class
  subagent dispatch (no `Task` tool). Persona prompts are user-invoked via
  `/agent-<slug>` instead. Workaround: log persona usage through commit
  messages and shell history. Revisit when Codex CLI gains a subagent API.

- **Generic Stop hook** — Codex CLI has no session-stop event. Workaround:
  operators who need a Stop equivalent can use their shell's `EXIT` trap or
  terminal exit handler.

- **statusline.sh** — Codex CLI has no status-line API. Removed from the
  Codex path. Sprint/task status surfaces via the `/sprint-status` slash
  prompt instead.
