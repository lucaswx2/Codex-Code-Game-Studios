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
