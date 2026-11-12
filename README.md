# AI Idea Scout

An autonomous research loop that scans the last 30 days of community discussion (Reddit, X, Hacker News, YouTube, GitHub, web) across AI topics — agentic AI, multi-agent architectures, RAG techniques, context engineering, and more — to find **emerging patterns and ideas that have not yet been fully implemented or tested**, then compiles them into concrete, real-world project ideas with a defined tangible impact on a population of people.

Ideas that are also expressible as a repeatable, prompt-driven task get a real, dual-format Claude Code skill. Ideas that prove recurring or high-impact get promoted to a polished, published writeup.

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

Driven by `scripts/heartbeat.sh` on an hourly cron job — each firing runs exactly one full cycle end-to-end (including the git push) and exits. See `CLAUDE.md` for the full cycle protocol.

## Directory structure

```
CLAUDE.md           Orchestration protocol (read every cycle)
docs/
  TOPICS.md         Topic rotation list and rationale
  METHODOLOGY.md    Research quality bar, maturity rubric, skill-shaped heuristic,
                     promotion/publishing criteria
pipeline/
  state.json        Cycle counter, topic cursor, last run
  queue.md          Topic queue (rotation + ad-hoc additions)
  changelog.md      One line per completed cycle
  published.md      Log of everything promoted to published/
  sessions/         Per-cycle orchestrator notes
research/
  YYYY-MM-DD-<topic>.md   Raw research digests from trend-scout
ideas/
  INDEX.md          Index of all generated ideas, status, and Format tag
  <idea-slug>.md    One file per project idea (see .claude/rules/idea-format.md)
skills/
  <skill-slug>/     Dual-format Claude Code skill for ideas tagged SKILL/BOTH
    SKILL.md
    README.md
    tests/
published/
  <idea-slug>.md    Polished public writeup for promoted ideas (see pipeline/published.md)
scripts/
  heartbeat.sh      Cron entry point — one cycle per invocation
.claude/
  agents/           trend-scout, gap-analyst, idea-synthesizer, skill-synthesizer,
                     publisher definitions
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
