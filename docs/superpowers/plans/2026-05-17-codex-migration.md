# Codex CLI Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Claude Code-specific tooling in this repository with an OpenAI Codex CLI equivalent so contributors can run the same game-studio workflow under Codex.

**Architecture:** Add an `AGENTS.md` (Codex's project-instruction convention) at the repo root, mirror the runtime configuration under a new `.codex/` tree (`config.toml`, `prompts/`, `personas/`, `hooks/`), translate all 73 skills into Codex custom prompts and all 49 agent definitions into invokable `agent-<slug>` prompts, port the bash hooks that map cleanly (session-start context, pre-commit/pre-push validation), and rewrite the user-facing docs (`README.md`, `UPGRADING.md`, `CLAUDE.md`) so Codex is the supported primary path. The shared content under `design/`, `src/`, `production/`, `docs/`, and `.claude/docs/` stays untouched and is referenced from `AGENTS.md` via Markdown links so both worlds read the same source of truth. Frontmatter shape differences (`allowed-tools`, `model`, `user-invocable` → Codex `description` + `argument-hint`) are handled by a single Python conversion script with a test, not by hand-editing 122 files.

**Tech Stack:** OpenAI Codex CLI (`codex` binary, ≥0.20), TOML config (`.codex/config.toml`), Markdown prompts with YAML frontmatter, Python 3.11 for the one-shot conversion script (uses only stdlib: `pathlib`, `re`, `argparse`, `unittest`), Bash for ported hooks, Git for trunk-based commits with conventional-commit messages.

---

## File Structure

**New files (Codex side):**

- `AGENTS.md` — root-level Codex project instructions; @-includes the same shared docs that `CLAUDE.md` loads.
- `.codex/config.toml` — Codex CLI configuration (sandbox, approval policy, MCP servers, profile, notify).
- `.codex/prompts/<slug>.md` — 73 user-invocable skills, one prompt file per slug (e.g. `start.md`, `brainstorm.md`, `dev-story.md`).
- `.codex/prompts/agent-<slug>.md` — 49 agent-persona prompts (e.g. `agent-game-designer.md`, `agent-godot-specialist.md`). Each prompt instructs the model to adopt the persona file under `.codex/personas/`.
- `.codex/personas/<slug>.md` — 49 verbatim persona bodies (the original `.claude/agents/<slug>.md` content with frontmatter rewritten).
- `.codex/hooks/session-start.sh` — ported context loader, identical to the Claude version but invoked from the new path.
- `.codex/hooks/detect-gaps.sh` — ported documentation-gap detector.
- `.codex/hooks/validate-commit.sh` — pre-commit validator (called by `.git/hooks/pre-commit`).
- `.codex/hooks/validate-push.sh` — pre-push validator (called by `.git/hooks/pre-push`).
- `.codex/hooks/validate-assets.sh` — manual validator invokable via `/validate-assets` prompt.
- `.codex/hooks/validate-skill-change.sh` — manual validator invokable via `/validate-skill-change` prompt.
- `.git/hooks/pre-commit` — small wrapper that calls `.codex/hooks/validate-commit.sh`.
- `.git/hooks/pre-push` — small wrapper that calls `.codex/hooks/validate-push.sh`.
- `tools/migration/convert_claude_to_codex.py` — one-shot conversion script with unit tests.
- `tools/migration/test_convert_claude_to_codex.py` — unit tests for the conversion script.
- `docs/codex/README.md` — Codex-specific operator's guide (install, run, prompts catalogue).
- `docs/codex/hook-mapping.md` — table mapping every original Claude hook to its Codex destination (or `not portable` + rationale).

**Modified files:**

- `CLAUDE.md` — rewritten to a 15-line redirect that points readers at `AGENTS.md`; keeps the existing `.claude/` tree functional for legacy users but stops being the canonical instructions.
- `README.md` — replace the "Built for Claude Code" framing with "Built for OpenAI Codex CLI (Claude Code supported as legacy)"; replace badge URLs; rewrite the *Getting Started* and *Slash Commands* sections.
- `UPGRADING.md` — add a top-of-file *Codex migration* section explaining the new entry points.
- `CONTRIBUTING.md` — replace `claude` invocation snippets with `codex` equivalents.
- `.gitignore` — add `.codex/cache/`, `.codex/sessions/`, `.codex/local.toml`.

**Files NOT modified (shared content, engine-agnostic):**

- All of `design/`, `src/`, `production/`, `tests/`, `tools/` (except the new `tools/migration/` we add).
- All of `.claude/docs/` (referenced from both `CLAUDE.md` and `AGENTS.md`).
- All of `.claude/rules/` (path-scoped coding rules; Codex prompts reference them by path).
- `docs/engine-reference/`, `docs/architecture/`, `docs/registry/`.

The `.claude/agents/`, `.claude/skills/`, `.claude/hooks/`, and `.claude/settings.json` files are **left in place** so existing Claude Code users keep working during the transition. They are marked as legacy in `CLAUDE.md` but not deleted by this plan; a follow-up plan can remove them once the team confirms Codex parity.

---

## Task 1: Set up Codex configuration foundation

**Files:**

- Create: `.codex/config.toml`
- Create: `AGENTS.md`
- Test: manual `codex --print-config` sanity check (no automated test for TOML existence)

- [ ] **Step 1: Create the Codex config file**

Write `.codex/config.toml` with this exact content:

```toml
# OpenAI Codex CLI — project configuration
# Docs: https://github.com/openai/codex/blob/main/codex-rs/config.md

# Default model for this workspace. Override per-session with `codex --model`.
model = "gpt-5-codex"

# Sandbox: workspace-write lets Codex edit files inside this repo but blocks
# changes outside it. Use `danger-full-access` only for hook-port debugging.
sandbox = "workspace-write"

# Approval: on-request means Codex asks before running commands flagged risky
# by the sandbox. Matches the "ask before write" protocol in CLAUDE.md.
approval_policy = "on-request"

# Project prompts directory. Files under .codex/prompts/<name>.md become
# /<name> slash commands inside `codex` interactive mode.
project_prompts_dir = ".codex/prompts"

# Notify: pipe Codex notifications to the legacy notify script so the
# repo's notification UX (toasts, sounds) keeps working.
notify = [".codex/hooks/notify.sh"]

# Lifecycle hooks. Codex CLI invokes these scripts at the matching event;
# unsupported events from the Claude version are documented in
# docs/codex/hook-mapping.md.
[hooks]
session_start = ".codex/hooks/session-start.sh"
pre_commit    = ".codex/hooks/validate-commit.sh"
pre_push      = ".codex/hooks/validate-push.sh"

# MCP servers. Mirror the ones the Claude session expects so /loop, context7,
# etc. keep working. Token-bearing servers should be configured in the user's
# ~/.codex/config.toml, not committed here.
[mcp_servers]
# Example shape — uncomment and fill in per machine:
# [mcp_servers.context7]
# command = "npx"
# args = ["-y", "@upstash/context7-mcp@latest"]
```

- [ ] **Step 2: Create the AGENTS.md root file**

Write `AGENTS.md` with this exact content:

````markdown
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
````

- [ ] **Step 3: Verify both files load**

Run:

```bash
test -f .codex/config.toml && echo "config ok"
test -f AGENTS.md && echo "agents ok"
python -c "import tomllib, pathlib; tomllib.loads(pathlib.Path('.codex/config.toml').read_text())" && echo "toml parses"
```

Expected output:

```
config ok
agents ok
toml parses
```

- [ ] **Step 4: Commit**

```bash
git add .codex/config.toml AGENTS.md
git commit -m "feat: add Codex CLI config and AGENTS.md entry point"
```

---

## Task 2: Build the Claude→Codex conversion script (TDD)

**Files:**

- Create: `tools/migration/convert_claude_to_codex.py`
- Create: `tools/migration/test_convert_claude_to_codex.py`
- Test: `tools/migration/test_convert_claude_to_codex.py`

This script is the workhorse for the bulk frontmatter rewriting in Tasks 3 and 4. Build it test-first so we catch frontmatter edge cases before touching 122 real files.

- [ ] **Step 1: Write the failing tests**

Create `tools/migration/test_convert_claude_to_codex.py`:

```python
"""Unit tests for the Claude→Codex frontmatter converter."""
import unittest
from convert_claude_to_codex import convert_skill, convert_agent


class ConvertSkillTests(unittest.TestCase):
    def test_strips_claude_only_fields_and_keeps_description(self):
        src = (
            "---\n"
            "name: brainstorm\n"
            'description: "Guided game concept ideation."\n'
            'argument-hint: "[hint]"\n'
            "user-invocable: true\n"
            "allowed-tools: Read, Write, Task\n"
            "model: sonnet\n"
            "---\n"
            "\n"
            "Body line one.\n"
        )
        result = convert_skill(src, slug="brainstorm")
        self.assertIn('description: "Guided game concept ideation."', result)
        self.assertIn('argument-hint: "[hint]"', result)
        self.assertNotIn("allowed-tools", result)
        self.assertNotIn("user-invocable", result)
        self.assertNotIn("model: sonnet", result)
        self.assertIn("Body line one.", result)

    def test_adds_codex_banner_under_frontmatter(self):
        src = "---\nname: x\ndescription: y\n---\n\nbody\n"
        result = convert_skill(src, slug="x")
        self.assertIn("> Codex slash-prompt", result)
        self.assertIn("Originally derived from `.claude/skills/x/SKILL.md`", result)

    def test_rewrites_task_tool_references(self):
        src = (
            "---\nname: t\ndescription: d\nallowed-tools: Task\n---\n"
            "Spawn a Task agent for X.\n"
        )
        result = convert_skill(src, slug="t")
        self.assertNotIn("Task agent", result)
        self.assertIn("ask the user to invoke /agent-", result)


class ConvertAgentTests(unittest.TestCase):
    def test_keeps_description_and_drops_claude_fields(self):
        src = (
            "---\n"
            "name: game-designer\n"
            'description: "Owns mechanical design."\n'
            "tools: Read, Write, Edit\n"
            "model: sonnet\n"
            "maxTurns: 20\n"
            "skills: [design-review, balance-check]\n"
            "memory: project\n"
            "---\n"
            "You are the Game Designer.\n"
        )
        result = convert_agent(src, slug="game-designer")
        self.assertIn('description: "Owns mechanical design."', result)
        self.assertNotIn("maxTurns", result)
        self.assertNotIn("memory: project", result)
        self.assertIn("You are the Game Designer.", result)

    def test_persona_wrapper_includes_slug_in_invocation_hint(self):
        src = "---\nname: writer\ndescription: d\n---\nBody.\n"
        result = convert_agent(src, slug="writer")
        self.assertIn("/agent-writer", result)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
cd tools/migration && python -m unittest test_convert_claude_to_codex.py -v
```

Expected: `ModuleNotFoundError: No module named 'convert_claude_to_codex'` (the implementation file does not exist yet).

- [ ] **Step 3: Write the minimal implementation**

Create `tools/migration/convert_claude_to_codex.py`:

```python
"""Convert Claude Code skill and agent files into Codex prompt/persona files.

Usage:
    python convert_claude_to_codex.py skills <claude_skills_dir> <codex_prompts_dir>
    python convert_claude_to_codex.py agents <claude_agents_dir> <codex_personas_dir> <codex_prompts_dir>

The skill mode reads each `<dir>/<slug>/SKILL.md`, rewrites the frontmatter, and
writes `<codex_prompts_dir>/<slug>.md`.

The agent mode reads each `<dir>/<slug>.md`, copies the persona body verbatim
(with rewritten frontmatter) to `<codex_personas_dir>/<slug>.md`, then writes a
thin wrapper at `<codex_prompts_dir>/agent-<slug>.md` that tells the model to
adopt the persona.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

CLAUDE_ONLY_SKILL_FIELDS = {
    "name", "user-invocable", "allowed-tools", "model", "disallowedTools",
    "maxTurns", "memory", "skills",
}
CLAUDE_ONLY_AGENT_FIELDS = {
    "name", "tools", "model", "maxTurns", "disallowedTools", "skills", "memory",
}

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def _split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    block = match.group(1)
    body = text[match.end():]
    fields: dict[str, str] = {}
    for line in block.splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return fields, body


def _render_frontmatter(fields: dict[str, str]) -> str:
    if not fields:
        return ""
    rendered = ["---"]
    for key, value in fields.items():
        rendered.append(f"{key}: {value}")
    rendered.append("---\n")
    return "\n".join(rendered)


def convert_skill(source: str, *, slug: str) -> str:
    fields, body = _split_frontmatter(source)
    kept = {
        key: value
        for key, value in fields.items()
        if key not in CLAUDE_ONLY_SKILL_FIELDS
    }
    body = body.replace("Task agent", "user-invoked agent prompt")
    body = re.sub(
        r"spawn\s+a\s+Task\s+(?:tool|call)",
        "ask the user to invoke /agent-<slug>",
        body,
        flags=re.IGNORECASE,
    )
    banner = (
        f"> Codex slash-prompt. Originally derived from "
        f"`.claude/skills/{slug}/SKILL.md`.\n\n"
    )
    return _render_frontmatter(kept) + "\n" + banner + body


def convert_agent(source: str, *, slug: str) -> str:
    fields, body = _split_frontmatter(source)
    kept = {
        key: value
        for key, value in fields.items()
        if key not in CLAUDE_ONLY_AGENT_FIELDS
    }
    banner = (
        f"> Codex persona. Invoke via `/agent-{slug}` from the project prompts.\n"
        f"> Originally derived from `.claude/agents/{slug}.md`.\n\n"
    )
    return _render_frontmatter(kept) + "\n" + banner + body


def _wrapper_prompt(slug: str, description: str) -> str:
    return (
        f"---\n"
        f"description: {description}\n"
        f"---\n\n"
        f"> Codex agent wrapper. Adopt the persona defined in "
        f"`.codex/personas/{slug}.md` and follow its collaboration protocol.\n\n"
        f"Read `.codex/personas/{slug}.md` first, then respond to the user's "
        f"request in that persona. Stay within the persona's tool and scope "
        f"constraints. If the request is outside the persona's domain, name "
        f"the persona that should handle it instead.\n"
    )


def _convert_skills_dir(claude_dir: pathlib.Path, codex_dir: pathlib.Path) -> int:
    codex_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for skill_dir in sorted(claude_dir.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            continue
        slug = skill_dir.name
        converted = convert_skill(skill_md.read_text(encoding="utf-8"), slug=slug)
        (codex_dir / f"{slug}.md").write_text(converted, encoding="utf-8")
        count += 1
    return count


def _convert_agents_dir(
    claude_dir: pathlib.Path,
    personas_dir: pathlib.Path,
    prompts_dir: pathlib.Path,
) -> int:
    personas_dir.mkdir(parents=True, exist_ok=True)
    prompts_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for agent_md in sorted(claude_dir.glob("*.md")):
        slug = agent_md.stem
        source = agent_md.read_text(encoding="utf-8")
        persona = convert_agent(source, slug=slug)
        (personas_dir / f"{slug}.md").write_text(persona, encoding="utf-8")
        fields, _ = _split_frontmatter(source)
        description = fields.get("description", '"Game studio persona."')
        wrapper = _wrapper_prompt(slug, description)
        (prompts_dir / f"agent-{slug}.md").write_text(wrapper, encoding="utf-8")
        count += 1
    return count


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="mode", required=True)
    skills = sub.add_parser("skills")
    skills.add_argument("claude_dir", type=pathlib.Path)
    skills.add_argument("codex_dir", type=pathlib.Path)
    agents = sub.add_parser("agents")
    agents.add_argument("claude_dir", type=pathlib.Path)
    agents.add_argument("personas_dir", type=pathlib.Path)
    agents.add_argument("prompts_dir", type=pathlib.Path)
    args = parser.parse_args(argv)
    if args.mode == "skills":
        n = _convert_skills_dir(args.claude_dir, args.codex_dir)
        print(f"converted {n} skills")
    else:
        n = _convert_agents_dir(args.claude_dir, args.personas_dir, args.prompts_dir)
        print(f"converted {n} agents")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

- [ ] **Step 4: Run tests to verify they pass**

Run:

```bash
cd tools/migration && python -m unittest test_convert_claude_to_codex.py -v
```

Expected: `OK` with 5 tests passing (`test_strips_claude_only_fields_and_keeps_description`, `test_adds_codex_banner_under_frontmatter`, `test_rewrites_task_tool_references`, `test_keeps_description_and_drops_claude_fields`, `test_persona_wrapper_includes_slug_in_invocation_hint`).

- [ ] **Step 5: Commit**

```bash
git add tools/migration/convert_claude_to_codex.py tools/migration/test_convert_claude_to_codex.py
git commit -m "feat(migration): add Claude->Codex frontmatter converter with tests"
```

---

## Task 3: Convert 73 skills to Codex prompts

**Files:**

- Create: `.codex/prompts/<slug>.md` × 73 (generated by the script)
- Read: `.claude/skills/*/SKILL.md` × 73 (unchanged inputs)
- Test: spot-check 3 representative prompts

- [ ] **Step 1: Run the converter in skills mode**

From the repo root:

```bash
python tools/migration/convert_claude_to_codex.py skills .claude/skills .codex/prompts
```

Expected output: `converted 73 skills`

- [ ] **Step 2: Verify the count matches**

Run:

```bash
ls .codex/prompts/ | grep -v '^agent-' | wc -l
```

Expected: `73`

- [ ] **Step 3: Spot-check three converted prompts**

Run (Windows Git Bash):

```bash
head -10 .codex/prompts/start.md
echo "---"
head -10 .codex/prompts/brainstorm.md
echo "---"
head -10 .codex/prompts/dev-story.md
```

Expected: each output starts with `---`, contains a `description:` line, contains an `argument-hint:` line, does **not** contain `allowed-tools`, `model:`, or `user-invocable`, and includes the banner `> Codex slash-prompt. Originally derived from ...`.

If a prompt is missing the banner or still has `allowed-tools`, the converter has a bug — return to Task 2 and add a regression test before fixing.

- [ ] **Step 4: Sanity-check that Task-tool references were rewritten**

Run:

```bash
grep -l "Task agent" .codex/prompts/ || echo "no Task agent references remain"
```

Expected: `no Task agent references remain`

- [ ] **Step 5: Commit**

```bash
git add .codex/prompts
git commit -m "feat(codex): port 73 Claude skills to Codex custom prompts"
```

---

## Task 4: Convert 49 agents to Codex personas + wrapper prompts

**Files:**

- Create: `.codex/personas/<slug>.md` × 49
- Create: `.codex/prompts/agent-<slug>.md` × 49
- Read: `.claude/agents/<slug>.md` × 49 (unchanged inputs)

- [ ] **Step 1: Run the converter in agents mode**

From the repo root:

```bash
python tools/migration/convert_claude_to_codex.py agents .claude/agents .codex/personas .codex/prompts
```

Expected output: `converted 49 agents`

- [ ] **Step 2: Verify counts**

Run:

```bash
ls .codex/personas/ | wc -l
ls .codex/prompts/ | grep '^agent-' | wc -l
```

Expected: `49` and `49`.

- [ ] **Step 3: Spot-check one persona and one wrapper**

Run:

```bash
head -15 .codex/personas/game-designer.md
echo "---WRAPPER---"
cat .codex/prompts/agent-game-designer.md
```

Expected:

- The persona starts with `---`, has a `description:` line, has no `tools:`, `model:`, `maxTurns:`, `memory:`, or `skills:` fields, and includes the banner `> Codex persona. Invoke via /agent-game-designer ...`.
- The wrapper is short, starts with `---\ndescription: ...\n---`, contains the line `Read \`.codex/personas/game-designer.md\` first`, and includes the slug `agent-game-designer` in its body.

- [ ] **Step 4: Commit**

```bash
git add .codex/personas .codex/prompts
git commit -m "feat(codex): port 49 Claude agents to Codex personas with wrapper prompts"
```

---

## Task 5: Port the session-start context hook

**Files:**

- Create: `.codex/hooks/session-start.sh`
- Read: `.claude/hooks/session-start.sh` (unchanged input)

The original hook prints branch, recent commits, active sprint, milestone, bug count, and TODO/FIXME counts. Codex CLI runs the configured `session_start` hook on session boot. We copy the script verbatim but flip its banner so the user can tell which CLI emitted it.

- [ ] **Step 1: Copy the script body**

Read `.claude/hooks/session-start.sh` and write `.codex/hooks/session-start.sh` with the same content, except the first echo line:

```bash
echo "=== Codex Code Game Studios — Session Context ==="
```

(Original line was `echo "=== Claude Code Game Studios — Session Context ==="`; change only that string. Everything else — branch detection, sprint detection, bug counts — stays byte-identical.)

- [ ] **Step 2: Make it executable**

Run:

```bash
chmod +x .codex/hooks/session-start.sh
```

- [ ] **Step 3: Smoke-test it manually**

Run:

```bash
bash .codex/hooks/session-start.sh
```

Expected: output begins with `=== Codex Code Game Studios — Session Context ===` and includes a `Branch:` line matching `git rev-parse --abbrev-ref HEAD`.

- [ ] **Step 4: Commit**

```bash
git add .codex/hooks/session-start.sh
git commit -m "feat(codex): port session-start context hook"
```

---

## Task 6: Port the detect-gaps hook

**Files:**

- Create: `.codex/hooks/detect-gaps.sh`
- Read: `.claude/hooks/detect-gaps.sh` (unchanged input)

The original hook checks whether the engine is configured, whether a game concept exists, and whether source code exists, then prints a "fresh project" or "gaps" banner. Codex doesn't have a second SessionStart hook slot, so we chain detect-gaps into session-start via a tail call.

- [ ] **Step 1: Copy detect-gaps.sh verbatim**

Read `.claude/hooks/detect-gaps.sh` and write `.codex/hooks/detect-gaps.sh` with identical content.

- [ ] **Step 2: Make it executable**

```bash
chmod +x .codex/hooks/detect-gaps.sh
```

- [ ] **Step 3: Append a call from session-start.sh**

Edit `.codex/hooks/session-start.sh` and append at the end of the file (after the existing TODO/FIXME block):

```bash

# Chain detect-gaps so Codex gets the same dual-hook behavior the Claude
# SessionStart matcher provided.
if [ -x "$(dirname "$0")/detect-gaps.sh" ]; then
    bash "$(dirname "$0")/detect-gaps.sh"
fi
```

- [ ] **Step 4: Smoke-test the chained call**

```bash
bash .codex/hooks/session-start.sh | tail -20
```

Expected: the tail of the output includes either `🚀 NEW PROJECT:` or a `=== Checking for Documentation Gaps ===` banner from the chained script.

- [ ] **Step 5: Commit**

```bash
git add .codex/hooks/detect-gaps.sh .codex/hooks/session-start.sh
git commit -m "feat(codex): port detect-gaps hook and chain it from session-start"
```

---

## Task 7: Port pre-commit and pre-push validators

**Files:**

- Create: `.codex/hooks/validate-commit.sh`
- Create: `.codex/hooks/validate-push.sh`
- Create: `.git/hooks/pre-commit`
- Create: `.git/hooks/pre-push`
- Read: `.claude/hooks/validate-commit.sh`, `.claude/hooks/validate-push.sh`

The Claude versions parsed PreToolUse JSON from stdin. Git pre-commit hooks receive a different contract (no stdin, no args; staged files via `git diff --cached`). We rewrite the entry shim while keeping the validation logic intact.

- [ ] **Step 1: Write the new validate-commit.sh**

Create `.codex/hooks/validate-commit.sh`:

```bash
#!/bin/bash
# Codex pre-commit validator.
# Invoked by .git/hooks/pre-commit OR by Codex's pre_commit hook.
# No stdin contract — read staged files directly from git.

set -e

STAGED=$(git diff --cached --name-only 2>/dev/null)
if [ -z "$STAGED" ]; then
    exit 0
fi

WARNINGS=""

# Conventional Commits enforcement — only when called as a git hook with
# COMMIT_EDITMSG present.
if [ -n "$1" ] && [ -f "$1" ]; then
    FIRST_LINE=$(head -1 "$1")
    if ! echo "$FIRST_LINE" | grep -qE '^(feat|fix|chore|docs|test|refactor|perf|build|ci|style|revert)(\(.+\))?!?: .+'; then
        WARNINGS+="commit message does not follow Conventional Commits (feat:/fix:/chore:/...).\n"
    fi
fi

# Forbid committing .env files
if echo "$STAGED" | grep -qE '(^|/)\.env'; then
    echo "ERROR: refusing to commit .env files" >&2
    exit 1
fi

# Warn about TODO/FIXME being added
if git diff --cached -U0 | grep -E '^\+.*\b(TODO|FIXME)\b' >/dev/null; then
    WARNINGS+="new TODO/FIXME added in this commit.\n"
fi

if [ -n "$WARNINGS" ]; then
    printf "validate-commit warnings:\n%b" "$WARNINGS" >&2
fi

exit 0
```

- [ ] **Step 2: Write the new validate-push.sh**

Create `.codex/hooks/validate-push.sh`:

```bash
#!/bin/bash
# Codex pre-push validator.
# Invoked by .git/hooks/pre-push (receives remote ref info on stdin) OR by
# Codex's pre_push hook (no stdin). Both paths converge on `git log` lookup.

set -e

REMOTE_BRANCH=$(git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null || echo "")
LOCAL_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Block force-push to protected branches
if [ "$LOCAL_BRANCH" = "main" ] || [ "$LOCAL_BRANCH" = "master" ]; then
    if [ "$GIT_PUSH_OPTION_COUNT" -gt 0 ] 2>/dev/null; then
        for i in $(seq 0 $((GIT_PUSH_OPTION_COUNT - 1))); do
            opt_var="GIT_PUSH_OPTION_$i"
            if [ "${!opt_var}" = "force=true" ]; then
                echo "ERROR: force-push to $LOCAL_BRANCH is blocked" >&2
                exit 1
            fi
        done
    fi
fi

# Warn if pushing without a tracking remote
if [ -z "$REMOTE_BRANCH" ]; then
    echo "validate-push warning: no upstream tracking branch set for $LOCAL_BRANCH" >&2
fi

exit 0
```

- [ ] **Step 3: Write the .git/hooks/pre-commit wrapper**

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Calls the Codex pre-commit validator. Receives $1 = path to COMMIT_EDITMSG
# when invoked as a commit-msg hook; for pre-commit there is no arg.
exec bash .codex/hooks/validate-commit.sh "$@"
```

- [ ] **Step 4: Write the .git/hooks/pre-push wrapper**

Create `.git/hooks/pre-push`:

```bash
#!/bin/bash
exec bash .codex/hooks/validate-push.sh
```

- [ ] **Step 5: Make all four scripts executable**

```bash
chmod +x .codex/hooks/validate-commit.sh .codex/hooks/validate-push.sh
chmod +x .git/hooks/pre-commit .git/hooks/pre-push
```

- [ ] **Step 6: Smoke-test the pre-commit hook**

```bash
echo "test" >> README.md
git add README.md
bash .git/hooks/pre-commit && echo "pre-commit ok"
git checkout README.md
```

Expected output: `pre-commit ok` (no warnings, no errors).

- [ ] **Step 7: Commit**

```bash
git add .codex/hooks/validate-commit.sh .codex/hooks/validate-push.sh
# Note: .git/hooks/ is NOT versioned; commit only the codex scripts.
git commit -m "feat(codex): port pre-commit and pre-push validators"
```

(`.git/hooks/pre-commit` and `.git/hooks/pre-push` are intentionally not committed — they are per-clone shims. Task 14 documents their installation in `docs/codex/README.md`.)

---

## Task 8: Port the remaining validators as manual prompts

**Files:**

- Create: `.codex/hooks/validate-assets.sh`
- Create: `.codex/hooks/validate-skill-change.sh`
- Create: `.codex/hooks/notify.sh`
- Create: `.codex/prompts/validate-assets.md`
- Create: `.codex/prompts/validate-skill-change.md`
- Read: `.claude/hooks/validate-assets.sh`, `.claude/hooks/validate-skill-change.sh`, `.claude/hooks/notify.sh`

Codex doesn't have a Claude-equivalent `PostToolUse(Write|Edit)` hook, so these become manually invokable via slash prompts.

- [ ] **Step 1: Copy the three scripts verbatim**

Copy each of `.claude/hooks/validate-assets.sh`, `.claude/hooks/validate-skill-change.sh`, `.claude/hooks/notify.sh` into `.codex/hooks/` with identical content (no edits — the logic is post-event reporting, not Claude-API specific).

- [ ] **Step 2: Make them executable**

```bash
chmod +x .codex/hooks/validate-assets.sh .codex/hooks/validate-skill-change.sh .codex/hooks/notify.sh
```

- [ ] **Step 3: Create the validate-assets prompt**

Write `.codex/prompts/validate-assets.md`:

```markdown
---
description: "Run asset-pipeline validation on the current working tree."
---

> Codex slash-prompt. Wraps `.codex/hooks/validate-assets.sh`.

Run the asset-pipeline validator and report any violations grouped by severity.

Shell command to invoke (you must read its output and surface findings):

```
bash .codex/hooks/validate-assets.sh
```

If the script exits non-zero, treat each line of stderr as a violation and
ask the user how they want to proceed (fix now, defer, suppress).
```

- [ ] **Step 4: Create the validate-skill-change prompt**

Write `.codex/prompts/validate-skill-change.md`:

```markdown
---
description: "Validate that a Codex prompt under .codex/prompts/ still parses."
---

> Codex slash-prompt. Wraps `.codex/hooks/validate-skill-change.sh`.

Invoke after editing any file under `.codex/prompts/` or `.codex/personas/`.
The script lints frontmatter and warns about missing description/argument-hint.

Shell command:

```
bash .codex/hooks/validate-skill-change.sh
```
```

- [ ] **Step 5: Smoke-test both scripts**

```bash
bash .codex/hooks/validate-assets.sh; echo "exit=$?"
bash .codex/hooks/validate-skill-change.sh; echo "exit=$?"
```

Expected: both exit `0` on a clean tree (they may print informational lines but not errors).

- [ ] **Step 6: Commit**

```bash
git add .codex/hooks/validate-assets.sh .codex/hooks/validate-skill-change.sh .codex/hooks/notify.sh .codex/prompts/validate-assets.md .codex/prompts/validate-skill-change.md
git commit -m "feat(codex): port asset/skill validators as manual prompts"
```

---

## Task 9: Document hooks that do not port

**Files:**

- Create: `docs/codex/hook-mapping.md`

The Claude version has 12 hooks; Codex CLI supports a smaller set. Document each original hook and its Codex destination so future maintainers know what changed.

- [ ] **Step 1: Write the mapping document**

Create `docs/codex/hook-mapping.md`:

```markdown
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
```

- [ ] **Step 2: Commit**

```bash
git add docs/codex/hook-mapping.md
git commit -m "docs(codex): map every Claude hook to its Codex destination"
```

---

## Task 10: Write the Codex operator's guide

**Files:**

- Create: `docs/codex/README.md`

- [ ] **Step 1: Write the guide**

Create `docs/codex/README.md`:

```markdown
# Codex Operator's Guide

This repository was originally built for Claude Code and is now also supported
under [OpenAI Codex CLI](https://github.com/openai/codex). Codex is the
recommended path going forward; the legacy `.claude/` tree still works for
contributors who prefer Claude Code.

## Install

```bash
npm install -g @openai/codex
# or, on macOS:
brew install --cask codex
```

You also need an OpenAI API key with Codex access:

```bash
export OPENAI_API_KEY=sk-...
```

## First run

```bash
cd Codex-Code-Game-Studios
codex
```

On startup, Codex:

1. Reads `AGENTS.md` for project instructions.
2. Loads `.codex/config.toml` (sandbox, approval policy, project prompts).
3. Runs `.codex/hooks/session-start.sh` which prints branch/sprint/milestone
   context and chains `detect-gaps.sh`.
4. Exposes 73 skill prompts (`/start`, `/brainstorm`, `/dev-story`, …) and
   49 persona wrappers (`/agent-game-designer`, `/agent-godot-specialist`, …).

Type `/` to browse the prompt catalogue.

## Git hooks (one-time, per clone)

The pre-commit and pre-push validators are not auto-installed — symlink them:

```bash
ln -s ../../.codex/hooks/validate-commit.sh .git/hooks/pre-commit
ln -s ../../.codex/hooks/validate-push.sh   .git/hooks/pre-push
chmod +x .git/hooks/pre-commit .git/hooks/pre-push
```

On Windows, create thin `.bat`/`bash` wrappers under `.git/hooks/` that call
the scripts; symlinks may not work without developer mode.

## Personas vs prompts

- **Slash prompts** under `.codex/prompts/<slug>.md` are workflow tools
  (`/dev-story`, `/architecture-review`, …). They drive a step-by-step process.
- **Persona wrappers** under `.codex/prompts/agent-<slug>.md` instruct Codex
  to adopt the persona body from `.codex/personas/<slug>.md`. Use them when
  you want domain expertise (e.g. `/agent-game-designer` for mechanics design,
  `/agent-godot-shader-specialist` for GLSL questions).

## Hook mapping

See [hook-mapping.md](hook-mapping.md) for the full event-by-event mapping
from the Claude version to the Codex version.

## When something is missing

If a workflow that worked under Claude Code does not work under Codex:

1. Check `hook-mapping.md` — the event may not be supported.
2. Check `.codex/prompts/<slug>.md` — the prompt may need a refresh after
   editing `.claude/skills/<slug>/SKILL.md`. Re-run
   `python tools/migration/convert_claude_to_codex.py skills .claude/skills .codex/prompts`.
3. File an issue tagged `codex-parity`.
```

- [ ] **Step 2: Commit**

```bash
git add docs/codex/README.md
git commit -m "docs(codex): add operator's guide"
```

---

## Task 11: Slim CLAUDE.md to a redirect

**Files:**

- Modify: `CLAUDE.md` (lines 1–55, full rewrite)

The legacy Claude tree should keep working, but `CLAUDE.md` should no longer be the canonical source. Replace its body with a short redirect that loads AGENTS.md content.

- [ ] **Step 1: Rewrite CLAUDE.md**

Replace the entire contents of `CLAUDE.md` with:

```markdown
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
```

- [ ] **Step 2: Verify the @-include resolves**

Run:

```bash
grep -c "^@AGENTS.md" CLAUDE.md
test -f AGENTS.md && echo "include target exists"
```

Expected:

```
1
include target exists
```

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "refactor(claude): convert CLAUDE.md to AGENTS.md redirect"
```

---

## Task 12: Update README.md to lead with Codex

**Files:**

- Modify: `README.md` (header, badges, *Getting Started*, *Slash Commands*, *Built for* footer)

- [ ] **Step 1: Rewrite the header block**

Replace lines 1–22 of `README.md` (the centered title, tagline, and badge row) with:

```markdown
<p align="center">
  <h1 align="center">Codex Code Game Studios</h1>
  <p align="center">
    Turn a single Codex CLI session into a full game development studio.
    <br />
    49 personas. 73 prompts. One coordinated AI team.
  </p>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT License"></a>
  <a href=".codex/personas"><img src="https://img.shields.io/badge/personas-49-blueviolet" alt="49 Personas"></a>
  <a href=".codex/prompts"><img src="https://img.shields.io/badge/prompts-73-green" alt="73 Prompts"></a>
  <a href=".codex/hooks"><img src="https://img.shields.io/badge/hooks-7-orange" alt="7 Hooks"></a>
  <a href=".claude/rules"><img src="https://img.shields.io/badge/rules-11-red" alt="11 Rules"></a>
  <a href="https://github.com/openai/codex"><img src="https://img.shields.io/badge/built%20for-OpenAI%20Codex%20CLI-10a37f?logo=openai&logoColor=white" alt="Built for Codex"></a>
  <a href="https://docs.anthropic.com/en/docs/claude-code"><img src="https://img.shields.io/badge/legacy-Claude%20Code-f5f5f5?logo=anthropic" alt="Legacy: Claude Code"></a>
</p>
```

(The hook count drops from 12 to 7 because five events have no Codex equivalent; see `docs/codex/hook-mapping.md`.)

- [ ] **Step 2: Rewrite the "Why This Exists" paragraph**

Find the paragraph starting "Building a game solo with AI is powerful" and replace the two sentences that follow it (the one starting "Claude Code Game Studios solves" and the one starting "The result:") with:

```markdown
**Codex Code Game Studios** solves this by giving your AI session the structure of a real studio. Instead of one general-purpose assistant, you get 49 specialized personas organized into a studio hierarchy — directors who guard the vision, department leads who own their domains, and specialists who do the hands-on work. Each persona has defined responsibilities, escalation paths, and quality gates.

The result: you still make every decision, but now you have a team that asks the right questions, catches mistakes early, and keeps your project organized from first brainstorm to launch. Codex CLI is the primary supported runtime; Claude Code is still wired up for contributors who prefer it.
```

- [ ] **Step 3: Replace the "What's Included" table**

Find the table headed `| Category | Count | Description |` and replace it with:

```markdown
| Category | Count | Description |
|----------|-------|-------------|
| **Personas** | 49 | Specialized agent prompts across design, programming, art, audio, narrative, QA, and production. Invoke with `/agent-<slug>`. |
| **Prompts** | 73 | Slash-prompts for every workflow phase (`/start`, `/design-system`, `/create-epics`, `/create-stories`, `/dev-story`, `/story-done`, etc.) |
| **Hooks** | 7 | Automated validation on session start, commits, pushes, asset changes, plus manual `/validate-*` prompts. See `docs/codex/hook-mapping.md`. |
| **Rules** | 11 | Path-scoped coding standards enforced when editing gameplay, engine, AI, UI, network code, and more |
| **Templates** | 41 | Document templates for GDDs, UX specs, ADRs, sprint plans, HUD design, accessibility, and more |
```

- [ ] **Step 4: Rewrite the "Slash Commands" intro**

Find the line `Type \`/\` in Claude Code to access all 73 skills:` and replace it with:

```markdown
Type `/` in Codex CLI to access all 73 workflow prompts plus 49 `/agent-*` persona wrappers:
```

- [ ] **Step 5: Add a "Getting Started" Codex block**

In the *Getting Started* section, before the existing Claude instructions, add:

```markdown
### Codex CLI (primary)

```bash
npm install -g @openai/codex
export OPENAI_API_KEY=sk-...
git clone <this-repo>
cd Codex-Code-Game-Studios
codex
```

Codex reads `AGENTS.md` and `.codex/config.toml` on startup. See
[`docs/codex/README.md`](docs/codex/README.md) for the full operator's guide.

### Claude Code (legacy)

The original `.claude/` tree still works:

```bash
claude
```

See [`CLAUDE.md`](CLAUDE.md) for the legacy entry point.
```

- [ ] **Step 6: Verify the README still renders**

Run:

```bash
python -c "import pathlib; t=pathlib.Path('README.md').read_text(encoding='utf-8'); assert 'Codex Code Game Studios' in t and '.codex/prompts' in t and 'Built for OpenAI Codex CLI' in t; print('readme ok')"
```

Expected: `readme ok`

- [ ] **Step 7: Commit**

```bash
git add README.md
git commit -m "docs(readme): lead with Codex; mark Claude as legacy"
```

---

## Task 13: Update UPGRADING.md and CONTRIBUTING.md

**Files:**

- Modify: `UPGRADING.md` (prepend new section)
- Modify: `CONTRIBUTING.md` (search/replace CLI invocations)

- [ ] **Step 1: Prepend a Codex migration section to UPGRADING.md**

Read the first 5 lines of `UPGRADING.md` to find the existing top heading, then insert this block immediately after the H1:

```markdown
## Migrating from Claude Code to Codex CLI (2026-05)

If you've been using this repo under Claude Code and want to switch to
OpenAI Codex CLI:

1. `npm install -g @openai/codex` and `export OPENAI_API_KEY=sk-...`
2. From the repo root, run `codex`. It reads `AGENTS.md` (added 2026-05)
   and `.codex/config.toml` automatically.
3. Install the git hooks once per clone:
   ```bash
   ln -s ../../.codex/hooks/validate-commit.sh .git/hooks/pre-commit
   ln -s ../../.codex/hooks/validate-push.sh   .git/hooks/pre-push
   chmod +x .git/hooks/pre-commit .git/hooks/pre-push
   ```
4. Prompts are at `.codex/prompts/<slug>.md` (workflow) and
   `.codex/prompts/agent-<slug>.md` (personas). Type `/` to browse them.
5. Five Claude lifecycle hooks have no Codex equivalent — see
   `docs/codex/hook-mapping.md` for the full table.

The legacy `.claude/` tree is still functional; nothing in this migration
deletes it. A follow-up migration may retire it once Codex parity is
confirmed in production use.

---
```

- [ ] **Step 2: Replace CLI invocations in CONTRIBUTING.md**

In `CONTRIBUTING.md`, replace every occurrence of:

- `claude` (when used as a shell command) → `codex`
- `Claude Code` → `Codex CLI (Codex Code Game Studios)`

Use this command to find candidates first:

```bash
grep -n "claude\|Claude Code" CONTRIBUTING.md
```

Then edit each match in context (some uses of "Claude" refer to the legacy tree and should be preserved verbatim — only change instructions that tell contributors which CLI to launch).

- [ ] **Step 3: Verify changes**

```bash
grep -n "codex" CONTRIBUTING.md UPGRADING.md
grep -c "Codex CLI" CONTRIBUTING.md UPGRADING.md
```

Expected: at least one `codex` line in each file, and at least 2 occurrences of `Codex CLI` across both files.

- [ ] **Step 4: Commit**

```bash
git add UPGRADING.md CONTRIBUTING.md
git commit -m "docs: add Codex migration notes to UPGRADING and CONTRIBUTING"
```

---

## Task 14: Update .gitignore for Codex runtime artifacts

**Files:**

- Modify: `.gitignore`

- [ ] **Step 1: Append Codex paths**

Append the following lines to the end of `.gitignore`:

```
# Codex CLI runtime artifacts
.codex/cache/
.codex/sessions/
.codex/local.toml
```

- [ ] **Step 2: Verify**

```bash
tail -5 .gitignore
```

Expected: the last lines match the block above.

- [ ] **Step 3: Commit**

```bash
git add .gitignore
git commit -m "chore: ignore Codex runtime artifacts"
```

---

## Task 15: End-to-end validation

**Files:**

- None modified (this task only inspects)

- [ ] **Step 1: Check the full file tree**

```bash
test -f AGENTS.md && echo "AGENTS.md ok"
test -f .codex/config.toml && echo "config ok"
test -d .codex/prompts && echo "prompts dir ok"
test -d .codex/personas && echo "personas dir ok"
test -d .codex/hooks && echo "hooks dir ok"
test -f docs/codex/README.md && echo "operator guide ok"
test -f docs/codex/hook-mapping.md && echo "hook map ok"
test -f tools/migration/convert_claude_to_codex.py && echo "converter ok"
```

Expected: 8 `ok` lines.

- [ ] **Step 2: Count prompts and personas**

```bash
ls .codex/prompts/ | grep -v '^agent-' | wc -l
ls .codex/prompts/ | grep '^agent-' | wc -l
ls .codex/personas/ | wc -l
```

Expected: `73`, `49`, `49`. Plus 2 extra prompts (`validate-assets.md`, `validate-skill-change.md`) — so the first count may be `75`. If it is, that is correct.

Adjust expectations: first count should be 73 (skills) + 2 (validators) = `75`.

- [ ] **Step 3: Verify config TOML is valid**

```bash
python -c "import tomllib, pathlib; cfg = tomllib.loads(pathlib.Path('.codex/config.toml').read_text()); assert cfg['sandbox'] == 'workspace-write'; assert '.codex/prompts' in cfg['project_prompts_dir']; print('config ok')"
```

Expected: `config ok`

- [ ] **Step 4: Verify the converter is reproducible**

```bash
rm -rf /tmp/codex-prompts-rerun
python tools/migration/convert_claude_to_codex.py skills .claude/skills /tmp/codex-prompts-rerun
diff -rq .codex/prompts /tmp/codex-prompts-rerun | grep -v '^Only in .codex/prompts: agent-' | grep -v 'validate-assets' | grep -v 'validate-skill-change' || echo "skills reproducible"
```

Expected: `skills reproducible` (the only differences should be the `agent-*` wrappers and the two manual `validate-*` prompts, which we filter out of the diff).

- [ ] **Step 5: Verify all tests still pass**

```bash
cd tools/migration && python -m unittest test_convert_claude_to_codex.py -v
```

Expected: 5 tests, all `ok`.

- [ ] **Step 6: Final commit (no code changes — tag the milestone)**

```bash
git tag -a codex-migration-v1 -m "Codex CLI parity reached for Claude Code Game Studios"
```

(No `git commit` here — Step 5 is the last commit; this step just tags it.)

---

## Task 16: Open follow-up issues for known gaps

**Files:**

- None — this task creates GitHub issues via `gh` (or documents them locally if `gh` is unavailable).

- [ ] **Step 1: Create issue for compaction-hook gap**

```bash
gh issue create --title "Codex parity: no PreCompact/PostCompact equivalent" \
  --body "Claude Code's PreCompact and PostCompact hooks have no Codex equivalent. The file-backed session state in production/session-state/active.md is the workaround. Track here so we revisit when Codex CLI adds a compaction event." \
  --label "codex-parity"
```

If `gh` is not authenticated, write the body to `docs/codex/known-gaps.md` instead:

```bash
cat > docs/codex/known-gaps.md <<'EOF'
# Known Codex parity gaps

- **PreCompact/PostCompact**: no Codex equivalent. Workaround: file-backed session state.
- **SubagentStart/SubagentStop**: no Codex equivalent (no `Task` tool). Persona invocations are user-driven.
- **Stop hook**: no Codex equivalent. Use shell `EXIT` trap if needed.
- **statusline.sh**: Codex CLI has no status-line API. Removed; sprint status surfaces via `/sprint-status` slash-prompt instead.
EOF
git add docs/codex/known-gaps.md
git commit -m "docs(codex): track parity gaps for future revisit"
```

- [ ] **Step 2: Commit any local fallback**

If Step 1 used the local-file fallback, the commit above completes this task. If `gh issue create` ran successfully, no commit is needed.

---

## Self-Review

Run through this checklist after the plan is written and before handing it off.

**1. Spec coverage:**

- AGENTS.md created → Task 1 ✓
- `.codex/config.toml` created → Task 1 ✓
- All 73 skills converted to prompts → Tasks 2 + 3 ✓
- All 49 agents converted to personas + wrappers → Tasks 2 + 4 ✓
- Session-start hook ported → Tasks 5 + 6 ✓
- Pre-commit / pre-push validators ported → Task 7 ✓
- Asset / skill-change validators ported as manual prompts → Task 8 ✓
- Hook mapping documented → Task 9 ✓
- Operator's guide → Task 10 ✓
- CLAUDE.md redirected → Task 11 ✓
- README updated → Task 12 ✓
- UPGRADING + CONTRIBUTING updated → Task 13 ✓
- `.gitignore` for Codex runtime → Task 14 ✓
- End-to-end validation → Task 15 ✓
- Follow-up issue tracking → Task 16 ✓

**2. Placeholder scan:** No `TBD`, no `TODO`, no `implement later`, no `similar to Task N`. Every shell command, every file body, and every test is spelled out in full.

**3. Type consistency:**

- Converter exports `convert_skill`, `convert_agent` — referenced by name in Task 2 tests and in Tasks 3/4 commands.
- CLI subcommand names `skills` and `agents` — consistent across Tasks 2, 3, 4, 15.
- Path constants `.codex/prompts`, `.codex/personas`, `.codex/hooks`, `.codex/config.toml` — consistent across all tasks.
- The `agent-<slug>` prompt-prefix convention is used in Tasks 2, 4, 10, 12, 13, 15.
- Hook count (7) used in README badge and in the hook-mapping table — matches: 4 ported scripts (session-start, detect-gaps chained, validate-commit, validate-push) + 2 manual validators (assets, skill-change) + notify = 7 entries.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-17-codex-migration.md`. Two execution options:

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration.

**2. Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints.

Which approach?
