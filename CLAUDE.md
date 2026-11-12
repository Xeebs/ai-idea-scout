# AI Idea Scout — Claude Code Instructions

AI Idea Scout is an autonomous research pipeline. Each cycle researches one topic for the freshest 30 days of community signal, identifies patterns that are **not yet fully implemented or tested** anywhere, and compiles them into real-world project ideas with a tangible-impact thesis. Ideas that are also expressible as a repeatable prompt-driven task get a real, dual-format Claude Code skill. Ideas that prove popular or impactful get a polished public writeup in `published/`.

Cycles alternate between two tracks (`pipeline/state.json`'s `active_track`):

- **INFRA** — AI-builder/agent-infra topics, the original scope. Output: `research/`, `ideas/`, `skills/`, `published/` — all in **this public repo**.
- **MARKETPLACE** — broad indie-builder topics (see `docs/TOPICS.md` → "Marketplace Rotation"), scored for `Marketplace Fit`, and packaged (when HIGH) as an Agensi.io listing draft awaiting human review. **All MARKETPLACE-track content — research, ideas, skills, packaged candidates, its own changelog and session notes — lives in `marketplace-content/`, a separate, private, nested git repo with its own remote. Nothing produced on a MARKETPLACE cycle is ever committed or pushed to this public repo.** See `docs/METHODOLOGY.md`'s "Marketplace track" section and `marketplace-content/README.md`.

This repo has no application code — the product is `ideas/`, `skills/`, `published/` (public) plus `marketplace-content/` (private, pushed separately).

Public repo: `Xeebs/ai-idea-scout`. Private marketplace repo: `Xeebs/ai-idea-scout-marketplace`.

## Continuity

This pipeline runs via an **hourly cron heartbeat** (`scripts/heartbeat.sh`), not a long-lived self-paced `/loop` session. Each invocation fires `claude --dangerously-skip-permissions` for exactly **one cycle, end to end, then exits**. `heartbeat.sh` holds a lock file for the duration so an overrunning cycle never overlaps the next hour's trigger. You do not need to self-pace or schedule your own wake-up — just finish one full cycle (through Phase 6, including both git pushes) and stop. If you hit something that can't complete this invocation (rate limit, a stuck subagent), write the current phase to `pipeline/state.json` and exit; the next hourly firing resumes from there.

## Cycle Protocol

### Phase 0 — Resume check

Read `pipeline/state.json`. If `current_phase` is not `IDLE`, a previous cycle died mid-flight — resume from that phase with the recorded `active_topic` and `active_track` (a cycle never flips `active_track` until it completes Phase 6, so a resumed cycle always continues on the track it started on).

Otherwise start a fresh cycle on the track named by `active_track` (`INFRA` or `MARKETPLACE`). Pick the next topic from that track's queue — `pipeline/queue.md` for INFRA, `pipeline/queue-marketplace.md` for MARKETPLACE: take the first `UNWORKED` entry (ad-hoc entries outrank rotation entries). If none, regenerate the rotation from the matching section of `docs/TOPICS.md` ("Rotation" for INFRA, "Marketplace Rotation" for MARKETPLACE) by appending every rotation topic as `UNWORKED` and take the first.

Mark the chosen topic `IN_PROGRESS` in that track's queue file and write `state.json` with `current_phase: RESEARCH, active_topic: <topic>` (leave `active_track` as-is).

### Phase 1 — Research (delegate: trend-scout or marketplace-trend-scout)

Spawn a **general-purpose** subagent. If `active_track` is `INFRA`:

> You are the trend-scout agent. Read `/home/xhasan/my-projects/ai-idea-scout/.claude/agents/trend-scout.md` and follow it exactly for the topic: "<topic>". Today's date is <YYYY-MM-DD>.

If `active_track` is `MARKETPLACE`, use the same shape but with `marketplace-trend-scout.md` instead.

The scout invokes the `/last30days` skill, then distills the output into a digest with 5–10 **candidate patterns** (see `.claude/rules/research-quality.md`) — at `research/<YYYY-MM-DD>-<topic-slug>.md` for INFRA, `marketplace-content/research/<YYYY-MM-DD>-<topic-slug>.md` for MARKETPLACE (the agent file encodes the correct path; verify against the right one for the active track). On return, verify the digest file exists and has at least 3 candidate patterns; if not, re-spawn once with the failure noted, then mark the topic `FAILED` in the queue and end the cycle.

Write `state.json` with `current_phase: GAP_ANALYSIS`.

### Phase 2 — Gap analysis (delegate: gap-analyst or marketplace-gap-analyst)

Spawn a **general-purpose** subagent — `gap-analyst.md` for `active_track: INFRA`, `marketplace-gap-analyst.md` for `active_track: MARKETPLACE`:

> You are the gap-analyst agent. Read `/home/xhasan/my-projects/ai-idea-scout/.claude/agents/<gap-analyst.md or marketplace-gap-analyst.md>` and follow it exactly. The digest to analyze is `<research/... or marketplace-content/research/...>/<file>`.

The analyst scores every candidate pattern `SATURATED`, `PARTIAL`, or `OPEN` (rubric in `docs/METHODOLOGY.md` — INFRA and Marketplace rubrics differ, each agent file points at its own) and writes the verdicts back into the digest file under each pattern. Only `OPEN` and `PARTIAL` patterns advance.

Write `state.json` with `current_phase: SYNTHESIS`.

### Phase 3 — Idea synthesis (delegate: idea-synthesizer or marketplace-idea-synthesizer)

If no patterns survived Phase 2, skip to Phase 6 (a cycle that produces zero ideas is a valid outcome — never pad). Otherwise spawn a **general-purpose** subagent — `idea-synthesizer.md` for `active_track: INFRA`, `marketplace-idea-synthesizer.md` for `active_track: MARKETPLACE`:

> You are the idea-synthesizer agent. Read `/home/xhasan/my-projects/ai-idea-scout/.claude/agents/<idea-synthesizer.md or marketplace-idea-synthesizer.md>` and follow it exactly. Source digest: `<file>`. Before writing anything, read `<ideas/INDEX.md or marketplace-content/INDEX.md>` and skip any pattern already covered by an existing idea.

The synthesizer writes one file per idea — to `ideas/` (INFRA) or `marketplace-content/ideas/` (MARKETPLACE) — following `.claude/rules/idea-format.md`: every idea MUST include a **Tangible Impact** section and a **Format** tag (PROJECT/SKILL/BOTH per the heuristic in `docs/METHODOLOGY.md`); MARKETPLACE ideas additionally carry a `Marketplace Fit: LOW|MEDIUM|HIGH` header field. Appends each to the matching INDEX file.

**Promotion check (orchestrator, no subagent)**: for each new idea, and for each pattern the synthesizer reported as a skipped duplicate, check whether the gap now meets the promotion bar in `docs/METHODOLOGY.md` (recurrence across cycles, or evidence density ≥100 combined points or ≥3 independent threads). If so, edit that idea's status directly from `PROPOSED` to `EXPLORING` in whichever INDEX file it lives in, with a one-line reason noted later. Never touch a status a human has already changed manually.

Write `state.json` with `current_phase: SKILL_SYNTHESIS`.

### Phase 4 — Skill synthesis (delegate: skill-synthesizer, conditional, INFRA only)

Scan `ideas/INDEX.md` for any idea (from this cycle or the backlog) tagged `Format: SKILL` or `Format: BOTH` that has no `skills/<slug>/` directory yet. If at least one exists, spawn:

> You are the skill-synthesizer agent. Read `/home/xhasan/my-projects/ai-idea-scout/.claude/agents/skill-synthesizer.md` and follow it exactly. Target idea: `ideas/<file>`.

Pick the **oldest** qualifying idea — at most one skill per cycle, to protect usage limits. If the synthesizer returns `NOVELTY_FAIL`, edit that idea's `Format` field to `PROJECT` and append a one-line note citing what was found. If `NO_CANDIDATES`, skip silently. Runs every cycle regardless of `active_track` (backlog catch-up), same as Phase 4b and 4.5 below. `ideas/INDEX.md` never contains MARKETPLACE ideas, so this phase never touches `marketplace-content/`.

Write `state.json` with `current_phase: MARKETPLACE_SKILL_SYNTHESIS`.

### Phase 4b — Marketplace skill synthesis (delegate: marketplace-skill-synthesizer, conditional)

Scan `marketplace-content/INDEX.md` for any idea tagged `Format: SKILL` or `Format: BOTH` that has no `marketplace-content/skills/<slug>/` directory yet. If at least one exists, spawn:

> You are the marketplace-skill-synthesizer agent. Read `/home/xhasan/my-projects/ai-idea-scout/.claude/agents/marketplace-skill-synthesizer.md` and follow it exactly. Target idea: `marketplace-content/ideas/<file>`.

Pick the **oldest** qualifying idea — at most one per cycle. If `NOVELTY_FAIL`, edit that idea's `Format` field to `PROJECT` with a one-line note. If `NO_CANDIDATES`, skip silently. Runs every cycle regardless of `active_track` (backlog catch-up). **Everything this phase touches lives under `marketplace-content/` — never stage or reference these files from the public repo.**

Write `state.json` with `current_phase: MARKETPLACE_PACKAGING`.

### Phase 4.5 — Marketplace packaging (delegate: marketplace-packager, conditional)

Scan `marketplace-content/INDEX.md` for any idea with `Marketplace Fit: HIGH`, `Format: SKILL` or `BOTH`, an existing `marketplace-content/skills/<slug>/` directory, and no `marketplace-content/candidates/<slug>/` yet. If at least one exists, spawn:

> You are the marketplace-packager agent. Read `/home/xhasan/my-projects/ai-idea-scout/.claude/agents/marketplace-packager.md` and follow it exactly. Target idea: `marketplace-content/ideas/<file>`.

Pick the **oldest** qualifying idea — at most one packaging per cycle, same usage-limit reasoning as skill synthesis. If it returns `ALREADY_PACKAGED` or `NOT_READY`, note the reason and move on. Runs every cycle regardless of `active_track` (backlog catch-up).

This phase never commits, uploads, or touches Agensi.io — it only stages files under `marketplace-content/` for a human to review (see `marketplace-content/README.md`). Phase 6b commits and pushes it, same as every other marketplace-content output.

Write `state.json` with `current_phase: PUBLISH`.

### Phase 5 — Publish (delegate: publisher, conditional, INFRA only by construction)

If any idea in `ideas/INDEX.md` has `status: EXPLORING` and no `published/<slug>.md` yet, spawn:

> You are the publisher agent. Read `/home/xhasan/my-projects/ai-idea-scout/.claude/agents/publisher.md` and follow it exactly.

At most one publish per cycle (oldest EXPLORING idea first). The publisher does its own git commit and push for the `published/` file, `pipeline/published.md`, and the INDEX status flip — that part of the repo state is already synced by the time this phase returns. If it returns `AUTH_FAIL`, note it in the session file (Phase 6) so a human notices gh auth needs attention; do not attempt to fix auth yourself mid-cycle. **Never point the publisher at `marketplace-content/INDEX.md` or a marketplace idea — publishing writes public content, and marketplace ideas must never be published publicly.** This is already enforced by construction since `publisher.md` only ever reads `ideas/INDEX.md`; do not change that.

Write `state.json` with `current_phase: CLOSE_OUT`.

### Phase 6 — Close out

#### Phase 6a — Public repo

1. Mark the topic `DONE` (or `FAILED`) in that cycle's track queue file (`pipeline/queue.md` for INFRA, `pipeline/queue-marketplace.md` for MARKETPLACE — both files live in the public repo regardless of track; they only ever contain generic topic-category names, never idea content).
2. Append one line to `pipeline/changelog.md`:
   - INFRA cycle: `- <date> · cycle <n> · INFRA · <topic> · <x> patterns found, <y> open/partial, <z> ideas, <skill written? slug>, <published? slug>`.
   - MARKETPLACE cycle: `- <date> · cycle <n> · MARKETPLACE · <topic> — see marketplace-content/changelog.md`. **Never put idea titles, slugs, pattern content, or pricing in the public changelog for a MARKETPLACE cycle** — counts and topic-category names only belong here; full detail goes in the private changelog (Phase 6b).
3. For an INFRA cycle only, write a short orchestrator note to `pipeline/sessions/<date>-cycle-<n>.md` (what worked, what to adjust next cycle, any `AUTH_FAIL`/`NOVELTY_FAIL` worth a human's attention). For a MARKETPLACE cycle, write the equivalent note to `marketplace-content/sessions/<date>-cycle-<n>.md` instead (Phase 6b pushes it) — never to the public `pipeline/sessions/`.
4. Write `state.json`: increment `cycle`, set `current_phase: IDLE`, `active_topic: null`, `last_run: <ISO timestamp>`, and **flip `active_track`** (`INFRA` → `MARKETPLACE` or `MARKETPLACE` → `INFRA`) — this is the only step that ever changes `active_track`, so a cycle that dies mid-flight and resumes always resumes on the track it started on.
5. **Before staging, sanity-check**: `git status --short` in the repo root must show nothing under `marketplace-content/` (it's gitignored — if it shows up, stop and investigate before committing anything).
6. **Commit and push whatever Phases 1–5 touched in the public tree that the publisher (Phase 5) didn't already commit** — typically `research/`, any new/edited `ideas/*.md` and `ideas/INDEX.md`, any new `skills/<slug>/`, the active track's queue file, `pipeline/changelog.md`, `pipeline/sessions/<file>` (INFRA cycles only), `pipeline/state.json`. Stage explicitly by path, never `git add -A`, and never add `marketplace-content/`:
   ```bash
   cd /home/xhasan/my-projects/ai-idea-scout
   git add research/ ideas/ skills/ pipeline/queue.md pipeline/queue-marketplace.md pipeline/changelog.md pipeline/sessions/ pipeline/state.json
   git commit -m "chore(pipeline): cycle <n> — <topic>"
   git push origin main
   ```
   If there is nothing to commit (clean tree), skip the commit, not an error.

#### Phase 6b — Private marketplace-content repo

Only meaningful on a MARKETPLACE cycle (or whenever Phase 4b/4.5 touched `marketplace-content/` on a backlog catch-up during an INFRA cycle). Check `git -C marketplace-content status --short` first; if clean, skip entirely.

```bash
cd /home/xhasan/my-projects/ai-idea-scout/marketplace-content
git add -A
git commit -m "chore(marketplace): cycle <n> — <topic>"
git push origin main
cd /home/xhasan/my-projects/ai-idea-scout
```

`git add -A` is fine here — this entire nested repo is private, so there is nothing to protect from itself. This repo's own history, remote, and push are completely independent of the public repo's; a failure here (e.g. network) should be noted in the session file but never block or roll back Phase 6a's already-completed public commit.

## Rules

- Never invent engagement numbers or sources — everything in a digest must trace to the last30days output or a verified search result.
- Never mark a pattern `OPEN` without the gap-analyst actually checking for existing implementations (GitHub, product launches, papers with code / existing paid listings, per track).
- Ideas are append-only: never delete or overwrite an existing idea file; supersede it with a new file and note the link in the matching INDEX.
- Same rule for `skills/`, `published/`, and their `marketplace-content/` equivalents: never delete or silently overwrite. A skill that needs a rewrite after `NOVELTY_FAIL` or a failed self-check is fine to edit in place before it's ever committed; once committed and pushed, supersede instead.
- **The public/private boundary is load-bearing, not cosmetic.** Nothing produced by a MARKETPLACE-track agent (`marketplace-trend-scout`, `marketplace-gap-analyst`, `marketplace-idea-synthesizer`, `marketplace-skill-synthesizer`, `marketplace-packager`) may ever be written outside `marketplace-content/`, referenced from a file in the public tree, or staged/committed/pushed via the public repo's remote. If you ever find marketplace content outside `marketplace-content/`, stop and flag it in the session file rather than trying to silently clean it up mid-cycle.
- `marketplace-content/review-queue.md` is human-owned once a row exists: the pipeline only ever appends new `PENDING_REVIEW` rows, never edits an existing row's status. The pipeline never has, requests, or uses Agensi.io credentials, and never uploads or lists anything itself.
- Keep subagent outputs on disk, not in conversation — the orchestrator only needs file paths and counts back from each agent.
- Token efficiency: pipe long command output through `tail`, read only relevant file ranges, and keep session notes under 20 lines.
