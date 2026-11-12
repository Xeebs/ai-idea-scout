#!/bin/bash
# Continuous loop driver -- replaces the old hourly cron trigger. Fires one
# full heartbeat cycle (both tracks in parallel, via heartbeat.sh) and, as
# soon as it finishes, fires the next one immediately rather than waiting
# for the next hour. heartbeat.sh's own lock file still protects against a
# second invocation overlapping (relevant if this loop is ever run alongside
# a leftover cron entry), but under this loop alone it's naturally serial.
set -uo pipefail

REPO="/home/xhasan/my-projects/ai-idea-scout"
GAP_SECONDS=10  # brief pause between cycles -- avoids a tight spin loop on a fast no-op cycle, negligible next to a real cycle's runtime

while true; do
    "$REPO/scripts/heartbeat.sh"
    sleep "$GAP_SECONDS"
done
