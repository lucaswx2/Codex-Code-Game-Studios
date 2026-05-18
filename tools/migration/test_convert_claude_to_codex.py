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
