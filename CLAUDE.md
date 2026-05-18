# Claude Code Game Studios — Legacy Entry Point

> The canonical project instructions live in [`AGENTS.md`](AGENTS.md).
> Claude Code reads this file by convention; the content below mirrors
> `AGENTS.md` via @-includes so both tools see the same project state.

@AGENTS.md

## Claude-Specific Notes

- The Claude `.claude/` tree (agents, skills, hooks, settings.json,
  statusline.sh) is still functional. Subagent dispatch, the Task tool, and
  the PreCompact/PostCompact hooks have no Codex equivalents, so this tree
  is retained for contributors who prefer Claude Code.
- For the Codex equivalent, see [`docs/codex/README.md`](docs/codex/README.md).
- For the per-hook mapping, see [`docs/codex/hook-mapping.md`](docs/codex/hook-mapping.md).
