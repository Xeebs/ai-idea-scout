# Methodology

## Thesis

The best new-project signal is not what's launching — it's what practitioners are *complaining about, wishing for, and duct-taping together* right now. The last30days skill surfaces that signal across Reddit, X, Hacker News, YouTube, GitHub, and the web, ranked by real engagement. This pipeline filters that signal through two gates before anything becomes an idea:

1. **Novelty gate (gap-analyst)** — is it actually unbuilt or only partially built? Verified by searching GitHub, products, and papers, never assumed.
2. **Impact gate (idea-synthesizer)** — can we name a specific population whose outcomes measurably change? If not, it's a technique, not a project.

## Maturity rubric

| Verdict | Meaning | Advances? |
|---------|---------|-----------|
| SATURATED | ≥2 maintained implementations or a shipped product covering the gap | No |
| PARTIAL | Only demos, stale repos (>6 months), narrow scope, or no evaluation | Yes |
| OPEN | Multi-channel search found only discussion and one-off hacks | Yes |

PARTIAL is often the sweet spot: the community has validated demand, early attempts de-risk feasibility, and no one has executed well yet.

## Impact criteria

Every idea names a **population** (specific enough to find in a room, with a size estimate), a **mechanism** (the causal chain from project to changed outcome), and **measures** (2–3 metrics that would prove it). Ideas that serve "developers" serve developers *of something, somewhere, with a named pain*.

## Skill-shaped heuristic

Every surviving pattern gets a **Format** tag — PROJECT, SKILL, or BOTH — decided by one question: *is the core value a repeatable expert judgment, drafting, review, or analysis task a prompt can carry out, or does it require persistent runtime infrastructure (storage, middleware, a server, state that must survive between invocations)?*

| Signal | Tag |
|---|---|
| Needs a database, a running service, a protocol implementation, anything that must stay up between invocations | PROJECT |
| The whole job is "given this input, produce this judgment/draft/review" — no infrastructure, just expertise applied once per invocation | SKILL |
| The gap is infrastructure-shaped, but a design/review/adoption task around it is independently valuable (e.g. the project is a runtime policy engine; a skill that reviews a proposed policy or drafts one is genuinely separable) | BOTH |

When in doubt between PROJECT and BOTH, prefer BOTH — a skill companion is cheap to write and tests the idea's value before anyone commits to the infrastructure build.

## Promotion & Publishing

`ideas/INDEX.md` statuses now mean:

| Status | Meaning |
|---|---|
| PROPOSED | Default for every new idea. |
| EXPLORING | Promoted — recurring signal or strong evidence density (below). Next publisher cycle will write it up. |
| PUBLISHED | Has a writeup in `published/<slug>.md` (and, if Format includes SKILL, a real `skills/<slug>/`). |
| PROTOTYPING | A human has started building it (set manually, not by the pipeline). |
| SHELVED | Superseded or judged not worth pursuing further (set manually or by gap-analyst re-review). |

**Promotion criteria (PROPOSED → EXPLORING)** — any one is sufficient, applied by the orchestrator at the end of Phase 3 (no subagent needed, it's a direct INDEX.md edit with a one-line justification):
1. **Recurrence** — the same gap surfaces in a second cycle (already-existing rule, now operationalized: the orchestrator checks the new digest's patterns against `ideas/INDEX.md` sources, same as the synthesizer's dedupe check, and bumps status instead of skipping if it finds a second independent occurrence).
2. **Evidence density** — the pattern's cited evidence totals ≥100 combined engagement points/upvotes across sources, OR is independently raised in ≥3 separate threads/posts within the digest.
3. **Owner override** — you can hand-edit `ideas/INDEX.md` status at any time; the pipeline never overwrites a manual status change.

**Publishing (EXPLORING → PUBLISHED)** — the `publisher` subagent, spawned at most once per cycle: picks the oldest EXPLORING idea without a `published/<slug>.md`, writes a polished public-facing writeup (expands "The Gap" and "The Project" with more color, links the source digest(s) and any companion skill), commits, pushes, logs to `pipeline/published.md`, and flips status to PUBLISHED.

## Cadence & convergence

- One topic per cycle, fired hourly by `scripts/heartbeat.sh` (cron), full rotation ≈ 10 cycles.
- Two consecutive zero-idea cycles → note it in `pipeline/sessions/` and review topic phrasing in `TOPICS.md` (the heartbeat keeps firing hourly regardless — there is no self-pacing to slow).
- The ledger in `ideas/INDEX.md` is append-only; superseded ideas are cross-linked, never deleted, so the reasoning trail stays auditable.
