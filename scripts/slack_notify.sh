#!/bin/bash

# Slack notification script for issue tracking
# Usage: ./scripts/slack_notify.sh "message"

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 \"message\""
    exit 1
fi

MESSAGE="$1"

if [ -z "$WEBHOOK_URL" ]; then
    echo "Warning: WEBHOOK_URL environment variable not set"
    exit 1
fi

# Send notification to Slack
curl -X POST \
    -H 'Content-type: application/json' \
    --data "{\"text\":\"$MESSAGE\"}" \
    "$WEBHOOK_URL" \
    --silent \
    --show-error \
    --fail

if [ $? -eq 0 ]; then
    echo "✅ Slack notification sent successfully"
else
    echo "❌ Failed to send Slack notification"
    exit 1
fi