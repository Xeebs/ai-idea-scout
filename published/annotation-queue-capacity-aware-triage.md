# Budget Triage: A Capacity-Aware Re-Prioritization Layer for Human Annotation Queues

Every LLM observability vendor will happily hand your team an annotation queue. None of them will tell you what to do when that queue grows faster than the humans assigned to clear it — and for most teams running production LLM features, it already has.

## The Gap

A Tianpan blog post names the mismatch plainly: "your eval pipeline emits 800 traces per week for human review, while your annotators have about ninety minutes a week budgeted for it... adding more reviewers buys you a constant factor, while the eval pipeline keeps growing geometrically." That's not a hypothetical — it's the shape of the problem at any team whose traffic, and therefore flagged-trace volume, grows faster than headcount.

Arize's own documentation backs this up from the vendor side, describing its annotation queues as "cheap, biased toward extreme reactions, and rarely based on a rubric." Both Arize and Datadog ship the queue mechanism — a place to collect flagged items for human review — but neither ships a feature that actively reconciles incoming volume against a declared reviewer-time budget. The closest thing on record is Arize's own worked example of a human doing the sizing math by hand (400 flagged traces against a 150-review budget), and a vendor advisory post (Future AGI) recommending risk-based routing as a practice, not a product feature. Two separate 2026 preprints — a queueing-theory model (Lin & Zhang) and a budget-aware sampling paper (ACT-as-Human) — have worked out the theory. Nobody has wired it onto a live queue.

Worth saying up front: this gap sits firmly in PARTIAL territory, not a wide-open blank. The mechanism, the manual workaround, and the academic framing all already exist — what's missing is specifically the automated, continuous re-triage loop. That narrows the pitch but doesn't erase it: Datadog or Arize shipping this natively is a real and plausible near-term risk, which is why this is framed as middleware on top of their APIs rather than a replacement for them.

## The Project

The core idea is a triage layer that sits in front of whichever annotation queue a team already runs — Arize or Datadog, to start — and continuously reconciles incoming flagged-item volume against a team-declared reviewer-time budget. Instead of letting the backlog accumulate silently or get worked in arrival order (which tends to reward whatever landed most recently rather than whatever matters most), the triage engine re-ranks and trims the live queue by a combined risk, confidence, and disagreement score. Low-value items get deferred or dropped — visibly, with a reason attached, and with an override path, so the team is making a tradeoff it can see rather than discovering a three-week-old unreviewed pile.

Four pieces make this work: a budget config (reviewer-hours per week, a cost-per-review estimate); a scoring function blending model confidence, inter-judge disagreement, and a declared business-risk tier; a scheduler that re-ranks and trims against the queue API on a fixed cadence; and a transparency report naming exactly what got cut each cycle and why, so a human reviewer can pull something back in.

## Tangible Impact

**Population**: the annotators and ML/eval engineers staffing human-review queues for LLM outputs at companies running production LLM features at scale — concretely, teams already running Arize or Datadog's annotation-queue feature, a subset of the roughly 51% of companies surveyed in LangChain's 2024 State of AI Agents report that run agents in production, where review volume scales with traffic but annotator headcount (per Tianpan's cited example, often 1-3 people with under two hours/week budgeted) does not.
**Mechanism**: Without active triage, a growing review queue either silently accumulates (nothing gets reviewed in time, regressions slip through unreviewed) or gets reviewed in arrival order (the easiest/most-recent items crowd out the highest-risk ones). A capacity-aware triage layer makes the budget tradeoff explicit and optimizes it: the fixed reviewer-hours get spent on the highest-risk/highest-disagreement items first, and the team can see exactly what's being skipped instead of discovering a stale, unreviewed backlog.
**Measure**: backlog growth rate (items added minus items reviewed per week) before vs. after adoption, targeting near-zero net growth at a fixed reviewer-budget; percentage of known/injected high-risk cases caught within budget versus a first-in-first-out baseline on the same traffic; reviewer-reported time-to-triage per session.

## Try It

There's no standalone skill for this one yet — the idea is tagged `Format: BOTH`, but no `skills/annotation-queue-capacity-aware-triage/` has been written. If that changes, this section will link it. For now, the one-shot version described in the idea file would take a queue export (item counts, confidence scores, disagreement flags, risk tags) plus a stated reviewer-hours budget and hand back a ranked review order with a cut line — but that's a design sketch, not a built artifact. Treat the continuous middleware described above as the real proposal; the skill angle is a smaller, weekly-planning-aid version of the same scoring logic, for teams not ready to run live middleware.

## The Honest Risk

If Arize or Datadog ship this as a native feature — and both are plausible candidates, since they already surface the sizing math manually in their own docs — the standalone layer's value narrows fast, to teams running other or self-hosted queue tooling. The scoring function is also the single point of failure: a miscalibrated score silently drops the wrong items, which is exactly why the transparency report and override path aren't a nice-to-have here, they're the whole point. And validating that the triage policy caught "the right things" requires a ground-truth labeled set most teams don't have until after an incident — the realistic validation path leans on hindsight replay against known-bad weeks, not a clean benchmark.

---

Surfaced from `research/2026-11-20-llm-evaluation-observability-ii.md`, pattern `P3`.
