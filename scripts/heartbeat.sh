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

PROMPT="Read CLAUDE.md's 'Orchestration' section and execute it exactly, for this single hourly firing: dispatch both the INFRA and MARKETPLACE track protocols as parallel subagents (per that section's instructions), wait for both to finish, then exit.

This is a single invocation, not a long-lived loop -- do not self-pace or schedule a wake-up. Each track subagent manages its own resume/retry lifecycle against its own state file (pipeline/state.json for INFRA, marketplace-content/state.json for MARKETPLACE) and does its own git commit + push to its own remote; if one track gets genuinely blocked, let the other still finish and commit normally. Once both have reported back (or you've waited a reasonable time for each), exit."

"$CLAUDE" \
    --dangerously-skip-permissions \
    -p "$PROMPT" \
    2>&1 | tee -a "$LOG_FILE"

log "=== AI Idea Scout heartbeat cycle complete ==="
