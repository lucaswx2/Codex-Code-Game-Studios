# Restructure `.codex/prompts/` → `.agents/skills/` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Codex CLI actually discover and run the 124 skill files by (a) moving them from the flat `.codex/prompts/<slug>.md` layout (which Codex v0.130.0+ ignores) to the conventional `.agents/skills/<slug>/SKILL.md` structure required by the loader at `codex-rs/core-skills/src/loader.rs` (constants `SKILLS_FILENAME = "SKILL.md"`, `AGENTS_DIR_NAME = ".agents"`, `SKILLS_DIR_NAME = "skills"`, plus `repo_agents_skill_roots()` which scans `<cwd>/.agents/skills/` for project-local skills), AND (b) re-adding the required `name:` field to each SKILL.md frontmatter — the Claude→Codex converter stripped it (`CLAUDE_ONLY_SKILL_FIELDS`), but `SkillMetadata.name: String` (model.rs) is non-Optional and parsing fails without it. After this, skills are invocable as `$<name>` per `injection.rs` (`Text inputs are scanned to extract $skill-name tokens`) or implicitly when the user describes the task (allow_implicit_invocation = true by default).

**Architecture:** Three-phase restructure optimized for parallel execution. **Phase A** is a single atomic Bash script that creates `.agents/skills/`, moves all 73 workflow skills into per-skill subdirectories, collocates each of the 49 persona wrappers with its persona body (`SKILL.md` + `persona.md`), moves 2 validators similarly, deletes the now-empty source dirs, and rewrites wrapper `Read` references via sed. **Phase B** is 8 parallel doc edits (README, AGENTS.md, docs/codex/*, hooks, config.toml) to update paths and switch the documented invocation from `/skill` to `$skill`. **Phase C** runs smoke verification and offers the user a runtime test (`$start` inside `codex`). Content of every skill/persona file is preserved byte-for-byte except where path references explicitly need updating.

**Tech Stack:** Bash + `mv` + `sed` for file restructure; Edit + Write for doc rewrites; `find` and `wc -l` for verification. No code changes.

---

## File Structure

**Creates:**

- `.agents/skills/<slug>/SKILL.md` × 73 (workflow skills)
- `.agents/skills/agent-<slug>/SKILL.md` × 49 (persona wrappers)
- `.agents/skills/agent-<slug>/persona.md` × 49 (persona bodies, collocated with wrappers)
- `.agents/skills/validate-assets/SKILL.md` (1)
- `.agents/skills/validate-skill-change/SKILL.md` (1)

Total new files: **173** (122 SKILL.md + 49 persona.md + 2 validators)

**Deletes:**

- `.codex/prompts/` (entire directory — 124 .md files become 122 SKILL.md + 2 validator SKILL.md after restructure)
- `.codex/personas/` (entire directory — 49 .md files become collocated persona.md)

**Modifies:**

- All 49 wrapper SKILL.md files — sed replaces `.codex/personas/<persona-slug>.md` → `persona.md` (relative reference, since persona body is collocated)
- `README.md` — paths + invocation syntax (3 sections: badges, What's Included, Slash Commands intro)
- `AGENTS.md` — paths in 3 references (Path-Scoped Rules already point at `.codex/rules/` which stays; Persona Memory stays at `.codex/persona-memory/`; only the "Custom slash-prompts live under" line in Codex-Specific Notes needs updating)
- `docs/codex/README.md` — paths + invocation syntax (Personas vs prompts section)
- `docs/codex/hooks.md` — `.codex/prompts/` references in validate-skill-change description
- `.codex/hooks/validate-skill-change.sh` — change path regex from `.codex/prompts/` to `.agents/skills/`
- `.codex/config.toml` — comment that mentions `.codex/prompts/`
- `src/AGENTS.md`, `docs/AGENTS.md`, `CCGS Skill Testing Framework/AGENTS.md` — any `.codex/prompts/` refs (likely 0–2 each)

**Preserved unchanged:**

- `.codex/config.toml` (hooks section — already correct)
- `.codex/hooks/*.sh` (except validate-skill-change.sh path regex)
- `.codex/rules/`, `.codex/persona-memory/` — these stay as-is
- `docs/codex/refs/` — migrated reference docs
- All plans under `docs/superpowers/plans/`

---

## Task 1: Single atomic restructure script

**Files:**
- Create: `.agents/skills/<slug>/SKILL.md` × 73 (workflow)
- Create: `.agents/skills/agent-<slug>/SKILL.md` × 49 (wrappers)
- Create: `.agents/skills/agent-<slug>/persona.md` × 49 (bodies)
- Create: `.agents/skills/validate-assets/SKILL.md`, `.agents/skills/validate-skill-change/SKILL.md`
- Delete: `.codex/prompts/` (entire dir)
- Delete: `.codex/personas/` (entire dir)
- Modify: 49 wrapper SKILL.md files (sed replace persona path)

- [ ] **Step 1: Baseline count (verify expected starting state)**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && \
echo "workflow skills: $(ls .codex/prompts/ | grep -v '^agent-' | grep -v '^validate-' | wc -l)" && \
echo "agent wrappers: $(ls .codex/prompts/ | grep '^agent-' | wc -l)" && \
echo "validators: $(ls .codex/prompts/ | grep '^validate-' | wc -l)" && \
echo "personas: $(ls .codex/personas/ | wc -l)" && \
test ! -d .agents && echo ".agents/ does not exist yet"
```

Expected: `73 / 49 / 2 / 49 / .agents/ does not exist yet`.

- [ ] **Step 2: Run the atomic restructure script**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && \
mkdir -p .agents/skills && \
\
echo "--- moving 73 workflow skills ---" && \
for f in .codex/prompts/*.md; do
  base=$(basename "$f" .md)
  case "$base" in
    agent-*) continue ;;
    validate-assets|validate-skill-change) continue ;;
  esac
  mkdir -p ".agents/skills/$base" && \
  mv "$f" ".agents/skills/$base/SKILL.md"
done && \
\
echo "--- moving 49 agent wrappers ---" && \
for f in .codex/prompts/agent-*.md; do
  base=$(basename "$f" .md)
  mkdir -p ".agents/skills/$base" && \
  mv "$f" ".agents/skills/$base/SKILL.md"
done && \
\
echo "--- collocating 49 personas ---" && \
for p in .codex/personas/*.md; do
  slug=$(basename "$p" .md)
  dest=".agents/skills/agent-$slug/persona.md"
  if [ -d ".agents/skills/agent-$slug" ]; then
    mv "$p" "$dest"
  else
    echo "WARNING: no wrapper dir for $slug — persona orphaned"
  fi
done && \
\
echo "--- moving 2 validators ---" && \
mkdir -p .agents/skills/validate-assets .agents/skills/validate-skill-change && \
mv .codex/prompts/validate-assets.md .agents/skills/validate-assets/SKILL.md && \
mv .codex/prompts/validate-skill-change.md .agents/skills/validate-skill-change/SKILL.md && \
\
echo "--- rewriting wrapper persona-path refs ---" && \
for f in .agents/skills/agent-*/SKILL.md; do
  dir=$(dirname "$f")
  slug=$(basename "$dir")
  persona_slug=${slug#agent-}
  sed -i "s|\`\.codex/personas/${persona_slug}\.md\`|\`persona.md\`|g" "$f"
done && \
\
echo "--- injecting required name: field into frontmatter ---" && \
for f in .agents/skills/*/SKILL.md; do
  slug=$(basename "$(dirname "$f")")
  # Insert 'name: <slug>' as the second line (right after opening ---).
  # Only if not already present (idempotent).
  if ! head -10 "$f" | grep -qE "^name:\s"; then
    sed -i "1a name: $slug" "$f"
  fi
done && \
\
echo "--- removing now-empty source dirs ---" && \
rmdir .codex/prompts .codex/personas 2>/dev/null && \
\
echo "RESTRUCTURE_DONE"
```

Expected output ends with `RESTRUCTURE_DONE`. If `WARNING: no wrapper dir for X — persona orphaned` appears anywhere, halt and investigate before proceeding.

- [ ] **Step 3: Verify counts after restructure**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && \
echo "workflow skills: $(find .agents/skills -mindepth 1 -maxdepth 1 -type d ! -name 'agent-*' ! -name 'validate-*' | wc -l)" && \
echo "agent wrappers: $(find .agents/skills -mindepth 1 -maxdepth 1 -type d -name 'agent-*' | wc -l)" && \
echo "validators: $(find .agents/skills -mindepth 1 -maxdepth 1 -type d -name 'validate-*' | wc -l)" && \
echo "personas (collocated): $(find .agents/skills/agent-*/persona.md -type f 2>/dev/null | wc -l)" && \
echo "total SKILL.md: $(find .agents/skills -name SKILL.md | wc -l)" && \
test ! -d .codex/prompts && echo ".codex/prompts removed" && \
test ! -d .codex/personas && echo ".codex/personas removed"
```

Expected:
```
workflow skills: 73
agent wrappers: 49
validators: 2
personas (collocated): 49
total SKILL.md: 124
.codex/prompts removed
.codex/personas removed
```

- [ ] **Step 4: Verify wrapper persona-path rewrite worked**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && \
echo "wrappers still referencing old path:" && \
grep -rln "\.codex/personas/" .agents/skills/ 2>/dev/null | wc -l && \
echo "wrappers correctly referencing collocated persona.md:" && \
grep -rln "Read \`persona\.md\`" .agents/skills/agent-*/SKILL.md 2>/dev/null | wc -l
```

Expected: `0` (no old refs) and `49` (collocated refs).

- [ ] **Step 4b: Verify every SKILL.md has the required `name:` frontmatter field**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && \
echo "SKILL.md files WITHOUT name: (must be 0):" && \
missing=0; \
for f in .agents/skills/*/SKILL.md; do
  head -10 "$f" | grep -qE "^name:\s" || { echo "$f"; missing=$((missing+1)); }
done; echo "total missing: $missing" && \
echo "" && \
echo "sample: name fields in first 3 skills" && \
for f in $(ls .agents/skills/*/SKILL.md | head -3); do
  slug=$(basename "$(dirname "$f")")
  name=$(head -5 "$f" | grep "^name:" | sed 's/name:\s*//')
  echo "  dir=$slug  frontmatter_name=$name"
done
```

Expected: `total missing: 0`, and each sample shows `dir == frontmatter_name`.

- [ ] **Step 5: Spot-check one wrapper and one workflow skill**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && \
echo "=== game-designer wrapper SKILL.md ===" && \
head -15 .agents/skills/agent-game-designer/SKILL.md && \
echo "=== game-designer persona.md (collocated) ===" && \
head -5 .agents/skills/agent-game-designer/persona.md && \
echo "=== start workflow SKILL.md ===" && \
head -10 .agents/skills/start/SKILL.md
```

Expected: frontmatter + body intact; wrapper says `Read \`persona.md\``; persona.md and SKILL.md both have valid `---` frontmatter blocks.

- [ ] **Step 6: Commit (note: docs not yet updated — they will be in Phase B; this commit captures only the file moves)**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && \
git add -A .agents .codex/prompts .codex/personas && \
git commit -m "refactor(codex): move prompts and personas to .agents/skills/<name>/SKILL.md layout"
```

---

## Task 2: Parallel doc updates (Wave B)

The next 8 sub-tasks touch DIFFERENT files and can be dispatched in parallel (single message with multiple tool calls). DO NOT commit individually — commit them all together at the end of Task 3.

**Files modified by this task:**
- `README.md`
- `AGENTS.md`
- `docs/codex/README.md`
- `docs/codex/hooks.md`
- `.codex/hooks/validate-skill-change.sh`
- `.codex/config.toml`
- `src/AGENTS.md`, `docs/AGENTS.md`, `CCGS Skill Testing Framework/AGENTS.md` (any of these that reference `.codex/prompts/`)

### Task 2.1: README.md path + invocation rewrites

- [ ] **Step 1: Verify baseline (refs that need to change)**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && \
grep -nE "\.codex/(prompts|personas)/|/agent-|Type \`/\` in Codex CLI" README.md | head -10
```

You should see badge link, "Slash Commands" intro, and "Persona wrappers" line.

- [ ] **Step 2: Update README.md — 4 specific edits**

**Edit 2.1a — badge link.** Find:

```
  <a href=".codex/prompts"><img src="https://img.shields.io/badge/prompts-73-green" alt="73 Prompts"></a>
```

Replace with:

```
  <a href=".agents/skills"><img src="https://img.shields.io/badge/skills-124-green" alt="124 Skills"></a>
```

Also find:

```
  <a href=".codex/personas"><img src="https://img.shields.io/badge/personas-49-blueviolet" alt="49 Personas"></a>
```

Delete that entire line (personas are now collocated inside agent-* skill dirs; the count is captured in the skills badge).

**Edit 2.1b — What's Included table.** Find the two rows:

```
| **Personas** | 49 | Specialized agent prompts across design, programming, art, audio, narrative, QA, and production. Invoke with `/agent-<slug>`. |
| **Prompts** | 73 | Slash-prompts for every workflow phase (`/start`, `/design-system`, `/create-epics`, `/create-stories`, `/dev-story`, `/story-done`, etc.) |
```

Replace with this single row:

```
| **Skills** | 124 | 73 workflow skills + 49 persona-adopting skills. Invoke with `$<skill-name>` (e.g. `$start`, `$agent-game-designer`) or describe the task and let Codex auto-select. All live under `.agents/skills/<name>/SKILL.md`. |
```

**Edit 2.1c — Slash Commands intro.** Find:

```
Type `/` in Codex CLI to access all 73 workflow prompts plus 49 `/agent-*` persona wrappers:
```

Replace with:

```
Skills under `.agents/skills/` are invoked with the `$` prefix (e.g. `$start`, `$brainstorm`, `$agent-game-designer`). The `/` prefix is reserved for built-in Codex CLI commands (`/hooks`, `/model`, `/review`, `/quit`). Codex can also auto-select a skill when you describe a task in natural language.
```

**Edit 2.1d — replace every `/skill-name` example in the Slash Commands sub-headings with `$skill-name`.** Run this sed:

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && \
sed -i -E 's|`/([a-z0-9-]+)`|`$\1`|g' README.md
```

This replaces backtick-wrapped `/foo` with backtick-wrapped `$foo` across the file. Verify it does not touch built-in commands like `/hooks` (it WILL touch them — they're also backtick-wrapped). Manually re-fix the built-in commands afterward:

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && \
sed -i \
  -e 's|`\$hooks`|`/hooks`|g' \
  -e 's|`\$model`|`/model`|g' \
  -e 's|`\$review`|`/review`|g' \
  -e 's|`\$quit`|`/quit`|g' \
  -e 's|`\$copy`|`/copy`|g' \
  -e 's|`\$statusline`|`/statusline`|g' \
  README.md
```

- [ ] **Step 3: Verify**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && \
  ! grep -q "\.codex/prompts" README.md && \
  ! grep -q "\.codex/personas" README.md && \
  grep -q "\.agents/skills" README.md && \
  grep -q "Skills under \`\.agents/skills/\` are invoked with the \`\$\` prefix" README.md && \
  grep -q "\`/hooks\`" README.md && \
  echo "README_OK"
```

Expected: `README_OK`.

### Task 2.2: AGENTS.md

- [ ] **Step 1: Find paths that need to change**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && \
grep -n -E "\.codex/(prompts|personas)/|agent-<slug>" AGENTS.md
```

- [ ] **Step 2: Update the Codex-Specific Notes section.** Find:

```
- Custom slash-prompts live under `.codex/prompts/`. Type `/` in interactive
  mode to list them. Persona prompts use the `agent-<slug>` prefix
  (e.g. `/agent-game-designer`).
```

Replace with:

```
- Skills live under `.agents/skills/<name>/SKILL.md` (Codex CLI's
  conventional location). Invoke them with the `$` prefix
  (e.g. `$start`, `$agent-game-designer`) or describe the task and let
  Codex auto-select. The `/` prefix is reserved for built-in Codex
  commands (`/hooks`, `/model`, `/review`, `/quit`).
```

- [ ] **Step 3: Verify**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && \
  ! grep -q "\.codex/prompts" AGENTS.md && \
  grep -q "\.agents/skills" AGENTS.md && \
  echo "AGENTS_OK"
```

Expected: `AGENTS_OK`.

### Task 2.3: docs/codex/README.md

- [ ] **Step 1: Find references**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && \
grep -n -E "\.codex/(prompts|personas)/|agent-<slug>|Slash prompts" docs/codex/README.md
```

- [ ] **Step 2: Update the "First run" → step 4 + the "Personas vs prompts" section.**

**Edit 2.3a — First run step 4.** Find:

```
4. Exposes 73 workflow slash-prompts (`/start`, `/brainstorm`, `/dev-story`, …)
   and 49 persona wrappers (`/agent-game-designer`, `/agent-godot-specialist`, …).
```

Replace with:

```
4. Discovers skills under `.agents/skills/`: 73 workflow skills
   (`$start`, `$brainstorm`, `$dev-story`, …) and 49 persona-adopting
   skills (`$agent-game-designer`, `$agent-godot-specialist`, …).
```

**Edit 2.3b — "Type `/` to browse" line.** Find:

```
Type `/` to browse the prompt catalogue. See [hooks.md](hooks.md) for the
full lifecycle-hook reference.
```

Replace with:

```
Invoke skills with the `$` prefix or describe your task in natural language
and Codex auto-selects. `/` is reserved for built-in CLI commands. See
[hooks.md](hooks.md) for the lifecycle-hook reference.
```

**Edit 2.3c — "Personas vs prompts" section.** Find:

```
## Personas vs prompts

- **Slash prompts** under `.codex/prompts/<slug>.md` are workflow tools
  (`/dev-story`, `/architecture-review`, …). They drive a step-by-step process.
- **Persona wrappers** under `.codex/prompts/agent-<slug>.md` instruct Codex
  to adopt the persona body from `.codex/personas/<slug>.md`. Use them when
  you want domain expertise (e.g. `/agent-game-designer` for mechanics design,
  `/agent-godot-shader-specialist` for GLSL questions).
```

Replace with:

```
## Skills

All skills live at `.agents/skills/<name>/SKILL.md`. Two categories:

- **Workflow skills** (`$start`, `$dev-story`, `$architecture-review`, …)
  drive step-by-step processes. The skill body is the SKILL.md itself.
- **Persona-adopting skills** (`$agent-game-designer`,
  `$agent-godot-shader-specialist`, …) consist of two collocated files
  per skill: `SKILL.md` (the wrapper that tells Codex to adopt the
  persona) and `persona.md` (the persona body — voice, constraints,
  collaboration protocol). Use them when you want domain expertise.
```

**Edit 2.3d — "If a workflow that worked under Claude Code…" line.** Find:

```
1. Check `hooks.md` — the event may not be supported.
2. Edit the prompt directly at `.codex/prompts/<slug>.md`.
3. File an issue.
```

Replace with:

```
1. Check `hooks.md` — the event may not be supported.
2. Edit the skill directly at `.agents/skills/<name>/SKILL.md`.
3. File an issue.
```

- [ ] **Step 3: Verify**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && \
  ! grep -q "\.codex/prompts" docs/codex/README.md && \
  ! grep -q "\.codex/personas" docs/codex/README.md && \
  grep -q "\.agents/skills" docs/codex/README.md && \
  echo "DOCS_CODEX_README_OK"
```

Expected: `DOCS_CODEX_README_OK`.

### Task 2.4: docs/codex/hooks.md

- [ ] **Step 1: Find refs**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && \
grep -n "\.codex/prompts" docs/codex/hooks.md
```

- [ ] **Step 2: Update the validate-skill-change row.** Find:

```
| `PostToolUse` | `^(Write\|Edit)$` | `.codex/hooks/validate-skill-change.sh` | Advises running `/skill-test` after edits to `.codex/prompts/`. |
```

Replace with:

```
| `PostToolUse` | `^(Write\|Edit)$` | `.codex/hooks/validate-skill-change.sh` | Advises running `$skill-test` after edits to `.agents/skills/`. |
```

- [ ] **Step 3: Verify**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && \
  ! grep -q "\.codex/prompts" docs/codex/hooks.md && \
  grep -q "\.agents/skills" docs/codex/hooks.md && \
  echo "HOOKS_DOC_OK"
```

Expected: `HOOKS_DOC_OK`.

### Task 2.5: validate-skill-change.sh path regex

- [ ] **Step 1: Find the current regex**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && \
grep -n "\.codex/prompts" .codex/hooks/validate-skill-change.sh
```

- [ ] **Step 2: Update the regex and comments.** Find these three occurrences and replace each:

**Replace 1.** Find:

```bash
# Fires when any file inside .codex/prompts/ is written or edited.
```

Replace with:

```bash
# Fires when any file inside .agents/skills/ is written or edited.
```

**Replace 2.** Find:

```bash
# Only act on files inside .codex/prompts/.
if ! echo "$FILE_PATH" | grep -qE '(^|/)\.codex/prompts/'; then
    exit 0
fi
```

Replace with:

```bash
# Only act on files inside .agents/skills/.
if ! echo "$FILE_PATH" | grep -qE '(^|/)\.agents/skills/'; then
    exit 0
fi
```

**Replace 3.** Find:

```bash
# Extract prompt name: .codex/prompts/[name].md → name
SKILL_NAME=$(echo "$FILE_PATH" \
    | grep -oE '\.codex/prompts/[^/]+\.md' \
    | sed -E 's|\.codex/prompts/||; s|\.md$||')
```

Replace with:

```bash
# Extract skill name: .agents/skills/[name]/SKILL.md → name
SKILL_NAME=$(echo "$FILE_PATH" \
    | grep -oE '\.agents/skills/[^/]+' \
    | sed -E 's|\.agents/skills/||')
```

- [ ] **Step 3: Smoke test**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && \
echo '{"tool_input":{"file_path":".agents/skills/start/SKILL.md"}}' | bash .codex/hooks/validate-skill-change.sh 2>&1 | head -3
```

Expected: prints `=== Skill Modified: start ===` then advisory line.

### Task 2.6: .codex/config.toml comment

- [ ] **Step 1: Find any `.codex/prompts` reference**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && \
grep -n "\.codex/prompts" .codex/config.toml
```

If 0 matches, skip the rest of this sub-task. Otherwise:

- [ ] **Step 2: Update the comment.** Find the block (around line 17-19):

```toml
# Custom slash-prompts under .codex/prompts/<name>.md are auto-discovered by
# Codex CLI by convention (no explicit config key). Type `/` in interactive
# mode to list them. Persona prompts use the `agent-<slug>` prefix
# (e.g. `/agent-game-designer`).
```

Replace with:

```toml
# Skills live at .agents/skills/<name>/SKILL.md (Codex CLI auto-discovers).
# Invoke with the $ prefix (e.g. $start, $agent-game-designer) or describe
# the task in natural language. The / prefix is reserved for built-in
# Codex commands.
```

- [ ] **Step 3: Verify TOML still parses**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && \
python -c "import tomllib, pathlib; tomllib.loads(pathlib.Path('.codex/config.toml').read_text()); print('config_ok')"
```

Expected: `config_ok`.

### Task 2.7: Nested AGENTS.md mirrors

- [ ] **Step 1: Find all `.codex/prompts` refs in nested AGENTS.md files**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && \
grep -rn "\.codex/prompts\|\.codex/personas" src/AGENTS.md design/AGENTS.md docs/AGENTS.md "CCGS Skill Testing Framework/AGENTS.md" 2>/dev/null
```

- [ ] **Step 2: For each match, apply the path substitution via sed**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && \
for f in src/AGENTS.md design/AGENTS.md docs/AGENTS.md "CCGS Skill Testing Framework/AGENTS.md"; do
  [ -f "$f" ] || continue
  sed -i \
    -e 's|\.codex/prompts/\[name\]\.md|.agents/skills/[name]/SKILL.md|g' \
    -e 's|\.codex/prompts/|.agents/skills/|g' \
    -e 's|\.codex/personas/|.agents/skills/agent-|g' \
    "$f"
done
```

- [ ] **Step 3: Verify**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && \
  count=$(grep -lE "\.codex/(prompts|personas)" src/AGENTS.md design/AGENTS.md docs/AGENTS.md "CCGS Skill Testing Framework/AGENTS.md" 2>/dev/null | wc -l) && \
  echo "nested files still referencing old paths: $count"
```

Expected: `0`.

### Task 2.8: UPGRADING.md + CONTRIBUTING.md (final sweep)

- [ ] **Step 1: Find any remaining `.codex/prompts` refs**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && \
grep -rn "\.codex/prompts\|\.codex/personas" UPGRADING.md CONTRIBUTING.md 2>/dev/null
```

- [ ] **Step 2: For each match, apply context-aware replacement.**

For CONTRIBUTING.md: prefer Edit operations for clarity since the file is short. Each `.codex/prompts/<name>.md` should become `.agents/skills/<name>/SKILL.md`, and each `.codex/personas/<name>.md` should become `.agents/skills/agent-<name>/persona.md`.

For UPGRADING.md: same substitution. The file is short (1 baseline entry).

Apply via sed:

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && \
sed -i \
  -e 's|\.codex/prompts/<slug>\.md|.agents/skills/<slug>/SKILL.md|g' \
  -e 's|\.codex/prompts/<name>\.md|.agents/skills/<name>/SKILL.md|g' \
  -e 's|\.codex/prompts/|.agents/skills/|g' \
  -e 's|\.codex/personas/|.agents/skills/agent-|g' \
  UPGRADING.md CONTRIBUTING.md
```

- [ ] **Step 3: Verify**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && \
  ! grep -qE "\.codex/(prompts|personas)" UPGRADING.md CONTRIBUTING.md && \
  echo "UPGRADING_CONTRIB_OK"
```

Expected: `UPGRADING_CONTRIB_OK`.

---

## Task 3: Final verification + single commit + push

**Files:**
- No modifications — verification and git push only.

- [ ] **Step 1: Full audit — zero `.codex/prompts` or `.codex/personas` refs anywhere**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && \
echo "=== broken old-path refs anywhere in repo (expect 0) ===" && \
grep -rE "\.codex/(prompts|personas)" \
  README.md AGENTS.md UPGRADING.md CONTRIBUTING.md SECURITY.md \
  docs/codex/ .codex/ \
  src/AGENTS.md design/AGENTS.md docs/AGENTS.md "CCGS Skill Testing Framework/AGENTS.md" \
  2>/dev/null | wc -l
```

Expected: `0`.

- [ ] **Step 2: Counts match expectation**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && \
echo "total SKILL.md files: $(find .agents/skills -name SKILL.md | wc -l)" && \
echo "total persona.md files: $(find .agents/skills -name persona.md | wc -l)" && \
echo "skills with both files (paired): $(find .agents/skills -name 'persona.md' -execdir test -f SKILL.md \; -print | wc -l)" && \
echo "agent skills missing persona.md: $(for d in .agents/skills/agent-*/; do [ -f "$d/persona.md" ] || echo "$d"; done | wc -l)"
```

Expected: `124 / 49 / 49 / 0`.

- [ ] **Step 3: Smoke-test hooks still run**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && \
bash .codex/hooks/session-start.sh 2>&1 | head -2 && \
echo '{"tool_input":{"file_path":".agents/skills/start/SKILL.md"}}' | bash .codex/hooks/validate-skill-change.sh 2>&1 | head -2
```

Expected: SessionStart banner + `=== Skill Modified: start ===`.

- [ ] **Step 4: Verify config.toml parses**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && \
python -c "import tomllib, pathlib; cfg = tomllib.loads(pathlib.Path('.codex/config.toml').read_text()); assert cfg.get('sandbox') == 'workspace-write'; assert 'SessionStart' in cfg['hooks']; print('config_ok')"
```

Expected: `config_ok`.

- [ ] **Step 5: Single combined commit for all Phase B doc updates**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && \
git add README.md AGENTS.md docs/codex/README.md docs/codex/hooks.md \
        .codex/hooks/validate-skill-change.sh .codex/config.toml \
        UPGRADING.md CONTRIBUTING.md \
        src/AGENTS.md docs/AGENTS.md "CCGS Skill Testing Framework/AGENTS.md" 2>/dev/null && \
git commit -m "docs: update all path refs and invocation syntax for .agents/skills/ layout"
```

- [ ] **Step 6: Push to GitHub**

```bash
cd C:/projetos/jogos/Codex-Code-Game-Studios && \
git push origin main && \
git log --oneline -5
```

Expected: 2 new commits visible at top (`refactor(codex):` and `docs:`).

---

## Task 4: User runtime test (manual — by user)

**Files:** none modified.

This task confirms the restructure actually fixed the runtime gap that motivated the plan.

- [ ] **Step 1: User exits and re-opens Codex CLI in WSL**

```bash
# user runs in WSL:
cd /mnt/c/projetos/jogos/Codex-Code-Game-Studios
codex
```

Expected on boot: no new warnings about ignored config keys; hooks still listed as approved from earlier session.

- [ ] **Step 2: User types `$start` inside the Codex session**

Expected: Codex recognizes `$start` and begins the onboarding flow defined in `.agents/skills/start/SKILL.md`. The first response should reference reading the start skill's instructions.

If Codex still says `Unrecognized command`, try `$ start` (with space) or simply describe the task: "begin the onboarding flow" — Codex should auto-detect and invoke the skill.

- [ ] **Step 3: User tests one persona skill**

Type inside Codex:

```
$agent-game-designer
```

Or:

```
adopt the game-designer persona
```

Expected: Codex reads `.agents/skills/agent-game-designer/SKILL.md`, which instructs it to read `persona.md` (collocated) and respond in that persona.

- [ ] **Step 4: User reports back**

Confirm to me whether `$start`, `$agent-<slug>`, or natural-language descriptions successfully trigger the skills. If anything fails, share the exact error message.

---

## Self-Review

**1. Spec coverage:**

- Move 73 workflow skills → Task 1 Step 2 ✓
- Move 49 agent wrappers + 49 personas (collocated) → Task 1 Step 2 ✓
- Move 2 validators → Task 1 Step 2 ✓
- Delete old dirs → Task 1 Step 2 ✓
- Rewrite wrapper persona-path refs → Task 1 Step 2 ✓
- **Inject required `name:` field into every SKILL.md frontmatter** (Codex CLI rejects skills without it per `SkillMetadata.name: String`) → Task 1 Step 2 + verified at Step 4b ✓
- Update README → Task 2.1 ✓
- Update AGENTS.md → Task 2.2 ✓
- Update docs/codex/README.md → Task 2.3 ✓
- Update docs/codex/hooks.md → Task 2.4 ✓
- Update validate-skill-change.sh → Task 2.5 ✓
- Update config.toml → Task 2.6 ✓
- Update nested AGENTS.md → Task 2.7 ✓
- Sweep UPGRADING + CONTRIBUTING → Task 2.8 ✓
- Verify + commit + push → Task 3 ✓
- User runtime test → Task 4 ✓

**2. Placeholder scan:** No `TBD`, no `TODO`, no `implement later`, no `similar to Task N`. Every sed command, regex, and bash chain is spelled out fully. The "If 0 matches, skip" branch in Task 2.6 has a defined fallback (skip) — not a placeholder.

**3. Type consistency:**

- Path constants `.agents/skills/<name>/SKILL.md`, `.agents/skills/agent-<slug>/persona.md` used identically across Tasks 1, 2.1–2.8, 3, 4.
- Invocation prefix `$` (not `/`) used consistently in docs and verify commands.
- Built-in command prefix `/` preserved for `/hooks`, `/model`, `/review`, `/quit`, `/copy`, `/statusline` (re-fix step in Task 2.1d).
- File extension expectations: `SKILL.md` for wrappers, `persona.md` for bodies — same across all tasks.
- Hook script behavior in Task 2.5 matches the smoke-test expectation in Task 3 Step 3.

**Risk note:** Task 1 Step 2 is a single non-rollbackable bash chain (file moves). If interrupted mid-script, the working tree may have half-moved files. Mitigation: `git status` before running shows clean tree (the plan's prerequisite); if interrupted, run `git checkout -- .` to restore — git tracks all the original files.

---

## Parallelism Notes (for executor)

**Phase A (Task 1):** single atomic bash chain — runs sequentially within the script but each `mv` is fast. Total time: ~3-5 seconds for 173 file moves on local SSD.

**Phase B (Task 2.1–2.8):** all 8 sub-tasks touch DIFFERENT files. The recommended execution is **one single message containing 8 parallel tool calls** (mix of Bash + Edit). Specifically:

- 2.1 README.md — Edit (4 separate Edits, but in one subagent or sequential within one shell)
- 2.2 AGENTS.md — Edit
- 2.3 docs/codex/README.md — Edit (4 Edits)
- 2.4 docs/codex/hooks.md — Edit
- 2.5 validate-skill-change.sh — Edit
- 2.6 .codex/config.toml — Edit
- 2.7 nested AGENTS.md mirrors — Bash sed loop
- 2.8 UPGRADING + CONTRIBUTING — Bash sed

Subagents for 2.1 and 2.3 (multi-edit files); inline Edits or Bash for the rest. Total wall-clock: ~30-60 seconds vs ~5-10 minutes sequential.

**Phase C (Task 3):** sequential — verification commands depend on Phase B completion, then single commit + push.

**Phase D (Task 4):** user-driven; cannot run in this session.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-18-restructure-to-agents-skills.md`. Two execution options:

**1. Subagent-Driven (recommended)** — I dispatch fresh subagents in parallel for Tasks 2.1–2.8, then do verification + commit + push inline. Uses `superpowers:subagent-driven-development`.

**2. Inline Execution** — I do everything in this session via `superpowers:executing-plans` with batched parallel tool calls and checkpoints.

Which approach?
