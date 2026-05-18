"""Convert Claude Code skill and agent files into Codex prompt/persona files.

Usage:
    python convert_claude_to_codex.py skills <claude_skills_dir> <codex_prompts_dir>
    python convert_claude_to_codex.py agents <claude_agents_dir> <codex_personas_dir> <codex_prompts_dir>
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


_CLAUDE_REPLACEMENTS: list[tuple[re.Pattern[str], str]] = [
    # Path rewrites — Claude tree paths to Codex tree paths. Specific first.
    (re.compile(r"\.claude/skills/\*/SKILL\.md"), ".codex/prompts/*.md"),
    (re.compile(r"\.claude/skills/\[([^\]]+)\]/SKILL\.md"),
     r".codex/prompts/[\1].md"),
    (re.compile(r"\.claude/skills/([A-Za-z0-9_-]+)/SKILL\.md"),
     r".codex/prompts/\1.md"),
    (re.compile(r"\.claude/skills/"), ".codex/prompts/"),
    (re.compile(r"\.claude/agents/"), ".codex/personas/"),
    (re.compile(r"\.claude/rules/"), ".codex/rules/"),
    (re.compile(r"\.claude/agent-memory/"), ".codex/persona-memory/"),
    # Brand — apply before tool patterns to avoid double rewriting.
    (re.compile(r"\bClaude Code\b"), "Codex CLI"),
    (re.compile(r"\bClaude session\b"), "Codex session"),
    # Tool: Task — multi-word patterns first, narrow enough to skip English "task".
    (re.compile(
        r"\bTask\s+in\s+this\s+skill\s+spawns?\s+a\s+SUBAGENT\s+[—-]\s+"
        r"a\s+separate\s+independent\s+(?:Claude|Codex)\s+session"
    ), "Each /agent-<name> invocation in this skill runs a separate independent Codex session"),
    (re.compile(r"\bparallel\s+Tasks?\b"), "parallel /agent-<name> invocations"),
    (re.compile(r"\bTask\s+calls?\b"), "/agent-<name> invocations"),
    (re.compile(r"\bTask\s+prompts?\b"), "agent prompt context"),
    (re.compile(r"\bTask\s+tool\b"), "/agent-<name> prompt"),
    (re.compile(r"\bTask\s+subagents?\b"), "/agent-<name> invocation"),
    (re.compile(r"\bvia\s+Task\b", re.IGNORECASE),
     "via the relevant /agent-<name> Codex prompt"),
    (re.compile(r"\bspawn\s+a\s+Task\s+(?:tool|call|agent)\b", re.IGNORECASE),
     "ask the user to invoke /agent-<name>"),
    # Tool: AskUserQuestion — always the Claude tool; safe to replace globally.
    (re.compile(r"`AskUserQuestion`"), "an inline question to the user"),
    (re.compile(r"\bAskUserQuestion\b"), "an inline user question"),
    # Tool: TodoWrite / TaskCreate family — Codex has no native task tracker.
    (re.compile(r"\b(?:TodoWrite|TaskCreate|TaskUpdate|TaskList)\b"),
     "inline progress notes (Codex has no native task tracker)"),
]


def _rewrite_claude_references(text: str) -> str:
    """Rewrite Claude-Code-specific tool and brand mentions to Codex equivalents.

    Conservative: only rewrites multi-word patterns where context unambiguously
    means the Claude tool, never bare ``Task`` (which collides with the English
    word in tables and headings).
    """
    for pattern, replacement in _CLAUDE_REPLACEMENTS:
        text = pattern.sub(replacement, text)
    return text


def convert_skill(source: str, *, slug: str) -> str:
    fields, body = _split_frontmatter(source)
    kept = {
        key: value
        for key, value in fields.items()
        if key not in CLAUDE_ONLY_SKILL_FIELDS
    }
    body = _rewrite_claude_references(body)
    banner = (
        f"> Codex slash-prompt. Originally derived from "
        f"`.claude/skills/{slug}/SKILL.md` (Claude-Code template fork — see "
        f"`docs/codex/README.md`).\n\n"
    )
    return _render_frontmatter(kept) + "\n" + banner + body


def convert_agent(source: str, *, slug: str) -> str:
    fields, body = _split_frontmatter(source)
    kept = {
        key: value
        for key, value in fields.items()
        if key not in CLAUDE_ONLY_AGENT_FIELDS
    }
    body = _rewrite_claude_references(body)
    banner = (
        f"> Codex persona. Invoke via `/agent-{slug}` from the project prompts.\n"
        f"> Originally derived from `.claude/agents/{slug}.md` "
        f"(Claude-Code template fork — see `docs/codex/README.md`).\n\n"
    )
    return _render_frontmatter(kept) + "\n" + banner + body


def rewrite_doc(source: str) -> str:
    """Rewrite a free-form documentation file's Claude-Code references in place."""
    return _rewrite_claude_references(source)


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


def _convert_docs(
    source_dir: pathlib.Path,
    dest_dir: pathlib.Path,
    files: list[str] | None,
) -> int:
    dest_dir.mkdir(parents=True, exist_ok=True)
    targets = files or [path.name for path in sorted(source_dir.glob("*.md"))]
    count = 0
    for filename in targets:
        src = source_dir / filename
        if not src.is_file():
            print(f"skip {filename}: not found", file=sys.stderr)
            continue
        (dest_dir / filename).write_text(
            rewrite_doc(src.read_text(encoding="utf-8")),
            encoding="utf-8",
        )
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
    docs = sub.add_parser("docs")
    docs.add_argument("source_dir", type=pathlib.Path)
    docs.add_argument("dest_dir", type=pathlib.Path)
    docs.add_argument("--files", nargs="+", default=None)
    args = parser.parse_args(argv)
    if args.mode == "skills":
        n = _convert_skills_dir(args.claude_dir, args.codex_dir)
        print(f"converted {n} skills")
    elif args.mode == "agents":
        n = _convert_agents_dir(args.claude_dir, args.personas_dir, args.prompts_dir)
        print(f"converted {n} agents")
    else:
        n = _convert_docs(args.source_dir, args.dest_dir, args.files)
        print(f"rewrote {n} docs")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
