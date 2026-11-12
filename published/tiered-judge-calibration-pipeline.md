# Judge Check: A Tiered Calibration Pipeline Against Known LLM-as-Judge Bias

Every CI gate and quality dashboard that leans on an LLM judge is quietly trusting a number nobody has actually checked recently. The evidence that this trust is misplaced is now public and specific — but the fix is still scattered across a PyPI package, a few papers, and one blog post, waiting for someone to wire it together.

## The Gap

An arXiv preprint (2606.19544) evaluating 21 judges across 9 providers found something uncomfortable: test-retest reliability above 0.95 — the judge is consistent — coexisting with position bias above 0.10 in two production-deployed judges. Consistency isn't the same as correctness, and the paper shows a judge can be reliably, confidently wrong about which answer wins depending on which side of the prompt it's shown on. Google said as much in public in late October 2026 (reported via IT Brief): "LLM judges are not objective arbiters of truth... they are subjective models with their own distinct biases." That's not a hedge in a methods section — that's the company shipping some of the most-used judge models admitting the thing teams quietly hope isn't true.

Practitioners already know this and are reacting individually. Adaline.ai's April 2026 write-up reported an 11.2-point agreement lift just from stacking position-swapping, chain-of-thought, and an explicit rubric onto an existing judge call. A calibration library, `judicator`, shipped on PyPI (v0.2.4) that auto-detects judge type and screens for concreteness and yes-bias. NUS released a calibration-method pipeline and dataset in the same window. Every piece of the fix exists. None of them are wired into one thing a team can adopt — each is an individually-authored mitigation, not a shared reference implementation, which means every team rediscovering the bias problem also has to rediscover (or skip) the fix from scratch.

## The Project

The pipeline runs eval traffic through three tiers instead of one judge call:

1. **Deterministic checks on everything.** Format, schema, forbidden-content, and length rules catch what doesn't need a model's opinion at all, for free, on 100% of traffic.
2. **A bias-mitigated judge pass on what's left.** Position-swapping, chain-of-thought, and an explicit rubric — the exact recipe Adaline.ai validated — applied as a wrapper around `judicator`'s existing detection logic rather than reimplementing judge-type and bias detection from zero.
3. **A rolling human-gold calibration set, measured continuously.** Not a one-time sanity check at launch — a live "judge agreement with humans this week" number that triggers a correction when it drifts, the same philosophy as a golden-eval-set drift monitor applied to the judge itself instead of the eval data.

The centerpiece is tier 3: most teams either trust a frozen judge prompt forever or hand-tune it once after a bad incident. This pipeline treats judge trust as a number that can go stale and gets re-measured on a schedule, with the deterministic and bias-mitigated tiers doing the work of keeping the judge-call volume (and bill) down.

## Tangible Impact

**Population**: ML/eval engineers at companies running LLM-as-judge in a CI gate or production quality dashboard — specifically teams that have read or been burned by the position-bias findings (the same audience as the 21-judge arXiv benchmark and Google's public walk-back of judge objectivity) but have no off-the-shelf way to act on it beyond ad hoc prompt tweaks.

**Mechanism**: Today teams either trust a single LLM-judge score uncritically, inheriting its documented position/self-preference bias, or hand-roll one mitigation technique at a time (as the Adaline.ai post shows). The tiered pipeline makes "how much do I trust this score" a continuously measured number instead of an assumption, catching judge drift the same way a golden-eval-set drift monitor catches data drift.

**Measure**: (1) judge-human agreement rate tracked weekly against the gold set, with calibration corrections triggered automatically when it drops below a threshold; (2) reduction in judge-driven false CI passes/fails on a labeled regression set, targeting at least the +11-point lift Adaline.ai reported from a single technique; (3) share of eval traffic resolved by the free deterministic tier (no judge call needed), directly cutting judge-call cost.

## Try It

No companion skill has been built for this idea yet — it's tagged `BOTH` in the idea file (a one-time "audit my judge setup" review is a separable task from the always-on pipeline), but the skill directory doesn't exist in this repo yet. Check back, or if you're building this yourself, the idea file's Skill Angle section sketches the exact trigger, inputs, and output such a review would produce.

In the meantime, the honest starting point is `judicator` on PyPI (v0.2.4) — it already does judge-type detection and concreteness/yes-bias screening, which is the piece this pipeline is designed to wrap rather than replace.

Worth saying plainly: a well-funded eval vendor (Braintrust, Galileo) or `judicator` itself could extend into the full three-tier pipeline before anyone else does — the calibration piece is already partially built by someone else, which is the strongest reason this gap might close on its own rather than staying open for a new entrant.

---

Surfaced from `research/2026-11-11-llm-evaluation-observability.md`, pattern `P7`.
