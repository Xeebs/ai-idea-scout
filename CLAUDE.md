# AI Idea Scout — Claude Code Instructions

AI Idea Scout is an autonomous research pipeline. Each cycle researches one AI topic for the freshest 30 days of community signal, identifies patterns that are **not yet fully implemented or tested** anywhere, and compiles them into real-world project ideas with a tangible-impact thesis. Ideas that are also expressible as a repeatable prompt-driven task get a real, dual-format Claude Code skill in `skills/`. Ideas that prove popular or impactful get a polished public writeup in `published/`. The product is the contents of `ideas/`, `skills/`, and `published/` — this repo has no application code.

Published to GitHub: `Xeebs/ai-idea-scout`.

## Continuity

This pipeline runs via an **hourly cron heartbeat** (`scripts/heartbeat.sh`), not a long-lived self-paced `/loop` session. Each invocation fires `claude --dangerously-skip-permissions` for exactly **one cycle, end to end, then exits**. `heartbeat.sh` holds a lock file for the duration so an overrunning cycle never overlaps the next hour's trigger. You do not need to self-pace or schedule your own wake-up — just finish one full cycle (through Phase 6, including the git push) and stop. If you hit something that can't complete this invocation (rate limit, a stuck subagent), write the current phase to `pipeline/state.json` and exit; the next hourly firing resumes from there.

## Cycle Protocol

### Phase 0 — Resume check

Read `pipeline/state.json`. If `current_phase` is not `IDLE`, a previous cycle died mid-flight — resume from that phase with the recorded `active_topic`. Otherwise pick the next topic: take the first `UNWORKED` entry in `pipeline/queue.md` (ad-hoc entries outrank rotation entries). If none, regenerate the rotation from `docs/TOPICS.md` by appending every rotation topic as `UNWORKED` and take the first.

Mark the chosen topic `IN_PROGRESS` in `pipeline/queue.md` and write `state.json` with `current_phase: RESEARCH, active_topic: <topic>`.

### Phase 1 — Research (delegate: trend-scout)

Spawn a **general-purpose** subagent with this prompt shape:

> You are the trend-scout agent. Read `/home/xhasan/my-projects/ai-idea-scout/.claude/agents/trend-scout.md` and follow it exactly for the topic: "<topic>". Today's date is <YYYY-MM-DD>.

The scout invokes the `/last30days` skill, then distills the output into `research/<YYYY-MM-DD>-<topic-slug>.md` with 5–10 **candidate patterns** (see `.claude/rules/research-quality.md`). On return, verify the digest file exists and has at least 3 candidate patterns; if not, re-spawn once with the failure noted, then mark the topic `FAILED` in the queue and end the cycle.

Write `state.json` with `current_phase: GAP_ANALYSIS`.

### Phase 2 — Gap analysis (delegate: gap-analyst)

Spawn a **general-purpose** subagent:

> You are the gap-analyst agent. Read `/home/xhasan/my-projects/ai-idea-scout/.claude/agents/gap-analyst.md` and follow it exactly. The digest to analyze is `research/<file>`.

The analyst scores every candidate pattern `SATURATED`, `PARTIAL`, or `OPEN` (rubric in `docs/METHODOLOGY.md`) and writes the verdicts back into the digest file under each pattern. Only `OPEN` and `PARTIAL` patterns advance.

Write `state.json` with `current_phase: SYNTHESIS`.

### Phase 3 — Idea synthesis (delegate: idea-synthesizer)

If no patterns survived Phase 2, skip to Phase 6 (a cycle that produces zero ideas is a valid outcome — never pad). Otherwise spawn a **general-purpose** subagent:

> You are the idea-synthesizer agent. Read `/home/xhasan/my-projects/ai-idea-scout/.claude/agents/idea-synthesizer.md` and follow it exactly. Source digest: `research/<file>`. Before writing anything, read `ideas/INDEX.md` and skip any pattern already covered by an existing idea.

The synthesizer writes one file per idea to `ideas/` following `.claude/rules/idea-format.md` — every idea MUST include a **Tangible Impact** section naming a specific population and the measurable change for them, and a **Format** tag (PROJECT/SKILL/BOTH per the heuristic in `docs/METHODOLOGY.md`) — and appends each to `ideas/INDEX.md`.

**Promotion check (orchestrator, no subagent)**: for each new idea, and for each pattern the synthesizer reported as a skipped duplicate, check whether the gap now meets the promotion bar in `docs/METHODOLOGY.md` (recurrence across cycles, or evidence density ≥100 combined points or ≥3 independent threads). If so, edit that idea's status in `ideas/INDEX.md` directly from `PROPOSED` to `EXPLORING`, with a one-line reason in the edit's commit later. Never touch a status a human has already changed manually.

Write `state.json` with `current_phase: SKILL_SYNTHESIS`.

### Phase 4 — Skill synthesis (delegate: skill-synthesizer, conditional)

Scan `ideas/INDEX.md` for any idea (from this cycle or the backlog) tagged `Format: SKILL` or `Format: BOTH` that has no `skills/<slug>/` directory yet. If at least one exists, spawn:

> You are the skill-synthesizer agent. Read `/home/xhasan/my-projects/ai-idea-scout/.claude/agents/skill-synthesizer.md` and follow it exactly. Target idea: `ideas/<file>`.

Pick the **oldest** qualifying idea — at most one skill per cycle, to protect usage limits. If the synthesizer returns `NOVELTY_FAIL`, edit that idea's `Format` field to `PROJECT` and append a one-line note citing what was found. If `NO_CANDIDATES`, skip silently.

Write `state.json` with `current_phase: PUBLISH`.

### Phase 5 — Publish (delegate: publisher, conditional)

If any idea in `ideas/INDEX.md` has `status: EXPLORING` and no `published/<slug>.md` yet, spawn:

> You are the publisher agent. Read `/home/xhasan/my-projects/ai-idea-scout/.claude/agents/publisher.md` and follow it exactly.

At most one publish per cycle (oldest EXPLORING idea first). The publisher does its own git commit and push for the `published/` file, `pipeline/published.md`, and the INDEX status flip — that part of the repo state is already synced by the time this phase returns. If it returns `AUTH_FAIL`, note it in the session file (Phase 6) so a human notices gh auth needs attention; do not attempt to fix auth yourself mid-cycle.

Write `state.json` with `current_phase: CLOSE_OUT`.

### Phase 6 — Close out

1. Mark the topic `DONE` (or `FAILED`) in `pipeline/queue.md`.
2. Append one line to `pipeline/changelog.md`: `- <date> · cycle <n> · <topic> · <x> patterns found, <y> open/partial, <z> ideas, <skill written? slug> , <published? slug>`.
3. Write a short orchestrator note to `pipeline/sessions/<date>-cycle-<n>.md` (what worked, what to adjust next cycle, any `AUTH_FAIL`/`NOVELTY_FAIL` worth a human's attention).
4. Write `state.json`: increment `cycle`, set `current_phase: IDLE`, `active_topic: null`, `last_run: <ISO timestamp>`.
5. **Commit and push whatever Phases 1–4 touched that the publisher (Phase 5) didn't already commit** — typically `research/`, any new/edited `ideas/*.md` and `ideas/INDEX.md`, any new `skills/<slug>/`, `pipeline/queue.md`, `pipeline/changelog.md`, `pipeline/sessions/<file>`, `pipeline/state.json`. Stage explicitly by path, never `git add -A`:
   ```bash
   cd /home/xhasan/my-projects/ai-idea-scout
   git add research/ ideas/ skills/ pipeline/queue.md pipeline/changelog.md pipeline/sessions/ pipeline/state.json
   git commit -m "chore(pipeline): cycle <n> — <topic>"
   git push origin main
   ```
   If there is nothing to commit (clean tree — e.g. a zero-idea cycle after the publisher already pushed its own change), skip the commit, not an error.

## Rules

- Never invent engagement numbers or sources — everything in a digest must trace to the last30days output or a verified search result.
- Never mark a pattern `OPEN` without the gap-analyst actually checking for existing implementations (GitHub, product launches, papers with code).
- Ideas are append-only: never delete or overwrite an existing idea file; supersede it with a new file and note the link in `INDEX.md`.
- Same rule for `skills/` and `published/`: never delete or silently overwrite. A skill that needs a rewrite after `NOVELTY_FAIL` or a failed self-check is fine to edit in place before it's ever committed; once committed and pushed, supersede instead.
- Keep subagent outputs on disk, not in conversation — the orchestrator only needs file paths and counts back from each agent.
- Token efficiency: pipe long command output through `tail`, read only relevant file ranges, and keep session notes under 20 lines.
