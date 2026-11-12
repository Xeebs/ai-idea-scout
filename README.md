# AI Idea Scout

An autonomous research loop that scans the last 30 days of community discussion (Reddit, X, Hacker News, YouTube, GitHub, web) to find **emerging patterns and ideas that have not yet been fully implemented or tested**, then compiles them into concrete, real-world project ideas with a defined tangible impact on a population of people.

Ideas that are also expressible as a repeatable, prompt-driven task get a real, dual-format Claude Code skill. Ideas that prove recurring or high-impact get promoted to a polished, published writeup.

Two parallel tracks alternate every cycle:
- **INFRA** — AI-builder/agent-infra topics (agentic AI, multi-agent, RAG, MCP, evals, safety), aimed at technical adopters. Output lives in this repo (`research/`, `ideas/`, `skills/`, `published/`).
- **MARKETPLACE** — broad indie-builder/small-business topics (copywriting, freelancing, productivity, SEO, etc.), scored for **Marketplace Fit** and, when HIGH, packaged as an Agensi.io listing draft (zip + price/description suggestion) awaiting human review — the pipeline never lists anything itself. **All of this track's output is private**: it lives in `marketplace-content/`, a separate nested git repo pushed to its own private GitHub remote, never to this public repo. See `marketplace-content/README.md` (not visible here if you're reading this on GitHub — it's local-only).

Runs continuously via an hourly cron heartbeat — no long-lived session required.

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

The diagram above is the INFRA track. The MARKETPLACE track mirrors it exactly (marketplace-trend-scout → marketplace-gap-analyst → marketplace-idea-synthesizer → marketplace-skill-synthesizer → marketplace-packager), with one difference: every step writes into the private `marketplace-content/` repo instead of the paths shown above, and there's an extra packaging step before anything would be "published" — except marketplace ideas are never published publicly at all.

Driven by `scripts/heartbeat.sh` on an hourly cron job — each firing runs exactly one full cycle end-to-end (including both git pushes, public and private) and exits. See `CLAUDE.md` for the full cycle protocol.

## Directory structure

```
CLAUDE.md           Orchestration protocol (read every cycle)
docs/
  TOPICS.md         Topic rotation list and rationale
  METHODOLOGY.md    Research quality bar, maturity rubric, skill-shaped heuristic,
                     promotion/publishing criteria
pipeline/
  state.json        Cycle counter, active_track, topic cursor, last run
  queue.md          INFRA-track topic queue (rotation + ad-hoc additions)
  queue-marketplace.md   MARKETPLACE-track topic queue
  changelog.md      One line per completed cycle
  published.md      Log of everything promoted to published/
  sessions/         Per-cycle orchestrator notes
research/
  YYYY-MM-DD-<topic>.md   Raw research digests from trend-scout or marketplace-trend-scout
ideas/
  INDEX.md          Index of all generated ideas, status, Format tag, and Track
  <idea-slug>.md    One file per project idea (see .claude/rules/idea-format.md)
skills/
  <skill-slug>/     Dual-format Claude Code skill for ideas tagged SKILL/BOTH
    SKILL.md
    README.md
    tests/
published/
  <idea-slug>.md    Polished public writeup for promoted ideas (see pipeline/published.md)
marketplace-content/   PRIVATE — separate nested git repo, own remote, gitignored here.
                        Mirrors research/ideas/skills above for the MARKETPLACE track, plus
                        candidates/<slug>/ (packaged listing drafts) and review-queue.md
                        (human approval ledger). See marketplace-content/README.md.
scripts/
  heartbeat.sh      Cron entry point — one cycle per invocation
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

Continuity is a cron job, not a session you keep open:

```
0 * * * * /home/xhasan/my-projects/ai-idea-scout/scripts/heartbeat.sh >> /home/xhasan/my-projects/ai-idea-scout/logs/cron.log 2>&1
```

Each firing is self-contained: it holds a lock file for the duration (so a long cycle never overlaps the next hour's trigger), runs one full pipeline cycle, and exits. Logs land in `logs/heartbeat-<date>.log` (rotated after 30 days) and `logs/cron.log`.
