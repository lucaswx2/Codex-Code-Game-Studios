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


def convert_skill(source: str, *, slug: str) -> str:
    fields, body = _split_frontmatter(source)
    kept = {
        key: value
        for key, value in fields.items()
        if key not in CLAUDE_ONLY_SKILL_FIELDS
    }
    body = re.sub(
        r"spawn\s+a\s+Task\s+(?:tool|call|agent)",
        f"ask the user to invoke /agent-{slug}",
        body,
        flags=re.IGNORECASE,
    )
    body = body.replace("Task agent", f"ask the user to invoke /agent-{slug}")
    body = body.replace("Task tool", f"/agent-{slug} prompt")
    body = re.sub(
        r"\bvia\s+Task\b",
        "via the relevant /agent-<name> Codex prompt",
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
