#!/bin/bash
# AI Idea Scout hourly heartbeat — runs exactly one pipeline cycle via Claude Code CLI.
# Designed for unattended execution on an always-on machine (cron).

set -euo pipefail

REPO="/home/xhasan/my-projects/ai-idea-scout"
LOG_DIR="$REPO/logs"
LOG_FILE="$LOG_DIR/heartbeat-$(date +%Y%m%d).log"
CLAUDE="/home/xhasan/.local/bin/claude"
LOCK_FILE="/tmp/ai-idea-scout-heartbeat.lock"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"; }

# Prevent overlapping cycles — a cycle can run long (full last30days run plus
# two analysis passes plus optional skill/publish work); never let the next
# hourly firing start a second one on top of it.
if [ -f "$LOCK_FILE" ]; then
    log "SKIP — previous cycle still running (lock: $LOCK_FILE)"
    exit 0
fi
touch "$LOCK_FILE"
trap 'rm -f "$LOCK_FILE"' EXIT

mkdir -p "$LOG_DIR"

# Rotate logs older than 30 days
find "$LOG_DIR" -name "heartbeat-*.log" -mtime +30 -delete 2>/dev/null || true

log "=== AI Idea Scout heartbeat cycle starting ==="

cd "$REPO"

PROMPT="Run exactly one AI Idea Scout pipeline cycle as defined in CLAUDE.md, end to end, then exit.

Steps:
1. Read pipeline/state.json first and resume from the recorded phase if mid-flight
2. Phase 1: spawn trend-scout for the next topic
3. Phase 2: spawn gap-analyst on the resulting digest
4. Phase 3: spawn idea-synthesizer, then apply the promotion check (PROPOSED -> EXPLORING) directly to ideas/INDEX.md where it applies
5. Phase 4: if any idea qualifies (Format SKILL/BOTH, no skills/<slug>/ yet), spawn skill-synthesizer for the oldest one
6. Phase 5: if any idea is EXPLORING without a published/<slug>.md, spawn publisher
7. Phase 6: close out — update queue.md, changelog.md, write the session note, reset state.json, and commit + push everything Phases 1-4 touched that the publisher did not already push

This is a single invocation, not a long-lived loop -- do not self-pace or schedule a wake-up. Finish the full cycle through the Phase 6 git push, then stop. If genuinely blocked (rate limit, a subagent stuck), write the current phase to pipeline/state.json and exit; the next hourly firing resumes from there."

"$CLAUDE" \
    --dangerously-skip-permissions \
    -p "$PROMPT" \
    2>&1 | tee -a "$LOG_FILE"

log "=== AI Idea Scout heartbeat cycle complete ==="
