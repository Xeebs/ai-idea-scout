# AI Idea Scout — Claude Code Instructions

AI Idea Scout is an autonomous research pipeline. Each cycle researches one topic for the freshest 30 days of community signal, identifies patterns that are **not yet fully implemented or tested** anywhere, and compiles them into real-world project ideas with a tangible-impact thesis. Ideas that are also expressible as a repeatable prompt-driven task get a real, dual-format Claude Code skill. Ideas that prove popular or impactful get a polished public writeup in `published/`.

**Two fully independent tracks run continuously, back-to-back, in parallel, as separate subagents — not on an hourly schedule anymore:**

- **INFRA** — AI-builder/agent-infra topics, the original scope. Entirely self-contained within this public repo: `pipeline/`, `research/`, `ideas/`, `skills/`, `published/`.
- **MARKETPLACE** — topics common among general, adept Claude/ChatGPT/Copilot power users (see `docs/TOPICS.md` → "Marketplace Rotation"; not narrow professional verticals, not AI-infra builders), scored for `Marketplace Fit` and packaged (when HIGH or MEDIUM) as an Agensi.io listing draft awaiting human review. Entirely self-contained within `marketplace-content/` — a separate, private, nested git repo with its own remote, its own `pipeline/`-equivalent files (`state.json`, `queue.md`, `changelog.md`, `sessions/`), and its own commit/push. **Nothing produced by this track is ever committed or pushed to this public repo.**

The two tracks share no mutable files — INFRA never writes inside `marketplace-content/`, and MARKETPLACE never writes outside it (it only ever *reads* `docs/TOPICS.md` from the public repo, read-only, for topic rotation phrasing). This is what makes it safe to run them concurrently: there is nothing for them to race over or step on.

This repo has no application code except `dashboard/` — a small local Flask app (no auth, LAN-only) that lets a human browse both tracks, change idea statuses, leave feedback, and approve/reject Agensi listing candidates. See `dashboard/README.md`. The product is `ideas/`, `skills/`, `published/` (public) plus `marketplace-content/` (private, pushed separately).

Public repo: `Xeebs/ai-idea-scout`. Private marketplace repo: `Xeebs/ai-idea-scout-marketplace`.

## Continuity

This pipeline runs via a **continuous loop** (`scripts/loop.sh`, run as the `ai-idea-scout-loop` systemd user service), not cron and not a long-lived self-paced `/loop` session inside one context window. Each firing of `scripts/heartbeat.sh` invokes `claude --dangerously-skip-permissions` **once**, for a single top-level session whose entire job is the Orchestration step below — dispatch both tracks as parallel subagents, wait for both, exit — then `loop.sh` immediately fires the next one (a short fixed pause, not an hour). `heartbeat.sh` still holds a lock file for the duration; under the loop alone firings are already serial, but the lock still protects against a stray manual/cron invocation overlapping one in progress.

Each track manages its **own** resume/retry lifecycle independently via its own state file (`pipeline/state.json` for INFRA, `marketplace-content/state.json` for MARKETPLACE). If a track's subagent can't finish within one firing (rate limit, a stuck sub-subagent), it writes its current phase to its own state file and stops; the *other* track is unaffected and still completes and commits normally. The very next firing's subagent for the stalled track resumes from where it left off — with no hour-long wait, a stalled track picks back up within seconds of the previous firing ending. Neither track should ever wait on, block, or need to know about the other.

## Orchestration (top-level session, every firing)

1. **Dispatch both track subagents in parallel** — one message, two delegations, neither waiting on the other:
   - **general-purpose subagent, "infra-cycle"**: `You are the AI Idea Scout INFRA track orchestrator. Read /home/xhasan/my-projects/ai-idea-scout/CLAUDE.md's "INFRA Track Protocol" section and execute it exactly, Phase 0 through Phase 6, end to end, including the git commit and push. This is a single invocation — do not self-pace or schedule a wake-up. If genuinely blocked, write the current phase to pipeline/state.json and stop; report what phase you stopped at.`
   - **general-purpose subagent, "marketplace-cycle"**: `You are the AI Idea Scout MARKETPLACE track orchestrator. Read /home/xhasan/my-projects/ai-idea-scout/CLAUDE.md's "MARKETPLACE Track Protocol" section and execute it exactly, Phase 0 through Phase 6, end to end, including the git commit and push to the private marketplace-content repo. This is a single invocation — do not self-pace or schedule a wake-up. If genuinely blocked, write the current phase to marketplace-content/state.json and stop; report what phase you stopped at.`
2. **Wait for both to report back.** Each is a complete, self-contained pipeline run against its own files and its own git remote — there is nothing to reconcile between their results.
3. Note any `AUTH_FAIL` / stalled-phase report from either in the firing's own stdout (captured by `heartbeat.sh`'s log redirect already — no separate file write needed at this level).
4. Exit.

---

## INFRA Track Protocol

Everything below reads and writes only within the public repo tree (never `marketplace-content/`).

### Phase 0 — Resume check

**Feedback intake (every cycle, resumed or fresh)**: read `pipeline/feedback.md`. For any `[UNCONSUMED]` entry, treat its text as human steering for this cycle — fold it into the topic choice below (e.g. an ad-hoc topic it implies) and/or pass it into Phase 1/3's subagent prompts as "Additional human guidance this cycle: <text>". After Phase 6 completes, flip each entry you incorporated from `[UNCONSUMED]` to `[CONSUMED cycle <n>]` in place (never delete it). This is the dashboard's "steer the pipeline" box — if you skip this, it's just a diary nobody reads.

Read `pipeline/state.json`. If `current_phase` is not `IDLE`, a previous INFRA cycle died mid-flight — resume from that phase with the recorded `active_topic`.

Otherwise pick the next topic: take the first `UNWORKED` entry in `pipeline/queue.md` (ad-hoc entries outrank rotation entries). If none, regenerate the rotation from `docs/TOPICS.md`'s "Rotation" section by appending every rotation topic as `UNWORKED` and take the first.

Mark the chosen topic `IN_PROGRESS` in `pipeline/queue.md` and write `state.json` with `current_phase: RESEARCH, active_topic: <topic>`.

### Phase 1 — Research (delegate: trend-scout)

Spawn a **general-purpose** subagent:

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

**Promotion check (orchestrator, no subagent)**: for each new idea, and for each pattern the synthesizer reported as a skipped duplicate, check whether the gap now meets the promotion bar in `docs/METHODOLOGY.md` (recurrence across cycles, or evidence density ≥50 combined points or ≥2 independent threads). If so, edit that idea's status in `ideas/INDEX.md` directly from `PROPOSED` to `EXPLORING`, with a one-line reason noted later. Never touch a status a human has already changed manually.

Write `state.json` with `current_phase: SKILL_SYNTHESIS`.

### Phase 4 — Skill synthesis (delegate: skill-synthesizer, conditional)

Scan `ideas/INDEX.md` for any idea (from this cycle or the backlog) tagged `Format: SKILL` or `Format: BOTH` that has no `skills/<slug>/` directory yet. Take up to the **oldest 3** qualifying ideas (fewer if fewer exist) and spawn one skill-synthesizer subagent per idea, in parallel (they write to disjoint `skills/<slug>/` directories, so there's nothing to race over):

> You are the skill-synthesizer agent. Read `/home/xhasan/my-projects/ai-idea-scout/.claude/agents/skill-synthesizer.md` and follow it exactly. Target idea: `ideas/<file>`.

Raised from the old 1-per-cycle cap to 3 — the backlog of skill-shaped ideas was growing faster than it drained. For each that returns `NOVELTY_FAIL`, edit that idea's `Format` field to `PROJECT` and append a one-line note citing what was found. `NO_CANDIDATES` overall → skip silently.

Write `state.json` with `current_phase: PUBLISH`.

### Phase 5 — Publish (delegate: publisher, conditional)

If any idea in `ideas/INDEX.md` has `status: EXPLORING` and no `published/<slug>.md` yet, spawn:

> You are the publisher agent. Read `/home/xhasan/my-projects/ai-idea-scout/.claude/agents/publisher.md` and follow it exactly.

At most one publish per cycle (oldest EXPLORING idea first). The publisher does its own git commit and push for the `published/` file, `pipeline/published.md`, and the INDEX status flip — that part of the repo state is already synced by the time this phase returns. If it returns `AUTH_FAIL`, note it in the session file (Phase 6) so a human notices gh auth needs attention; do not attempt to fix auth yourself mid-cycle.

Write `state.json` with `current_phase: CLOSE_OUT`.

### Phase 6 — Close out

1. Mark the topic `DONE` (or `FAILED`) in `pipeline/queue.md`.
2. Append one line to `pipeline/changelog.md`: `- <date> · cycle <n> · <topic> · <x> patterns found, <y> open/partial, <z> ideas, <skill written? slug>, <published? slug>`.
3. Write a short orchestrator note to `pipeline/sessions/<date>-cycle-<n>.md` (what worked, what to adjust next cycle, any `AUTH_FAIL`/`NOVELTY_FAIL` worth a human's attention).
4. Write `state.json`: increment `cycle`, set `current_phase: IDLE`, `active_topic: null`, `last_run: <ISO timestamp>`.
5. **Commit and push whatever Phases 1–4 touched that the publisher (Phase 5) didn't already commit** — typically `research/`, any new/edited `ideas/*.md` and `ideas/INDEX.md`, any new `skills/<slug>/`, `pipeline/queue.md`, `pipeline/changelog.md`, `pipeline/sessions/<file>`, `pipeline/state.json`. Stage explicitly by path, never `git add -A`, and never touch `marketplace-content/` (it's gitignored — if `git status --short` shows it, stop and flag rather than staging it):
   ```bash
   cd /home/xhasan/my-projects/ai-idea-scout
   git add research/ ideas/ skills/ pipeline/queue.md pipeline/changelog.md pipeline/sessions/ pipeline/state.json
   git commit -m "chore(pipeline): cycle <n> — <topic>"
   git push origin main
   ```
   If there is nothing to commit (clean tree — e.g. a zero-idea cycle after the publisher already pushed its own change), skip the commit, not an error.

---

## MARKETPLACE Track Protocol

Everything below reads and writes only within `marketplace-content/` (the private nested repo), except one read-only reference to the public repo's `docs/TOPICS.md`. **Never write, stage, commit, or push anything outside `marketplace-content/` from this protocol.**

### Phase 0 — Resume check

**Feedback intake (every cycle, resumed or fresh)**: read `marketplace-content/feedback.md`. For any `[UNCONSUMED]` entry, treat its text as human steering for this cycle — fold it into the topic choice below and/or pass it into Phase 1/3's subagent prompts as "Additional human guidance this cycle: <text>". After Phase 6 completes, flip each entry you incorporated from `[UNCONSUMED]` to `[CONSUMED cycle <n>]` in place (never delete it).

Read `marketplace-content/state.json`. If `current_phase` is not `IDLE`, a previous MARKETPLACE cycle died mid-flight — resume from that phase with the recorded `active_topic`.

Otherwise pick the next topic: take the first `UNWORKED` entry in `marketplace-content/queue.md` (ad-hoc entries outrank rotation entries). If none, regenerate the rotation from `docs/TOPICS.md`'s "Marketplace Rotation" section (public repo, read-only) by appending every rotation topic as `UNWORKED` and take the first.

Mark the chosen topic `IN_PROGRESS` in `marketplace-content/queue.md` and write `marketplace-content/state.json` with `current_phase: RESEARCH, active_topic: <topic>`.

### Phase 1 — Research (delegate: marketplace-trend-scout)

Spawn a **general-purpose** subagent:

> You are the marketplace-trend-scout agent. Read `/home/xhasan/my-projects/ai-idea-scout/.claude/agents/marketplace-trend-scout.md` and follow it exactly for the topic: "<topic>". Today's date is <YYYY-MM-DD>.

Writes a digest to `marketplace-content/research/<YYYY-MM-DD>-<topic-slug>.md` with 5–10 candidate patterns. On return, verify the digest exists with at least 3 patterns; if not, re-spawn once with the failure noted, then mark the topic `FAILED` in `marketplace-content/queue.md` and end the cycle.

Write `marketplace-content/state.json` with `current_phase: GAP_ANALYSIS`.

### Phase 2 — Gap analysis (delegate: marketplace-gap-analyst)

Spawn a **general-purpose** subagent:

> You are the marketplace-gap-analyst agent. Read `/home/xhasan/my-projects/ai-idea-scout/.claude/agents/marketplace-gap-analyst.md` and follow it exactly. The digest to analyze is `marketplace-content/research/<file>`.

Scores every pattern `SATURATED`/`PARTIAL`/`OPEN` against paid listings and free skill marketplaces (rubric in `docs/METHODOLOGY.md`), edits the digest in place. Only `OPEN`/`PARTIAL` advance.

Write `marketplace-content/state.json` with `current_phase: SYNTHESIS`.

### Phase 3 — Idea synthesis (delegate: marketplace-idea-synthesizer)

If no patterns survived Phase 2, skip to Phase 6. Otherwise spawn a **general-purpose** subagent:

> You are the marketplace-idea-synthesizer agent. Read `/home/xhasan/my-projects/ai-idea-scout/.claude/agents/marketplace-idea-synthesizer.md` and follow it exactly. Source digest: `marketplace-content/research/<file>`. Before writing anything, read `marketplace-content/INDEX.md` and skip any pattern already covered.

Writes one idea file per surviving pattern to `marketplace-content/ideas/`, each with a `Marketplace Fit: LOW|MEDIUM|HIGH` field, and appends to `marketplace-content/INDEX.md`.

**Promotion check (orchestrator, no subagent)**: same bar as INFRA (recurrence, or evidence density), applied to `marketplace-content/INDEX.md` entries. Never touch a status a human has already changed manually.

Write `marketplace-content/state.json` with `current_phase: SKILL_SYNTHESIS`.

### Phase 4 — Skill synthesis (delegate: marketplace-skill-synthesizer, conditional)

Scan `marketplace-content/INDEX.md` for any idea tagged `Format: SKILL`/`BOTH` with no `marketplace-content/skills/<slug>/` yet. Take up to the **oldest 3** qualifying ideas and spawn one marketplace-skill-synthesizer subagent per idea, in parallel (disjoint output directories):

> You are the marketplace-skill-synthesizer agent. Read `/home/xhasan/my-projects/ai-idea-scout/.claude/agents/marketplace-skill-synthesizer.md` and follow it exactly. Target idea: `marketplace-content/ideas/<file>`.

Raised from the old 1-per-cycle cap to 3, same reasoning as INFRA's Phase 4. For each `NOVELTY_FAIL` → edit `Format` to `PROJECT` with a one-line note. `NO_CANDIDATES` overall → skip silently.

Write `marketplace-content/state.json` with `current_phase: PACKAGING`.

### Phase 5 — Packaging (delegate: marketplace-packager, conditional)

Scan `marketplace-content/INDEX.md` for any idea with `Marketplace Fit: HIGH` or `MEDIUM` (not `LOW`), `Format: SKILL`/`BOTH`, an existing `marketplace-content/skills/<slug>/`, and no `marketplace-content/candidates/<slug>/` yet. Loosened from HIGH-only: too few ideas were ever scoring HIGH for the review queue to get real throughput, and a human reviews every candidate before anything is ever listed anyway, so the cost of a MEDIUM-fit candidate turning out not to be worth listing is just a few minutes of the human's review time, not a bad listing going live. If at least one exists, spawn:

> You are the marketplace-packager agent. Read `/home/xhasan/my-projects/ai-idea-scout/.claude/agents/marketplace-packager.md` and follow it exactly. Target idea: `marketplace-content/ideas/<file>`.

Pick the oldest qualifying idea — at most one per cycle. `ALREADY_PACKAGED`/`NOT_READY` → note and move on.

This phase never commits, uploads, or touches Agensi.io — it only stages files for a human to review (see `marketplace-content/README.md`). **There is no publish phase on this track** — marketplace ideas are never made public; that's the entire point of this track living in a private repo.

Write `marketplace-content/state.json` with `current_phase: CLOSE_OUT`.

### Phase 6 — Close out

1. Mark the topic `DONE` (or `FAILED`) in `marketplace-content/queue.md`.
2. Append one line to `marketplace-content/changelog.md` (full detail is fine — this repo is private).
3. Write a session note to `marketplace-content/sessions/<date>-cycle-<n>.md`.
4. Write `marketplace-content/state.json`: increment `cycle`, `current_phase: IDLE`, `active_topic: null`, `last_run: <ISO timestamp>`.
5. Commit and push the whole repo to its own remote:
   ```bash
   cd /home/xhasan/my-projects/ai-idea-scout/marketplace-content
   git add -A
   git commit -m "chore(marketplace): cycle <n> — <topic>"
   git push origin main
   ```
   `git add -A` is fine here — this entire nested repo is private, so there's nothing to protect from itself. If there's nothing to commit, skip, not an error.

---

## Rules

- Never invent engagement numbers or sources — everything in a digest must trace to the last30days output or a verified search result.
- Never mark a pattern `OPEN` without the gap-analyst actually checking for existing implementations (GitHub, product launches, papers with code / existing paid listings and free skill marketplaces, per track).
- Ideas are append-only: never delete or overwrite an existing idea file; supersede it with a new file and note the link in the matching INDEX.
- Same rule for `skills/`, `published/`, and their `marketplace-content/` equivalents: never delete or silently overwrite.
- **The public/private boundary is load-bearing, not cosmetic.** Nothing produced by a MARKETPLACE-track agent may ever be written outside `marketplace-content/`, referenced from a file in the public tree, or staged/committed/pushed via the public repo's remote — and nothing INFRA produces belongs inside `marketplace-content/`. If you ever find content on the wrong side of that boundary, stop and flag it in the relevant session file rather than trying to silently clean it up mid-cycle.
- **The two tracks run as independent, parallel subagents and must stay that way.** Neither reads the other's state file, queue, or INDEX; neither waits on the other. Don't reintroduce shared mutable state between them.
- `marketplace-content/review-queue.md` is human-owned once a row exists: the pipeline only ever appends new `PENDING_REVIEW` rows, never edits an existing row's status. The pipeline never has, requests, or uses Agensi.io credentials, and never uploads or lists anything itself.
- **Human feedback always wins.** Before any subagent reworks an *existing* idea file (a dedupe check in idea synthesis, skill synthesis, packaging), the orchestrator checks that idea file for a `## Human Feedback` section (written via `dashboard/`) and passes its content into that subagent's spawn prompt as context. A human's note on an idea is a steer, not a suggestion to weigh against other signal.
- Idea statuses, review-queue decisions, and `## Human Feedback` sections are written by a human via `dashboard/`, mirroring how the orchestrator itself edits a status directly on promotion — never revert or "clean up" a human-made edit to any of these, even if it looks inconsistent with the pipeline's own judgment.
- **Every idea states its Data Sources (Manual vs. Connected) explicitly, carried through into the SKILL.md and any packaged LISTING.md** — see `docs/METHODOLOGY.md`. This came directly from real review-queue rejections where a skill made the user paste data it could have read from a connector instead; never let this field go missing or vague on a new idea.
- Keep subagent outputs on disk, not in conversation — the orchestrator only needs file paths and counts back from each agent.
- Token efficiency: pipe long command output through `tail`, read only relevant file ranges, and keep session notes under 20 lines.
