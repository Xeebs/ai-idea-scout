# Cohort Watch: A Per-Segment Regression Gate for Distilled Small Models

A team distills a model for one narrow production task. The aggregate eval score ticks up two points. They ship. Weeks later they discover the regression was never actually fixed — it just moved, concentrating entirely in their highest-value customer cohort, invisible to a benchmark that only ever looked at the average. That exact failure is documented, by name, in vendor guidance from two independent sources. The fix they both recommend — evaluate per cohort, not just in aggregate — exists nowhere as a tool. Only as advice.

## The Gap

FutureAGI's glossary content describes the failure mode directly: a team distills a model, the global eval score improves, they ship, and only afterward discover "the regression is concentrated on the highest-value cohort." Redwerk's distillation guidance independently names "no real eval data exists" as a reason a distillation project shouldn't even start — implying that the eval sets most teams do have aren't built to catch this. Predibase's own distillation playbook adds a third independent voice recommending the same practice: build a production-shaped, cohort-stratified eval set rather than trusting a synthetic or aggregate one.

Three vendors, three independent write-ups, one unaddressed recommendation. A multi-channel search for anything that actually implements it — `gh search repos` for cohort- or segment-level model-eval tooling, plus a broader web search — turned up nothing closer than ModelScope's EasyDistill, which is a distillation pipeline, not an eval tool, and has no cohort-eval feature at all. The advice is everywhere. The tool is nowhere.

## The Project

Cohort Watch is a cohort-aware evaluation harness built for one specific moment: the point just before a team promotes a distilled, fine-tuned, or quantized model to replace whatever is currently in production. It takes a labeled eval set tagged by cohort — language or dialect, device tier, customer segment, edge-case category, whatever the team already knows matters — and runs both the outgoing and incoming model against it. Instead of reporting one number, it reports one number per cohort, with a significance check on each delta, and it fails the promotion if any single cohort regresses past a configurable threshold, no matter how good the aggregate looks.

Wired into CI, it becomes a release gate that never lets a global improvement paper over a cohort-level regression again. The pieces are small by design: a labeled-eval ingestion format, a per-cohort delta calculator with a statistical floor to avoid false alarms on small cohorts, and a pass/fail gate with the specific at-risk cohorts named in the output — not just a red X.

## Tangible Impact

**Population**: ML/MLOps teams shipping task-specific distilled or fine-tuned small models to production — a population Gartner projects will triple its use of small, task-specific models relative to general-purpose LLMs by 2027, and which a Snorkel AI survey found 74% of respondent organizations intended to pursue via distillation — and, transitively, the specific customer cohorts (a minority dialect, an edge-case device type, a long-tail product category) whose outcomes silently regress when a global score masks a cohort-level drop, exactly as FutureAGI's and Redwerk's documented cases describe.

**Mechanism**: Today's eval sets are built to be representative by accident, not stratified by cohort, so a 2-point aggregate improvement can hide a double-digit regression in one segment — discovered only after the affected customers complain or churn. Requiring and checking cohort-tagged data turns that into a pre-release block instead of a post-incident autopsy.

**Measure**: (1) rate of cohort-level regressions caught pre-ship versus the team's prior aggregate-only process, backtested against a reconstruction of a known regression case; (2) post-ship cohort-specific error-rate trend before versus after adopting the gate; (3) added time/cost per release cycle, to confirm the check is cheap enough that teams actually run it every time rather than skip it under deadline pressure.

## Why Now

Distillation adoption is accelerating — Gartner's 2027 forecast and Snorkel's 74%-intent survey both point the same direction — faster than eval practice is maturing to match it. That's the exact window where a cheap, drop-in gate has the most leverage: before teams entrench an aggregate-only habit that gets harder to dislodge the longer it ships without visible failure.

## Try It

A companion skill already exists: **Cohort Watch: Per-Cohort Regression Gate** (`skills/distilled-model-cohort-regression-gate/`) — "Given a labeled eval set tagged by cohort plus a baseline and candidate model's outputs on it, computes per-cohort accuracy deltas with a paired significance check and returns a go/no-go ship recommendation that names any cohort regressing even while the aggregate score improves." It's the one-shot judgment version of the idea — useful today even before anyone builds the full CI-wired pipeline. Paste the README's prompt template into any AI chat tool along with your eval data, or drop the `skills/distilled-model-cohort-regression-gate/` folder into `~/.claude/skills/` for Claude Code.

## The Catch

The hard part this tool doesn't solve: defining cohorts that actually matter is a domain-judgment call, not a naive demographic slice, and getting it wrong courts its own fairness and legal exposure. Small cohorts also make regression detection statistically noisy, which is why the gate needs a documented minimum-sample floor rather than flagging every small-sample wobble as a crisis. And the obvious long-term risk to this project specifically: once the pattern is named publicly, a well-resourced eval vendor — Arize, Galileo, Braintrust — could bolt cohort-aware gating onto an existing platform fast, shrinking this project's edge to "shipped it first" rather than "owns the category."

---

Surfaced from `research/2026-11-14-small-and-local-models.md`, pattern `P3`.
