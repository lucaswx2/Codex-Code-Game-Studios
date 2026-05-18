## Summary

Brief description of what this PR does.

## Type of Change

- [ ] New persona (`.codex/personas/<slug>.md` + `.codex/prompts/agent-<slug>.md` wrapper)
- [ ] New slash prompt (`.codex/prompts/<slug>.md`)
- [ ] New lifecycle hook or path-scoped rule
- [ ] Bug fix
- [ ] Documentation improvement
- [ ] Other:

## Changes

-
-
-

## Checklist

- [ ] I've tested this in an OpenAI Codex CLI session
- [ ] New personas include the Collaboration Protocol section
- [ ] New slash prompts use the flat `.codex/prompts/<name>.md` format (no subdirectories — Codex does not pick them up)
- [ ] Frontmatter on prompts is minimal: `description` (required) + `argument-hint` (optional)
- [ ] Reference docs are updated when relevant (`docs/codex/refs/`, `docs/codex/hooks.md`)
- [ ] Hooks use `grep -E` (POSIX) and fail gracefully without `jq`/`python`
- [ ] No hardcoded paths or platform-specific assumptions
- [ ] LF line endings only (`.gitattributes` enforces this for `.sh`/`.py`/`.toml`/`.yaml`)
