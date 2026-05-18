---
name: Bug Report
about: Something isn't working as expected
title: "[Bug] "
labels: bug
assignees: ''
---

## Description

A clear description of what the bug is.

## Steps to Reproduce

1. Open `codex` in a project using this template
2. Run `/<prompt>` or `/agent-<slug>` (or trigger the hook that fails)
3. ...
4. See error

## Expected Behavior

What you expected to happen.

## Actual Behavior

What actually happened. Include any error messages, hook output, or
unexpected slash-command behavior.

## Environment

- **OS**: (e.g., Windows 11, macOS 14, Ubuntu 24.04, WSL2)
- **Shell**: (e.g., bash, zsh, fish, Git Bash)
- **Codex CLI version**: (run `codex --version`)
- **Node.js version**: (run `node --version`)
- **Model**: (e.g., `gpt-5.3-codex`, `gpt-5.5`)
- **jq installed?**: Yes / No
- **Python installed?**: Yes / No

## Affected Component

- [ ] Persona (which one? — e.g., `agent-game-designer`):
- [ ] Slash prompt (which one? — e.g., `start`, `dev-story`):
- [ ] Lifecycle hook (which one? — `session-start`, `validate-commit`, ...):
- [ ] Path-scoped rule (which one? — see `.codex/rules/`):
- [ ] Reference doc (under `docs/codex/refs/`):
- [ ] Documentation (README, AGENTS.md, etc.):
- [ ] Other:

## Additional Context

Any other context — screenshots, terminal output, output from `bash
.codex/hooks/session-start.sh`, contents of `production/session-state/active.md`
if relevant.
