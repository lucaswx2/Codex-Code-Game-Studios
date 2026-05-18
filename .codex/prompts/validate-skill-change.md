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
