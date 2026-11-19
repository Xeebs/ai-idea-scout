#!/bin/bash
# Atomically claims today's single shared skill-synthesis slot. The slot is
# shared across BOTH tracks (INFRA + MARKETPLACE) and across both tracks'
# own cycles that day -- at most one new skill gets written system-wide per
# calendar day, no matter how many cycles fire or which track gets there
# first. Exit 0 = claimed (go ahead and spawn exactly one skill-synthesizer
# for your oldest qualifying idea). Exit 1 = already used today by someone.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
QUOTA_FILE="$DIR/.skill-quota.json"
LOCK_FILE="$DIR/.skill-quota.lock"
TODAY="$(date +%F)"

exec 9>"$LOCK_FILE"
flock 9

if [ -f "$QUOTA_FILE" ]; then
    DATE=$(python3 -c "import json;print(json.load(open('$QUOTA_FILE')).get('date',''))" 2>/dev/null || echo "")
    COUNT=$(python3 -c "import json;print(json.load(open('$QUOTA_FILE')).get('count',0))" 2>/dev/null || echo 0)
else
    DATE=""
    COUNT=0
fi

if [ "$DATE" != "$TODAY" ]; then
    COUNT=0
fi

if [ "$COUNT" -ge 1 ]; then
    echo "skill quota already used today ($TODAY) -- skip Phase 4 this cycle" >&2
    exit 1
fi

COUNT=$((COUNT + 1))
python3 -c "import json; json.dump({'date': '$TODAY', 'count': $COUNT}, open('$QUOTA_FILE', 'w'))"
echo "claimed today's skill slot ($TODAY)"
exit 0
