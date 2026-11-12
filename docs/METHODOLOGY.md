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

- One topic per cycle, fired continuously back-to-back by `scripts/loop.sh` (no hourly throttle), full rotation ≈ 10 cycles.
- Two consecutive zero-idea cycles → note it in `pipeline/sessions/` and review topic phrasing in `TOPICS.md` (the loop keeps firing regardless — there is no self-pacing to slow).
- The ledger in `ideas/INDEX.md` is append-only; superseded ideas are cross-linked, never deleted, so the reasoning trail stays auditable.

## Marketplace track

A second track aimed at Agensi.io's actual audience (indie builders and small-business operators searching Google) rather than the INFRA track's AI-builder niche. It runs **every hour, in parallel with INFRA**, as a fully independent subagent with its own state file, queue, and git repo — see `CLAUDE.md`'s "Orchestration" section and "MARKETPLACE Track Protocol". It uses its own topic rotation (`docs/TOPICS.md` → "Marketplace Rotation") and queue (`marketplace-content/queue.md`), and its own agents — `marketplace-trend-scout`, `marketplace-gap-analyst`, `marketplace-idea-synthesizer`, `marketplace-skill-synthesizer`, `marketplace-packager` — sibling rewrites of the INFRA agents with the same file-contract shapes but a buyer-facing rubric.

**Everything this track produces lives in `marketplace-content/` — a separate, private, nested git repo with its own remote, never pushed to the public `ai-idea-scout` repo.** The orchestration logic described here (this doc, `CLAUDE.md`, the agent definitions themselves, `docs/TOPICS.md`) stays public — it's process, not sellable content. But the actual research digests, idea files, skills, and packaged listing candidates are the product being readied for sale, so they never touch the public repo. See `marketplace-content/README.md`.

### Marketplace maturity rubric (marketplace-gap-analyst)

| Verdict | Bar |
|---------|-----|
| SATURATED | ≥2 well-reviewed paid listings (prompt packs, GPTs, skills, Agensi itself), OR ≥1 well-adopted free Claude Code skill on a public skill marketplace, already cover the task well |
| PARTIAL | Listings/skills exist but are low-quality, generic, unreviewed, stale, or too narrow |
| OPEN | Genuine search — paid listings AND free skill marketplaces — found no decent existing coverage despite real demand signal |

This mirrors the INFRA rubric's shape but checks paid-listing saturation (PromptBase, Gumroad, GPT store, Agensi) *and* free skill-marketplace saturation (claudemarketplaces.com, claude-plugins.dev, skills.sh) instead of GitHub/papers — the right competitive set for something that will be sold, not open-sourced. The free-skill-marketplace check was added after cycle 20's test run: a HIGH-fit idea passed gap analysis only to hit `NOVELTY_FAIL` at skill-synthesis time against free competing skills gap-analyst hadn't checked for — catching that here instead avoids wasting a full skill-synthesis cycle.

### Marketplace Fit rubric (marketplace-idea-synthesizer)

Every MARKETPLACE-track idea gets a **Marketplace Fit** rating, independent of the Format tag:

| Rating | Bar |
|---|---|
| HIGH | Broad audience outside AI/agent builders; the task has real search/demand signal; resolves to one prompt-driven invocation (no persistent infra); a visible willingness-to-pay signal exists (people already pay for an adjacent or worse alternative) |
| MEDIUM | Meets most of the above but audience is narrower, or demand signal is thin, or no direct pricing comparison was found |
| LOW | Niche/AI-builder audience, or no willingness-to-pay signal — this idea probably belongs on the INFRA track instead |

Only `Marketplace Fit: HIGH` ideas that are also `Format: SKILL` or `BOTH` and already have a `marketplace-content/skills/<slug>/` directory (written by `marketplace-skill-synthesizer`, the MARKETPLACE track's own Phase 4) become candidates for packaging.

### Packaging & human approval gate

The `marketplace-packager` agent (the MARKETPLACE track's own Phase 5, at most once per cycle) turns a qualifying skill into `marketplace-content/candidates/<slug>/` (a copy of `SKILL.md` + a drafted `LISTING.md` with proposed title, category, price, and free/paid recommendation) and `marketplace-content/candidates/<slug>.zip`, then appends a `PENDING_REVIEW` row to `marketplace-content/review-queue.md`.

**The pipeline stops there.** It has no Agensi.io credentials and never uploads, lists, or prices anything itself. `marketplace-content/review-queue.md` is human-owned exactly like `ideas/INDEX.md` statuses — the pipeline appends new `PENDING_REVIEW` rows but never advances a row to `APPROVED`, `REJECTED`, or `LISTED`; only a human does that, after actually reviewing the zip and completing the listing on agensi.io/sell. See `marketplace-content/README.md` for the human-side workflow.
