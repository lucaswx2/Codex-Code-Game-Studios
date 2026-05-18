# Codex Hooks Reference

This project wires the following Codex CLI lifecycle hooks via
`.codex/config.toml`. Event names use PascalCase as required by Codex
v0.130.0+; values are TOML arrays of tables. On first run, Codex prompts you
to review and approve each hook (`/hooks` in interactive mode).

## Wired Hooks

| Event | Matcher | Script | Purpose |
|---|---|---|---|
| `SessionStart` | (none) | `.codex/hooks/session-start.sh` | Prints branch / sprint / milestone / bug count at session start; chains into `detect-gaps.sh` to surface missing documentation. |
| `PreToolUse` | `^Bash$` | `.codex/hooks/validate-commit.sh` | Inspects git commit commands. Warns on non-Conventional-Commit messages; blocks `.env` files. |
| `PreToolUse` | `^Bash$` | `.codex/hooks/validate-push.sh` | Inspects git push commands. Blocks force-push to `main`/`master`. |
| `PostToolUse` | `^(Write\|Edit)$` | `.codex/hooks/validate-assets.sh` | Validates naming conventions on files written under `assets/`. |
| `PostToolUse` | `^(Write\|Edit)$` | `.codex/hooks/validate-skill-change.sh` | Advises running `/skill-test` after edits to `.codex/prompts/`. |

## TOML Syntax

Codex hooks are arrays of tables. Example:

```toml
[hooks]

[[hooks.SessionStart]]

[[hooks.SessionStart.hooks]]
type = "command"
command = "bash .codex/hooks/session-start.sh"
timeout = 10
```

See `.codex/config.toml` in this repo for the full wiring, and the official
Codex docs at <https://developers.openai.com/codex/config-reference> for the
authoritative schema.

## Notifications (user-level only)

`notify` is honored only in `~/.codex/config.toml`, not in project-local
config. The repo ships `.codex/hooks/notify.sh` (a Windows-toast notifier).
To use it, add to your user config:

```toml
notify = ["bash", "/absolute/path/to/.codex/hooks/notify.sh"]
```

## Git Hooks (optional, per-clone)

The same `validate-commit.sh` / `validate-push.sh` scripts work as git hooks
for users who commit outside Codex. Install once per clone:

```bash
ln -s ../../.codex/hooks/validate-commit.sh .git/hooks/pre-commit
ln -s ../../.codex/hooks/validate-push.sh   .git/hooks/pre-push
chmod +x .git/hooks/pre-commit .git/hooks/pre-push
```

On Windows, use a thin `.bat` or `bash` wrapper if symlinks are not enabled.
