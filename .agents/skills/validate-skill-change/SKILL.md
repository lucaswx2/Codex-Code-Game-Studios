---
name: validate-skill-change
description: "Validate that a Codex prompt under .agents/skills/ still parses."
---

> Codex slash-prompt. Wraps `.codex/hooks/validate-skill-change.sh`.

Invoke after editing any file under `.agents/skills/`.
The script lints frontmatter and warns about missing description/argument-hint.

Shell command:

```
bash .codex/hooks/validate-skill-change.sh
```
