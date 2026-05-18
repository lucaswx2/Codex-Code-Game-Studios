# Remove Claude Code Backcompat Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminate every Claude Code retrocompatibility surface from this repo so the project runs only on OpenAI Codex CLI. Users who want Claude Code are pointed to the upstream Donchitos repository.

**Architecture:** Four-phase cleanup. (1) Delete the entire `.claude/` tree, all `CLAUDE.md` files (root + 4 nested), the now-meaningless `docs/codex/known-gaps.md`, and the migration tooling at `tools/migration/`. (2) Strip the `Originally derived from \`.claude/...\`` attribution banners from 73 skill prompts and 49 personas (122 files total) with a single sed pass. (3) Rewrite the user-facing surface (`README.md`, `AGENTS.md`, `docs/codex/README.md`, `UPGRADING.md`, `CONTRIBUTING.md`) to drop the dual-runtime "legacy Claude still works" framing while preserving a short historical attribution to Donchitos at the bottom of `AGENTS.md` only. (4) Clean hook script headers and remove the backward-compat `.claude/skills/` branch in `validate-skill-change.sh`. The migration plan at `docs/superpowers/plans/2026-05-17-codex-migration.md` and the `docs/codex/refs/` tree stay as-is — those are now the project's own canonical docs, not legacy mirrors.

**Tech Stack:** Bash + `git rm` for deletes, `sed -i` for the banner strip, manual Edit operations for the prose rewrites. No code changes — this is a docs/structural pruning. Verification via `grep -r` after each step.

---

## File Structure

**Deletes** (no longer needed):

- `.claude/` — entire directory tree (agents, skills, hooks, rules, docs, settings.json, statusline.sh, agent-memory)
- `CLAUDE.md` — root redirect file
- `docs/CLAUDE.md`, `src/CLAUDE.md`, `design/CLAUDE.md`, `CCGS Skill Testing Framework/CLAUDE.md` — 4 nested CLAUDE.md files
- `docs/codex/known-gaps.md` — documented Claude features lost in migration; meaningless once Claude side is gone
- `tools/migration/` — converter served its purpose; reinstateable from git history if ever needed for a one-shot upstream sync
- `docs/codex/hook-mapping.md` — was Claude→Codex hook mapping; replaced by a leaner native hook reference at `docs/codex/hooks.md`

**Modifies**:

- `README.md` — remove "Legacy: Claude Code" badge, the `### Claude Code (legacy)` Getting Started subsection, the dual-runtime fork notice; tighten badge row; rewrite sponsor section
- `AGENTS.md` — slim the fork notice to a single historical-attribution paragraph at the bottom; remove "CLAUDE.md points here too" and "legacy `.claude/` tree is preserved" wording
- `docs/codex/README.md` — drop "originally built for Claude Code and is now also supported" framing; replace with Codex-only operator's guide
- `docs/codex/hooks.md` — new file (replaces `hook-mapping.md`); a native Codex hook reference, no Claude column
- `UPGRADING.md` — reset to a single Codex v1.0.0 baseline entry (the pre-fork Claude upgrade history goes away)
- `CONTRIBUTING.md` — Codex-only language; remove "originally Claude Code" wording in the title/intro
- `SECURITY.md` — verify no Claude refs (already migrated earlier; check only)
- `.codex/config.toml` — verify clean (already correct; check only)
- `.codex/hooks/session-start.sh` — remove the `# Originally derived from the Claude Code SessionStart hook` attribution comment
- `.codex/hooks/validate-assets.sh`, `validate-skill-change.sh`, `notify.sh`, `detect-gaps.sh` — same comment cleanup
- `.codex/hooks/validate-skill-change.sh` — remove the `.claude/skills/` backward-compat branch from the path regex; match only `.codex/prompts/`
- All 73 files under `.codex/prompts/*.md` (skill prompts only — wrappers and validators excluded) — strip the single attribution banner line
- All 49 files under `.codex/personas/*.md` — strip the two attribution banner lines

**Preserved unchanged** (now this project's own canonical content):

- `.codex/prompts/`, `.codex/personas/`, `.codex/rules/`, `.codex/hooks/`, `.codex/persona-memory/` — bodies stay; only banners go.
- `docs/codex/refs/` — 61 reference docs migrated from upstream; these are ours now.
- `docs/superpowers/plans/2026-05-17-codex-migration.md` — historical record of how the migration happened.
- `AGENTS.md` mirrors at `src/`, `design/`, `docs/`, `CCGS Skill Testing Framework/` — Codex path-scoped instructions.

---

## Task 1: Delete the .claude tree

**Files:**
- Delete: `.claude/` (recursive, 8 subentries: `agent-memory/`, `agents/`, `docs/`, `hooks/`, `rules/`, `skills/`, `settings.json`, `statusline.sh`)

- [ ] **Step 1: Count what will be removed**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && find .claude -type f | wc -l
```

Expected: ~250+ files (49 agents + 73 skill dirs each with SKILL.md + 12 hooks + 11 rules + ~30 docs + 38 templates + ...).

- [ ] **Step 2: Remove the tree**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && git rm -r .claude
```

- [ ] **Step 3: Verify it's gone**

```bash
test ! -d .claude && echo "gone" || echo "STILL THERE"
```

Expected: `gone`

- [ ] **Step 4: Commit**

```bash
git commit -m "chore: remove .claude tree (Claude Code retrocompat dropped)"
```

---

## Task 2: Delete all CLAUDE.md files

**Files:**
- Delete: `CLAUDE.md` (root)
- Delete: `docs/CLAUDE.md`, `src/CLAUDE.md`, `design/CLAUDE.md`, `CCGS Skill Testing Framework/CLAUDE.md`

- [ ] **Step 1: List the 5 files**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && find . -name CLAUDE.md -not -path "./.git/*"
```

Expected: 5 paths.

- [ ] **Step 2: Remove all 5**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && git rm CLAUDE.md docs/CLAUDE.md src/CLAUDE.md design/CLAUDE.md "CCGS Skill Testing Framework/CLAUDE.md"
```

- [ ] **Step 3: Verify**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && find . -name CLAUDE.md -not -path "./.git/*" | wc -l
```

Expected: `0`

- [ ] **Step 4: Commit**

```bash
git commit -m "chore: delete all CLAUDE.md files (AGENTS.md is canonical now)"
```

---

## Task 3: Delete migration tooling and stale docs

**Files:**
- Delete: `tools/migration/` (recursive — 6 files: converter, tests, `__pycache__/`)
- Delete: `docs/codex/known-gaps.md`
- Delete: `docs/codex/hook-mapping.md`

- [ ] **Step 1: Verify nothing else imports the converter**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && grep -rln "convert_claude_to_codex" --exclude-dir=.git --exclude-dir=tools 2>/dev/null
```

Expected: only matches inside `docs/superpowers/plans/2026-05-17-codex-migration.md` (historical) and possibly the docs themselves. No live imports from `.codex/` or src/.

- [ ] **Step 2: Remove**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && git rm -r tools/migration docs/codex/known-gaps.md docs/codex/hook-mapping.md
```

- [ ] **Step 3: Verify**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && test ! -d tools/migration && test ! -f docs/codex/known-gaps.md && test ! -f docs/codex/hook-mapping.md && echo "all gone"
```

Expected: `all gone`

- [ ] **Step 4: Commit**

```bash
git commit -m "chore: delete migration tooling and Claude-era hook map (no longer needed)"
```

---

## Task 4: Write the new Codex-native hooks reference

**Files:**
- Create: `docs/codex/hooks.md`

Replace the deleted `hook-mapping.md` with a native reference: how Codex hooks are wired in this project, no Claude column.

- [ ] **Step 1: Write the file**

Create `docs/codex/hooks.md` with this exact content:

````markdown
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
````

- [ ] **Step 2: Verify**

```bash
test -f docs/codex/hooks.md && grep -q "SessionStart" docs/codex/hooks.md && echo "ok"
```

Expected: `ok`

- [ ] **Step 3: Commit**

```bash
git add docs/codex/hooks.md
git commit -m "docs(codex): add native hooks reference (replaces hook-mapping.md)"
```

---

## Task 5: Strip attribution banner from 73 skill prompts

**Files:**
- Modify: `.codex/prompts/*.md` (only the 73 skill prompts that carry the banner — wrappers and validate-* files do not)

The banner pattern is a single line right after the frontmatter:

```
> Codex slash-prompt. Originally derived from `.claude/skills/<slug>/SKILL.md` (Claude-Code template fork — see `docs/codex/README.md`).
```

- [ ] **Step 1: Count current banners (baseline)**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && grep -rcE '^> Codex slash-prompt\. Originally derived from `\.claude/skills/' .codex/prompts/ | awk -F: '{s+=$2} END {print s}'
```

Expected: `73`

- [ ] **Step 2: Strip via sed**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && sed -i '/^> Codex slash-prompt\. Originally derived from `\.claude\/skills\//d' .codex/prompts/*.md
```

- [ ] **Step 3: Verify 0 remain**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && grep -rcE '^> Codex slash-prompt\. Originally derived from `\.claude/skills/' .codex/prompts/ | awk -F: '{s+=$2} END {print s}'
```

Expected: `0`

- [ ] **Step 4: Spot-check one prompt**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && head -10 .codex/prompts/start.md
```

Expected: the file starts with frontmatter (`---\n...\n---`) followed by the body content directly, no `> Codex slash-prompt...` line.

- [ ] **Step 5: Commit**

```bash
git add .codex/prompts/
git commit -m "chore(codex): strip Claude-fork attribution banner from 73 skill prompts"
```

---

## Task 6: Strip attribution banner from 49 personas

**Files:**
- Modify: `.codex/personas/*.md` (49 files)

The banner is two lines:

```
> Codex persona. Invoke via `/agent-<slug>` from the project prompts.
> Originally derived from `.claude/agents/<slug>.md` (Claude-Code template fork — see `docs/codex/README.md`).
```

- [ ] **Step 1: Count current banners (baseline)**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && grep -rcE '^> Codex persona\. Invoke via' .codex/personas/ | awk -F: '{s+=$2} END {print s}'
```

Expected: `49`

- [ ] **Step 2: Strip both banner lines via sed**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && sed -i \
  -e '/^> Codex persona\. Invoke via `\/agent-/d' \
  -e '/^> Originally derived from `\.claude\/agents\//d' \
  .codex/personas/*.md
```

- [ ] **Step 3: Verify both patterns gone**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && \
  invoke=$(grep -rcE '^> Codex persona\. Invoke via' .codex/personas/ | awk -F: '{s+=$2} END {print s}') && \
  derived=$(grep -rcE '^> Originally derived from `\.claude/agents/' .codex/personas/ | awk -F: '{s+=$2} END {print s}') && \
  echo "invoke: $invoke / derived: $derived"
```

Expected: `invoke: 0 / derived: 0`

- [ ] **Step 4: Spot-check one persona**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && head -8 .codex/personas/game-designer.md
```

Expected: file starts with `---\n...frontmatter...\n---\n\nYou are the Game Designer...` with no `> Codex persona ...` lines.

- [ ] **Step 5: Commit**

```bash
git add .codex/personas/
git commit -m "chore(codex): strip Claude-fork attribution banner from 49 personas"
```

---

## Task 7: Rewrite README.md

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Remove the "Legacy: Claude Code" badge**

Edit `README.md`. Find the line:

```html
  <a href="https://docs.anthropic.com/en/docs/claude-code"><img src="https://img.shields.io/badge/legacy-Claude%20Code-f5f5f5?logo=anthropic" alt="Legacy: Claude Code"></a>
```

Delete the entire line (including its leading whitespace and trailing newline).

- [ ] **Step 2: Replace the fork notice block**

Find the fork notice block that begins:

```markdown
> **🍴 Fork notice — how this repo came to be:**
>
> This repository is a **vibe-coded fork** of [Claude Code Game Studios]...
```

(the block ends at the next `---` separator)

Replace the entire fork notice block — but keep the surrounding `---` separators — with:

```markdown
> **About this project:** Originally derived from [Donchitos's Claude Code Game Studios](https://github.com/Donchitos/Claude-Code-Game-Studios). This is now a standalone OpenAI Codex CLI project — **no Claude Code retrocompatibility**. If you want the Claude Code version, use the upstream repo directly.
```

- [ ] **Step 3: Remove the "Why This Exists" trailing legacy line**

Find the paragraph ending with:

```
... Codex CLI is the primary supported runtime; Claude Code is still wired up for contributors who prefer it.
```

Replace just the second sentence so the paragraph ends with:

```
... Codex CLI is the supported runtime.
```

- [ ] **Step 4: Remove the "Claude Code (legacy)" Getting Started subsection**

Find the block:

````markdown
### Claude Code (legacy)

The original `.claude/` tree still works:

```bash
claude
```

See [`CLAUDE.md`](CLAUDE.md) for the legacy entry point.
````

Delete the entire block.

- [ ] **Step 5: Rewrite the sponsor + footer lines**

Find:

```markdown
Codex Code Game Studios (fork of Claude Code Game Studios) is free and open source.
```

Replace with:

```markdown
Codex Code Game Studios is free and open source.
```

Find:

```markdown
Sponsorships help fund time spent maintaining prompts, adding new personas, keeping up with Codex CLI / Claude Code and engine API changes, and responding to community issues.
```

Replace with:

```markdown
Sponsorships help fund time spent maintaining prompts, adding new personas, keeping up with Codex CLI and engine API changes, and responding to community issues.
```

Find:

```markdown
*Built for OpenAI Codex CLI (forked from Claude Code Game Studios by Donchitos). Maintained and extended — contributions welcome via [GitHub Discussions](https://github.com/Donchitos/Claude-Code-Game-Studios/discussions).*
```

Replace with:

```markdown
*Built for OpenAI Codex CLI. Originally derived from Claude Code Game Studios by Donchitos. Contributions welcome via GitHub issues and PRs on this fork.*
```

- [ ] **Step 6: Verify**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && \
  ! grep -q "Legacy: Claude Code" README.md && \
  ! grep -q "Claude Code (legacy)" README.md && \
  ! grep -q "still wired up" README.md && \
  echo "README ok"
```

Expected: `README ok`

- [ ] **Step 7: Commit**

```bash
git add README.md
git commit -m "docs(readme): remove Claude Code legacy framing; keep upstream attribution only"
```

---

## Task 8: Rewrite AGENTS.md

**Files:**
- Modify: `AGENTS.md`

- [ ] **Step 1: Replace the fork notice at the top**

Find the fork notice block at lines 7-18 (starts with `> **🍴 Fork notice:**`). Replace the entire block with nothing (delete it). The fork attribution moves to the bottom in Step 3.

- [ ] **Step 2: Update the "canonical entry point" intro**

Find:

```markdown
> This file is the canonical entry point for OpenAI Codex CLI. The legacy
> `CLAUDE.md` points here too, so contributors using either tool see the
> same instructions.
```

Replace with:

```markdown
> This file is the canonical entry point for OpenAI Codex CLI.
```

- [ ] **Step 3: Add a short attribution note at the bottom**

Append at the very end of `AGENTS.md`:

```markdown

---

## Attribution

This repository originated as a fork of
[Donchitos's Claude Code Game Studios](https://github.com/Donchitos/Claude-Code-Game-Studios)
and is now a standalone Codex CLI project. Conversion was performed in a
single migration session, recorded at
[`docs/superpowers/plans/2026-05-17-codex-migration.md`](docs/superpowers/plans/2026-05-17-codex-migration.md).
For the Claude Code version, use the upstream repo directly.
```

- [ ] **Step 4: Verify**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && \
  ! grep -q "vibe-coded fork" AGENTS.md && \
  ! grep -q "CLAUDE.md points here" AGENTS.md && \
  ! grep -q "legacy .claude" AGENTS.md && \
  grep -q "Donchitos's Claude Code Game Studios" AGENTS.md && \
  echo "AGENTS.md ok"
```

Expected: `AGENTS.md ok`

- [ ] **Step 5: Commit**

```bash
git add AGENTS.md
git commit -m "docs(agents): slim fork notice; keep historical attribution only"
```

---

## Task 9: Rewrite docs/codex/README.md

**Files:**
- Modify: `docs/codex/README.md`

- [ ] **Step 1: Remove the fork notice block at the top**

Find the block:

```markdown
> **🍴 Fork notice:** This repository is a **vibe-coded fork** of
> ...
> `../../tools/migration/convert_claude_to_codex.py`).

This repository was originally built for Claude Code and is now primarily
supported under [OpenAI Codex CLI](https://github.com/openai/codex). Codex is
the recommended path going forward; the legacy `.claude/` tree still works for
contributors who prefer Claude Code.
```

Replace the entire block (from `> **🍴 Fork notice:**` through `...prefer Claude Code.`) with:

```markdown
This repository runs on [OpenAI Codex CLI](https://github.com/openai/codex).
For the Claude Code version, see the upstream [Donchitos repo](https://github.com/Donchitos/Claude-Code-Game-Studios)
— this fork does not retain Claude Code retrocompatibility.
```

- [ ] **Step 2: Remove the "Hook mapping" cross-reference (file deleted)**

Find:

```markdown
## Hook mapping

See [hook-mapping.md](hook-mapping.md) for the full event-by-event mapping
from the Claude version to the Codex version.
```

Replace with:

```markdown
## Hooks

See [hooks.md](hooks.md) for the lifecycle-hook reference and TOML syntax.
```

- [ ] **Step 3: Update the "When something is missing" guidance**

Find the section "## When something is missing" and replace:

```markdown
1. Check `hook-mapping.md` — the event may not be supported.
2. Check `.codex/prompts/<slug>.md` — the prompt may need a refresh after
   editing `.claude/skills/<slug>/SKILL.md`. Re-run
   `python tools/migration/convert_claude_to_codex.py skills .claude/skills .codex/prompts`.
3. File an issue tagged `codex-parity`.
```

With:

```markdown
1. Check `hooks.md` — the event may not be supported.
2. Edit the prompt directly at `.codex/prompts/<slug>.md`.
3. File an issue.
```

- [ ] **Step 4: Verify**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && \
  ! grep -q "legacy .claude" docs/codex/README.md && \
  ! grep -q "vibe-coded fork" docs/codex/README.md && \
  ! grep -q "hook-mapping.md" docs/codex/README.md && \
  ! grep -q "tools/migration" docs/codex/README.md && \
  echo "docs/codex/README ok"
```

Expected: `docs/codex/README ok`

- [ ] **Step 5: Commit**

```bash
git add docs/codex/README.md
git commit -m "docs(codex): drop legacy framing; point hooks ref to new hooks.md"
```

---

## Task 10: Reset UPGRADING.md

**Files:**
- Modify: `UPGRADING.md` (full rewrite)

The current file is the original Claude project's upgrade history with our Codex migration section prepended. For a clean break we reset it to a single baseline entry.

- [ ] **Step 1: Read the current file to confirm its size**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && wc -l UPGRADING.md
```

Expected: ~800+ lines.

- [ ] **Step 2: Overwrite the entire file**

Replace the full contents of `UPGRADING.md` with:

```markdown
# Upgrading Codex Code Game Studios

This document tracks upgrade notes for major versions of this Codex CLI
project. Pre-fork upgrade history (Claude Code era) lives in the upstream
[Donchitos repository](https://github.com/Donchitos/Claude-Code-Game-Studios).

## v1.0.0 — initial Codex CLI release (2026-05)

First release as a standalone OpenAI Codex CLI project. Derived in a single
migration session from Donchitos's Claude Code Game Studios; details at
[`docs/superpowers/plans/2026-05-17-codex-migration.md`](docs/superpowers/plans/2026-05-17-codex-migration.md).

### Highlights

- Project instructions in `AGENTS.md` (Codex auto-loads it on session start).
- 73 workflow slash-prompts under `.codex/prompts/` (e.g. `/start`,
  `/brainstorm`, `/dev-story`, `/architecture-review`).
- 49 agent personas invokable as `/agent-<slug>` (e.g. `/agent-game-designer`,
  `/agent-godot-shader-specialist`).
- 11 path-scoped coding rules under `.codex/rules/`, referenced from the
  Path-Scoped Rules table in `AGENTS.md`.
- 5 lifecycle hooks wired via `.codex/config.toml` (`SessionStart`, two
  `PreToolUse` for git commit/push validation, two `PostToolUse` for asset
  and skill-change validation). Codex prompts you to approve them on first
  run via `/hooks`.

### Install

```bash
npm install -g @openai/codex
export OPENAI_API_KEY=sk-...
cd <repo>
codex
```

See [`docs/codex/README.md`](docs/codex/README.md) for the full operator's
guide and [`docs/codex/hooks.md`](docs/codex/hooks.md) for hook semantics.
```

- [ ] **Step 3: Verify**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && \
  ! grep -q "Migrating from Claude Code" UPGRADING.md && \
  ! grep -q "Three new directory-scoped CLAUDE.md" UPGRADING.md && \
  grep -q "Codex Code Game Studios" UPGRADING.md && \
  wc -l UPGRADING.md
```

Expected: `ok` (implicit) and ~35 lines.

- [ ] **Step 4: Commit**

```bash
git add UPGRADING.md
git commit -m "docs(upgrading): reset to single Codex v1.0.0 baseline entry"
```

---

## Task 11: Rewrite CONTRIBUTING.md

**Files:**
- Modify: `CONTRIBUTING.md`

- [ ] **Step 1: Update the title and intro**

Find:

```markdown
# Contributing to Codex Code Game Studios

CCGS is a coordination framework for indie game development. It started as
Claude Code Game Studios (Donchitos); this fork runs primarily under OpenAI
Codex CLI — see [`docs/codex/README.md`](docs/codex/README.md) for the
migration story. Both runtimes are still supported.
```

Replace with:

```markdown
# Contributing to Codex Code Game Studios

CCGS is a coordination framework for indie game development running on
OpenAI Codex CLI. See [`docs/codex/README.md`](docs/codex/README.md) for the
operator's guide. For the original Claude Code version, see the upstream
[Donchitos repo](https://github.com/Donchitos/Claude-Code-Game-Studios) —
this fork does not retain Claude Code retrocompatibility.
```

- [ ] **Step 2: Find remaining Claude references in the body**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && grep -n "Claude" CONTRIBUTING.md
```

Expected: a few hits (legacy paths like `.claude/skills/` may appear in technical examples). For each, decide:

- Path examples like `.claude/skills/<name>/SKILL.md` → rewrite to `.codex/prompts/<name>.md`.
- General brand references → rewrite or remove.

Apply Edit operations for each match.

- [ ] **Step 3: Verify**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && grep -c "Claude" CONTRIBUTING.md
```

Expected: `0`, or only matches inside historical attribution sentences if any.

- [ ] **Step 4: Commit**

```bash
git add CONTRIBUTING.md
git commit -m "docs(contributing): Codex-only language; remove Claude framing"
```

---

## Task 12: Clean hook script header comments

**Files:**
- Modify: `.codex/hooks/session-start.sh`, `validate-assets.sh`, `validate-skill-change.sh`, `notify.sh`, `detect-gaps.sh`

The "Originally derived from the Claude Code ... hook" attribution comments in the headers are no longer needed. Strip them.

- [ ] **Step 1: Inspect current headers**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && for f in .codex/hooks/*.sh; do echo "=== $f ==="; head -5 "$f"; done
```

- [ ] **Step 2: Strip the "Originally derived from" line in each script**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && sed -i '/^# Originally derived from the Claude Code/d' .codex/hooks/*.sh
```

- [ ] **Step 3: Also strip the `same dual-hook behavior the Claude` comment fragment in session-start.sh**

Find in `.codex/hooks/session-start.sh`:

```bash
# Chain detect-gaps so Codex gets the same dual-hook behavior the Claude
# SessionStart matcher provided.
```

Replace those 2 comment lines with:

```bash
# Chain detect-gaps so SessionStart loads both the runtime context and any
# documentation gaps before the model starts the conversation.
```

- [ ] **Step 4: Verify**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && grep -cE "Claude Code" .codex/hooks/*.sh
```

Expected: every line shows `:0`.

- [ ] **Step 5: Commit**

```bash
git add .codex/hooks/
git commit -m "chore(codex): strip Claude attribution comments from hook scripts"
```

---

## Task 13: Remove backward-compat from validate-skill-change.sh

**Files:**
- Modify: `.codex/hooks/validate-skill-change.sh`

Currently the script matches BOTH `.codex/prompts/` AND legacy `.claude/skills/` paths. Drop the legacy branch.

- [ ] **Step 1: Find the matcher block**

The current pattern is:

```bash
# Only act on files inside .codex/prompts/ or the legacy .claude/skills/
if ! echo "$FILE_PATH" | grep -qE '(^|/)(\.codex/prompts/|\.claude/skills/)'; then
    exit 0
fi

# Extract skill/prompt name from either layout:
#   .codex/prompts/[name].md   → name
#   .claude/skills/[name]/SKILL.md → name
SKILL_NAME=$(echo "$FILE_PATH" \
    | grep -oE '(\.codex/prompts/[^/]+\.md|\.claude/skills/[^/]+)' \
    | sed -E 's|\.codex/prompts/||; s|\.md$||; s|\.claude/skills/||')
```

- [ ] **Step 2: Replace with Codex-only**

Replace the block above with:

```bash
# Only act on files inside .codex/prompts/.
if ! echo "$FILE_PATH" | grep -qE '(^|/)\.codex/prompts/'; then
    exit 0
fi

# Extract prompt name: .codex/prompts/[name].md → name
SKILL_NAME=$(echo "$FILE_PATH" \
    | grep -oE '\.codex/prompts/[^/]+\.md' \
    | sed -E 's|\.codex/prompts/||; s|\.md$||')
```

- [ ] **Step 3: Also update the file's top comment**

Find at the top of the file:

```bash
# Fires when any file inside .codex/prompts/ (or legacy .claude/skills/) is written or edited.
```

Replace with:

```bash
# Fires when any file inside .codex/prompts/ is written or edited.
```

- [ ] **Step 4: Verify**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && grep -c "\.claude/skills" .codex/hooks/validate-skill-change.sh
```

Expected: `0`

- [ ] **Step 5: Smoke-test the script**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && \
echo '{"tool_input":{"file_path":".codex/prompts/start.md"}}' | bash .codex/hooks/validate-skill-change.sh 2>&1
```

Expected: prints `=== Skill Modified: start ===` and an advisory; exits 0.

- [ ] **Step 6: Commit**

```bash
git add .codex/hooks/validate-skill-change.sh
git commit -m "fix(codex): drop legacy .claude/skills/ branch from validate-skill-change"
```

---

## Task 14: Final verification

**Files:**
- None modified (read-only audit)

- [ ] **Step 1: Audit for stray Claude refs in functional code**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && \
echo "=== .codex/ functional refs to claude/ paths ===" && \
grep -rEn "\\.claude/" .codex/ 2>/dev/null && \
echo "=== expected: 0 lines ==="
```

Expected: 0 lines printed (silent grep).

- [ ] **Step 2: Audit for Claude Code mentions outside intentional attribution**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && \
grep -rln "Claude Code" \
  README.md AGENTS.md UPGRADING.md CONTRIBUTING.md SECURITY.md \
  docs/codex/ .codex/ \
  src/AGENTS.md design/AGENTS.md docs/AGENTS.md \
  "CCGS Skill Testing Framework/AGENTS.md" 2>/dev/null
```

Expected: only `README.md`, `AGENTS.md`, `CONTRIBUTING.md`, `UPGRADING.md`, `docs/codex/README.md` — each containing only the short upstream attribution lines. Verify by reading the context of each match.

- [ ] **Step 3: Confirm AGENTS.md links still resolve**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && \
broken=0; \
for ref in $(grep -hoE "docs/codex/refs/[a-zA-Z0-9_/.-]+\.(md|yaml)" AGENTS.md 2>/dev/null | sort -u); do
  [ ! -f "$ref" ] && { echo "MISSING: $ref"; broken=$((broken+1)); }
done; echo "broken AGENTS.md links: $broken"
```

Expected: `broken AGENTS.md links: 0`

- [ ] **Step 4: Smoke-test session-start hook**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && bash .codex/hooks/session-start.sh 2>&1 | head -3
```

Expected: starts with `=== Codex Code Game Studios — Session Context ===` and shows `Branch: main`.

- [ ] **Step 5: Validate config.toml still parses**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && python -c "import tomllib, pathlib; cfg = tomllib.loads(pathlib.Path('.codex/config.toml').read_text()); assert cfg.get('sandbox') == 'workspace-write'; print('config ok')"
```

Expected: `config ok`

- [ ] **Step 6: Tag the milestone**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && git tag -a v1.0.0-codex -m "Codex Code Game Studios v1.0.0 — Claude Code retrocompat removed"
```

(No `git commit` here; the deletes/edits are already committed.)

---

## Self-Review

**1. Spec coverage:**

- `.claude/` deleted → Task 1 ✓
- All `CLAUDE.md` files deleted → Task 2 ✓
- Migration tooling + stale Claude-era docs deleted → Task 3 ✓
- Replacement Codex-native hooks reference → Task 4 ✓
- Banner strip from prompts → Task 5 ✓
- Banner strip from personas → Task 6 ✓
- README rewritten → Task 7 ✓
- AGENTS.md rewritten → Task 8 ✓
- docs/codex/README.md rewritten → Task 9 ✓
- UPGRADING.md reset → Task 10 ✓
- CONTRIBUTING.md rewritten → Task 11 ✓
- Hook comments cleaned → Task 12 ✓
- validate-skill-change.sh legacy branch removed → Task 13 ✓
- Final audit + tag → Task 14 ✓

**2. Placeholder scan:**

- No `TBD`, no `TODO`, no `implement later`, no `similar to Task N`. Every Edit and every shell command is spelled out fully.

**3. Type consistency:**

- File path constants (`.codex/prompts/`, `.codex/personas/`, `.codex/hooks/`, `docs/codex/`) used consistently across all 14 tasks.
- The `docs/codex/hooks.md` filename introduced in Task 4 is referenced again in Tasks 9 and 11.
- The `--no-Claude-Code-retrocompat` framing is consistent across README/AGENTS/docs/codex/README/UPGRADING/CONTRIBUTING.
- Hook script names (`session-start.sh`, `validate-commit.sh`, etc.) match between Tasks 4 and 12 and the `.codex/config.toml` already on disk.

**Risk note:** This plan is destructive for the `.claude/` tree. Recovery from git history is straightforward (`git revert` or `git checkout <pre-tag>`), but anyone with uncommitted work in `.claude/` will lose it. Confirm the working tree is clean before starting Task 1.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-18-remove-claude-backcompat.md`. Two execution options:

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration. Uses `superpowers:subagent-driven-development`.

**2. Inline Execution** — execute in this session via `superpowers:executing-plans`, batch with checkpoints.

Which approach?
