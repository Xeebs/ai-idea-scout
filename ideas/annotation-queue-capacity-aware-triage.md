# Budget Triage: A Capacity-Aware Re-Prioritization Layer for Human Annotation Queues

- **Status**: EXPLORING (promoted 2026-11-20 cycle 290: evidence density — ≥2 independent threads)
- **Date**: 2026-11-20
- **Topic**: LLM evaluation & observability
- **Source**: research/2026-11-20-llm-evaluation-observability-ii.md · P3
- **Maturity verdict**: PARTIAL — Datadog LLM Observability and Arize ship the annotation-queue mechanism itself; Arize's own docs give a worked manual sizing example (400 flagged traces → 150-review budget) but as something a human calculates once, not an automated re-triage feature. An arXiv queueing-theory paper (Lin & Zhang, 2603.13870) and a separate budget-aware-sampling preprint (ACT-as-Human, 2511.09833) model the problem academically. No shipped product actively re-triages a queue against a declared reviewer-time budget.
- **Format**: BOTH
- **Data Sources**: CONNECTED — reads flagged-trace volume and reviewer-time logs directly from Arize's AX annotation-queue API or Datadog LLM Observability's annotation-queue API (both mature, existing products with documented APIs today); the triage engine sits as middleware re-ordering/trimming items within whichever queue the team already runs, rather than replacing it.

## The Gap
A Tianpan blog post states the mismatch directly: "your eval pipeline emits 800 traces per week for human review, while your annotators have about ninety minutes a week budgeted for it... adding more reviewers buys you a constant factor, while the eval pipeline keeps growing geometrically." Arize's own annotation-queue docs independently acknowledge such queues are "cheap, biased toward extreme reactions, and rarely based on a rubric." Both named observability vendors (Datadog, Arize) ship the queue as a mechanism but neither ships an active re-triage feature that reconciles incoming volume against a stated reviewer-capacity budget — the routing-by-risk idea exists only as vendor advisory blog content (Future AGI), not a confirmed shipped feature.

## The Project
A capacity-aware triage layer that sits in front of an existing annotation queue (Arize or Datadog, to start) and continuously reconciles incoming flagged-item volume against a team-declared reviewer-time budget. Instead of the queue accumulating unboundedly, the triage engine re-ranks and trims the live queue by a combined risk/confidence/disagreement score, dropping or deferring low-value items and surfacing exactly which items were cut and why — so the team is making a visible, reversible tradeoff rather than discovering an invisible backlog three weeks later.

Components: a budget config (reviewer-hours/week, cost-per-review estimate); a scoring function combining model confidence, inter-judge disagreement, and declared business risk tier; a re-ranking/trimming scheduler running against the queue API on a set cadence; a transparency report naming every item dropped this cycle and the score that dropped it, so a reviewer can override.

## Tangible Impact
**Population**: the annotators and ML/eval engineers staffing human-review queues for LLM outputs at companies running production LLM features at scale — concretely, teams already running Arize or Datadog's annotation-queue feature, a subset of the roughly 51% of companies surveyed in LangChain's 2024 State of AI Agents report that run agents in production, where review volume scales with traffic but annotator headcount (per Tianpan's cited example, often 1-3 people with under two hours/week budgeted) does not.
**Mechanism**: Without active triage, a growing review queue either silently accumulates (nothing gets reviewed in time, regressions slip through unreviewed) or gets reviewed in arrival order (the easiest/most-recent items crowd out the highest-risk ones). A capacity-aware triage layer makes the budget tradeoff explicit and optimizes it: the fixed reviewer-hours get spent on the highest-risk/highest-disagreement items first, and the team can see exactly what's being skipped instead of discovering a stale, unreviewed backlog.
**Measure**: backlog growth rate (items added minus items reviewed per week) before vs. after adoption, targeting near-zero net growth at a fixed reviewer-budget; percentage of known/injected high-risk cases caught within budget versus a first-in-first-out baseline on the same traffic; reviewer-reported time-to-triage per session.

## Why Now
Arize and Datadog's annotation-queue APIs are mature and already in production use in 2026, and the underlying academic framing (queueing theory under a reviewer budget, budget-aware sampling) has already been worked out in two independent 2026 preprints — the missing piece is wiring a scoring-and-trim loop onto an existing queue API rather than inventing new infrastructure.

## Skill Angle
Trigger: a team's lead annotator or eval engineer wants a one-time recommendation on how to triage this week's backlog without installing continuous middleware. Inputs: the current queue export (item count, confidence scores, disagreement flags, risk tags, pasted as a CSV/JSON) and the stated reviewer-hours budget for the period. Output: a ranked review order with a cut line marking which items fit the budget, a one-line reason per cut item, and a rough estimate of how much of the declared budget the recommended plan actually consumes. The skill is a one-shot weekly planning aid; the project is the continuously-running middleware re-triaging the live queue automatically.

## MVP Sketch
2–3 weeks, 1–2 people: build against Arize's annotation-queue API first (documented, mature), implement the confidence+disagreement scoring function, and a trim/re-rank job running once daily. Validate on one team's real queue history: replay a known week's traffic against both FIFO and the triage policy, and measure whether the triage policy would have surfaced the same high-risk cases the team already knows (in hindsight) mattered most, within the same reviewer-hour budget.

## Risks & Open Questions
- A triage policy that silently drops low-scored items could create a blind spot if the scoring function itself is miscalibrated — the transparency report and override mechanism are load-bearing, not optional.
- If Arize or Datadog ship this as a native feature in the near term (both are plausible candidates given they already surface the sizing math manually), the standalone layer's value narrows to teams on other/self-hosted queue tooling.
- Measuring "did we catch the right things" requires a ground-truth labeled set of what actually mattered, which many teams don't have until after an incident — the MVP's validation leans on hindsight review rather than a clean held-out benchmark.
- Reviewer trust in an automated triage decision may lag; adoption likely requires a transparent override path from day one, not a black-box ranking.
