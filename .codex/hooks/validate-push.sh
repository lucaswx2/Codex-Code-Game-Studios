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
