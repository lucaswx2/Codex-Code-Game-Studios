"""Unit tests for the Claude→Codex frontmatter converter."""
import unittest
from convert_claude_to_codex import convert_skill, convert_agent, rewrite_doc


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

    def test_rewrites_via_task_pattern(self):
        src = (
            "---\nname: x\ndescription: d\n---\n"
            "Spawn the game-designer agent via Task to review the brief.\n"
        )
        result = convert_skill(src, slug="x")
        self.assertNotIn("via Task", result)
        self.assertIn("via the relevant /agent-<name> Codex prompt", result)

    def test_rewrites_task_calls(self):
        src = (
            "---\nname: x\ndescription: d\n---\n"
            "Issue all Task calls simultaneously to avoid serialization.\n"
        )
        result = convert_skill(src, slug="x")
        self.assertNotIn("Task call", result)
        self.assertIn("/agent-<name> invocations", result)

    def test_rewrites_ask_user_question(self):
        src = (
            "---\nname: x\ndescription: d\n---\n"
            "Use `AskUserQuestion` to gather preferences from the user.\n"
        )
        result = convert_skill(src, slug="x")
        self.assertNotIn("AskUserQuestion", result)

    def test_rewrites_claude_code_brand(self):
        src = (
            "---\nname: x\ndescription: d\n---\n"
            "Claude Code reads this file at session start.\n"
        )
        result = convert_skill(src, slug="x")
        self.assertNotIn("Claude Code", result)
        self.assertIn("Codex CLI", result)

    def test_preserves_task_word_in_table_header(self):
        src = (
            "---\nname: x\ndescription: d\n---\n"
            "| Task | Owner | Status |\n| --- | --- | --- |\n"
        )
        result = convert_skill(src, slug="x")
        self.assertIn("| Task | Owner | Status |", result)

    def test_rewrites_skill_paths(self):
        src = (
            "---\nname: x\ndescription: d\n---\n"
            "Glob `.claude/skills/*/SKILL.md`. "
            "Read `.claude/skills/[name]/SKILL.md`. "
            "Look up `.claude/skills/brainstorm/SKILL.md`.\n"
        )
        result = convert_skill(src, slug="x")
        body_only = result.split("Claude-Code template fork", 1)[1]
        self.assertNotIn(".claude/skills/", body_only)
        self.assertIn(".codex/prompts/*.md", body_only)
        self.assertIn(".codex/prompts/[name].md", body_only)
        self.assertIn(".codex/prompts/brainstorm.md", body_only)

    def test_rewrites_docs_path_and_claude_md_filename(self):
        src = (
            "---\nname: x\ndescription: d\n---\n"
            "Read `.claude/docs/director-gates.md` then `.claude/docs/templates/foo.md`. "
            "Refer to CLAUDE.md for project standards.\n"
        )
        result = convert_skill(src, slug="x")
        body_only = result.split("Claude-Code template fork", 1)[1]
        self.assertNotIn(".claude/docs/", body_only)
        self.assertNotIn("CLAUDE.md", body_only)
        self.assertIn("docs/codex/refs/director-gates.md", body_only)
        self.assertIn("docs/codex/refs/templates/foo.md", body_only)
        self.assertIn("AGENTS.md", body_only)

    def test_rewrites_agent_and_rule_paths(self):
        src = (
            "---\nname: x\ndescription: d\n---\n"
            "Definitions live under `.claude/agents/` and rules in `.claude/rules/`.\n"
        )
        result = convert_skill(src, slug="x")
        self.assertNotIn(".claude/agents/", result)
        self.assertNotIn(".claude/rules/", result)
        self.assertIn(".codex/personas/", result)
        self.assertIn(".codex/rules/", result)

    def test_rewrites_todowrite_family(self):
        src = (
            "---\nname: x\ndescription: d\n---\n"
            "Use TodoWrite to track progress; also TaskCreate and TaskList.\n"
        )
        result = convert_skill(src, slug="x")
        self.assertNotIn("TodoWrite", result)
        self.assertNotIn("TaskCreate", result)
        self.assertNotIn("TaskList", result)
        self.assertIn("inline progress notes", result)


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

    def test_agent_body_also_rewrites_claude_references(self):
        src = (
            "---\nname: a\ndescription: d\n---\n"
            "Use `AskUserQuestion` and Claude Code conventions.\n"
        )
        result = convert_agent(src, slug="a")
        self.assertNotIn("AskUserQuestion", result)
        self.assertNotIn("Claude Code", result)
        self.assertIn("Codex CLI", result)


class RewriteDocTests(unittest.TestCase):
    def test_rewrites_brand_in_freeform_doc(self):
        result = rewrite_doc("Claude Code session begins here. Use Task calls.")
        self.assertNotIn("Claude Code", result)
        self.assertIn("Codex CLI", result)
        self.assertIn("/agent-<name> invocations", result)

    def test_preserves_unrelated_content(self):
        src = "## Project Structure\n\nThe /src directory contains source code.\n"
        self.assertEqual(rewrite_doc(src), src)


if __name__ == "__main__":
    unittest.main()
