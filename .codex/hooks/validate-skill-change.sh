#!/bin/bash
# Codex post-write validator: advises running skill-test after prompt file changes.
# Fires when any file inside .codex/prompts/ (or legacy .claude/skills/) is written or edited.
# Originally derived from the Claude Code PostToolUse hook in `.claude/hooks/`.
#
# Exit behavior:
#   exit 0 = advisory only (non-blocking)
#
# Input schema (PostToolUse for Write|Edit):
# { "tool_name": "Write", "tool_input": { "file_path": "...", "content": "..." } }

INPUT=$(cat)

# Parse file path -- use jq if available, fall back to grep
if command -v jq >/dev/null 2>&1; then
    FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
else
    FILE_PATH=$(echo "$INPUT" | grep -oE '"file_path"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/"file_path"[[:space:]]*:[[:space:]]*"//;s/"$//')
fi

# Normalize path separators (Windows backslash to forward slash)
FILE_PATH=$(echo "$FILE_PATH" | sed 's|\\|/|g')

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

if [ -z "$SKILL_NAME" ]; then
    exit 0
fi

echo "=== Skill Modified: $SKILL_NAME ===" >&2
echo "Run /skill-test static $SKILL_NAME to validate structural compliance." >&2
echo "====================================" >&2

exit 0
