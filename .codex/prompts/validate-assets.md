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
