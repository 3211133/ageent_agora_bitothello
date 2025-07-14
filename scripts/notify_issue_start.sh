#!/bin/bash

# Notify issue start
# Usage: ./scripts/notify_issue_start.sh <issue_number> "Issue Title" <priority>

set -e

if [ $# -ne 3 ]; then
    echo "Usage: $0 <issue_number> \"Issue Title\" <priority>"
    echo "Example: $0 65 \"Path Traversal Vulnerability\" \"HIGH\""
    exit 1
fi

ISSUE_NUMBER="$1"
ISSUE_TITLE="$2"
PRIORITY="$3"
TIMESTAMP=$(date)

MESSAGE="🚀 **Issue Started** - #${ISSUE_NUMBER}: ${ISSUE_TITLE}
👤 Assigned: Claude Code
🎯 Priority: ${PRIORITY}
🕐 Started: ${TIMESTAMP}"

./scripts/slack_notify.sh "$MESSAGE"