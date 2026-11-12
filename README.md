# AI Idea Scout

An autonomous research loop that scans the last 30 days of community discussion (Reddit, X, Hacker News, YouTube, GitHub, web) to find **emerging patterns and ideas that have not yet been fully implemented or tested**, then compiles them into concrete, real-world project ideas with a defined tangible impact on a population of people.

Ideas that are also expressible as a repeatable, prompt-driven task get a real, dual-format Claude Code skill. Ideas that prove recurring or high-impact get promoted to a polished, published writeup.

Two fully independent tracks run **every hour, in parallel** (via subagents, not alternating):
- **INFRA** — AI-builder/agent-infra topics (agentic AI, multi-agent, RAG, MCP, evals, safety), aimed at technical adopters. Output lives in this repo (`research/`, `ideas/`, `skills/`, `published/`).
- **MARKETPLACE** — broad indie-builder/small-business topics (copywriting, freelancing, productivity, SEO, etc.), scored for **Marketplace Fit** and, when HIGH, packaged as an Agensi.io listing draft (zip + price/description suggestion) awaiting human review — the pipeline never lists anything itself. **All of this track's output is private**: it lives in `marketplace-content/`, a separate nested git repo with its own state/queue/changelog, pushed to its own private GitHub remote, never to this public repo. See `marketplace-content/README.md` (not visible here if you're reading this on GitHub — it's local-only).

The two tracks share no mutable files, so running them concurrently every hour is safe — there's nothing for them to race over.

Runs continuously via a looping systemd service — no long-lived session required, and no hourly throttle: a new cycle fires immediately after the previous one finishes.

## How it works

```
pipeline/queue.md        ← topic rotation queue
        │
        ▼
trend-scout agent        ← runs the /last30days skill on the next topic,
        │                  writes a dated research digest to research/
        ▼
gap-analyst agent        ← scores each candidate pattern for implementation
        │                  maturity: SATURATED / PARTIAL / OPEN
        ▼
idea-synthesizer agent   ← turns OPEN and PARTIAL patterns into project
        │                  idea files in ideas/, each tagged Format:
        │                  PROJECT / SKILL / BOTH
        ▼
  (promotion check)      ← orchestrator bumps PROPOSED → EXPLORING on
        │                  recurrence or strong evidence density
        ▼
skill-synthesizer agent  ← for SKILL/BOTH ideas without one yet, writes a
        │                  dual-format skill to skills/ (at most 1/cycle)
        ▼
publisher agent          ← for the oldest EXPLORING idea without one yet,
        │                  writes a polished writeup to published/,
        │                  commits, pushes, flips status to PUBLISHED
        ▼
pipeline/state.json      ← cycle counter, topic cursor, dedupe ledger
```

The diagram above is the INFRA track. The MARKETPLACE track mirrors it exactly (marketplace-trend-scout → marketplace-gap-analyst → marketplace-idea-synthesizer → marketplace-skill-synthesizer → marketplace-packager) against its own files inside the private `marketplace-content/` repo, with an extra packaging step and no publish step at all — marketplace ideas are never made public.

Driven by `scripts/heartbeat.sh`, looped continuously by `scripts/loop.sh` (as the `ai-idea-scout-loop` systemd service) instead of an hourly cron trigger — each firing spawns **both tracks as parallel subagents**, waits for both to finish their own full cycle end-to-end (including both git pushes, public and private), and the loop immediately fires the next one. See `CLAUDE.md`'s "Orchestration" section for the dispatch, and the two Track Protocol sections for each track's own cycle.

## Directory structure

```
CLAUDE.md           Orchestration protocol (read every cycle)
docs/
  TOPICS.md         Topic rotation list and rationale
  METHODOLOGY.md    Research quality bar, maturity rubric, skill-shaped heuristic,
                     promotion/publishing criteria
pipeline/           INFRA-track only — the MARKETPLACE track has its own equivalent
                     files inside marketplace-content/, never these.
  state.json        Cycle counter, topic cursor, last run
  queue.md          Topic queue (rotation + ad-hoc additions)
  changelog.md      One line per completed cycle
  published.md      Log of everything promoted to published/
  sessions/         Per-cycle orchestrator notes
research/
  YYYY-MM-DD-<topic>.md   Raw research digests from trend-scout (INFRA only)
ideas/
  INDEX.md          Index of all generated ideas, status, and Format tag (INFRA only)
  <idea-slug>.md    One file per project idea (see .claude/rules/idea-format.md)
skills/
  <skill-slug>/     Dual-format Claude Code skill for ideas tagged SKILL/BOTH
    SKILL.md
    README.md
    tests/
published/
  <idea-slug>.md    Polished public writeup for promoted ideas (see pipeline/published.md)
marketplace-content/   PRIVATE — separate nested git repo, own remote, gitignored here.
                        Full self-contained MARKETPLACE-track pipeline: its own
                        state.json/queue.md/changelog.md/sessions/, plus
                        research/ideas/skills/INDEX.md mirroring the above, plus
                        candidates/<slug>/ (packaged listing drafts) and review-queue.md
                        (human approval ledger). See marketplace-content/README.md.
scripts/
  heartbeat.sh      One firing — dispatches both tracks as parallel subagents, exits
  loop.sh           Continuous driver — fires heartbeat.sh back-to-back forever
                     (run as the ai-idea-scout-loop systemd service)
.claude/
  agents/           trend-scout, gap-analyst, idea-synthesizer, skill-synthesizer,
                     publisher, and their marketplace-track siblings
                     (marketplace-trend-scout, marketplace-gap-analyst,
                     marketplace-idea-synthesizer, marketplace-skill-synthesizer,
                     marketplace-packager)
  rules/            idea-format.md, skill-format.md, research-quality.md
```

## Requirements

- The [last30days skill](https://github.com/mvanhorn/last30days-skill) installed as a Claude Code plugin (already installed at `~/.claude/plugins/cache/last30days-skill/`).
- Optional API keys (`SCRAPECREATORS_API_KEY`, etc.) improve source coverage; the skill degrades gracefully to web search without them.
- `gh` CLI authenticated as the repo owner (needed by the `publisher` subagent to push).

## Running it

Continuity is a systemd user service running `scripts/loop.sh`, not a cron job and not a session you keep open:

```bash
systemctl --user status ai-idea-scout-loop    # check it's running
systemctl --user restart ai-idea-scout-loop   # after editing CLAUDE.md/agents
journalctl --user -u ai-idea-scout-loop -f    # tail live output
```

`loop.sh` fires `heartbeat.sh` and, as soon as it exits, fires it again — no hourly wait. Each firing is self-contained: it holds a lock file for the duration (so a long cycle can't overlap a second one), runs both tracks' full cycles in parallel, and exits; `loop.sh` then pauses briefly and fires the next one. Logs land in `logs/heartbeat-<date>.log` (rotated after 30 days) and `logs/cron.log` (kept as the log filename for continuity, though nothing here is triggered by cron anymore).

## Dashboard

A local, mobile-friendly web app (`dashboard/`) to watch both tracks, change idea statuses, leave feedback the pipeline reads at the start of its next cycle, and approve/reject Agensi.io listing candidates — from an iPhone over the home LAN, no auth. Runs as a systemd user service; see `dashboard/README.md` for the URL and operational commands.
