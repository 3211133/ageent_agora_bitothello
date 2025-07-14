#!/bin/bash

# Notify issue completion
# Usage: ./scripts/notify_issue_complete.sh <issue_number> "Issue Title" "Solution Summary" [commit_hash] [additional_notes]

set -e

if [ $# -lt 3 ]; then
    echo "Usage: $0 <issue_number> \"Issue Title\" \"Solution Summary\" [commit_hash] [additional_notes]"
    echo "Example: $0 65 \"Path Traversal Vulnerability\" \"Added file path validation\" \"abc1234\" \"Tests passing\""
    exit 1
fi

ISSUE_NUMBER="$1"
ISSUE_TITLE="$2"
SOLUTION="$3"
COMMIT_HASH="${4:-}"
ADDITIONAL_NOTES="${5:-}"
TIMESTAMP=$(date)

MESSAGE="✅ **Issue Completed** - #${ISSUE_NUMBER}: ${ISSUE_TITLE}
📝 Solution: ${SOLUTION}
🕐 Completed: ${TIMESTAMP}"

if [ -n "$COMMIT_HASH" ]; then
    MESSAGE="${MESSAGE}
🔗 Commit: ${COMMIT_HASH}"
fi

if [ -n "$ADDITIONAL_NOTES" ]; then
    MESSAGE="${MESSAGE}
📊 Notes: ${ADDITIONAL_NOTES}"
fi

./scripts/slack_notify.sh "$MESSAGE"