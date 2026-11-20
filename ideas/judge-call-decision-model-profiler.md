# Hidden Rule: A Decision-Model Discovery Profiler for Disguised LLM-Judge Calls

- **Status**: PROPOSED
- **Date**: 2026-11-20
- **Topic**: LLM evaluation & observability
- **Source**: research/2026-11-20-llm-evaluation-observability.md · P5
- **Maturity verdict**: OPEN — `gh search repos` for "LLM judge replace deterministic decision model" and "LLM judge cost profiler pipeline" returned zero relevant results. Openlayer's "jevals" lets a team manually swap an already-identified LLM-judge step for a typed decision definition, but requires the user to already know which calls qualify — it doesn't discover them. A DEV Community reference to a "PAJAMA" judge-distillation paper is unverified and, even if real, distills one already-chosen judge rather than auditing a whole pipeline to find which calls are secretly deterministic routing decisions. No discovery/profiling tool matching this pattern was found anywhere.
- **Format**: BOTH — the always-on profiler that scans a pipeline's live or historical judge-call logs needs continuous or periodic access to a running trace store; a one-shot "here are N example judge calls, is this a disguised rule?" assessment is a separable judgment task.
- **Data Sources**: CONNECTED — reads a pipeline's historical LLM-judge/classification call logs (inputs, outputs, and any confidence scores) via the team's existing observability or tracing platform (PostHog AI evals, Langfuse, Braintrust, or a generic OpenTelemetry trace store) — these trace-storage APIs already exist and are mature; what's missing is the decision-boundary-discovery profiler built on top of them.

## The Gap
Hacker News "Not Everything Needs an LLM" (newsletter.posthog.com/p/decision-models, 2026-11-17, 186 points/75 comments — the highest-engagement item in this digest, strongly complaint-shaped against reflexive LLM-judge use) argues a meaningful subset of LLM-judge or LLM-classification calls in production pipelines are really just routing/threshold decisions in disguise, and should be swapped for a small deterministic decision model. The piece is an essay, not a tool. No tool was found that profiles an *existing* eval/observability pipeline's judge calls and automatically flags which specific ones are decision-model-replaceable, as distinct from manually swapping a call a human has already singled out.

## The Project
A profiler that connects to a pipeline's existing trace/observability store, pulls historical input/output pairs for each distinct LLM-judge or LLM-classification call site, and tests whether that call site's outputs are well-explained by a simple deterministic rule over fields already present in the input (a threshold on a numeric field, a regex/keyword match, a lookup against an existing enum) rather than genuinely needing LLM judgment. Call sites that pass this test are surfaced in a ranked report — proposed rule, estimated agreement rate against historical LLM-judge verdicts, and estimated cost savings — for a human to approve before any swap happens. This targets discovery specifically: finding the candidates, not training or distilling a classifier for calls that are already known to need learned judgment (that distillation-and-swap problem is the separately-scoped `eval-ground-truth-classifier-autoswap.md` already in this ledger).

## Tangible Impact
**Population**: engineering teams running production pipelines with multiple LLM-judge or LLM-classification call sites (support-ticket routing, moderation flags, data-quality gates) who suspect — per the HN piece's own framing and its 75-comment discussion — that some of these calls are reflexive LLM use rather than genuine judgment, but have no systematic way to find which ones without manually auditing every call site by hand.
**Mechanism**: automatically surfacing which specific judge calls reduce to a simple rule, with an estimated agreement rate against the LLM's own historical verdicts, lets a team cut latency and cost on exactly the calls where an LLM was never adding judgment, without needing to manually review every call site or risk swapping one that still needs real judgment.
**Measure**: number of call sites correctly identified as rule-replaceable per 100 audited (validated against held-out historical verdicts); latency/cost reduction achieved on swapped call sites; false-swap rate (a swapped call site whose later real-world agreement with the LLM drops below the estimate, triggering review).

## Why Now
The HN piece's unusually high engagement (186 points/75 comments, the digest's top item) signals this is a live, widely-felt complaint right now, and the underlying mechanics — pipelines now routinely log judge-call inputs/outputs through mature observability platforms — make a profiler buildable today without any new model capability.

## Skill Angle
Trigger: a team wants a quick read on whether a specific LLM-judge or classification call looks like a disguised deterministic decision, without wiring up the full live profiler. Inputs: a batch of 15–30 example (input, LLM-judge-output) pairs for one call site. Output: a verdict on whether a simple rule (named explicitly, e.g. "flag if `confidence_score > 0.85`") would reproduce the LLM's outputs closely enough to be worth testing further, plus the estimated agreement rate on the provided sample. This is the no-infrastructure version of the same discovery logic the full profiler runs continuously against live trace data.

## MVP Sketch
2–4 weeks, 1–2 people: build the rule-fitting core (test a handful of simple rule families — threshold, regex/keyword, enum lookup — against historical input/output pairs) against one real or realistic pipeline's judge-call log export, validate the ranked-report output against a manually-audited ground truth of "which of these 10 call sites did a human agree are actually rule-shaped," and confirm the profiler's top-ranked candidates match the human's independent judgment.

## Risks & Open Questions
- Closely adjacent to `eval-ground-truth-classifier-autoswap.md` already in this ledger — that idea trains a distilled classifier from labeled ground truth for tasks that genuinely need a learned model; this idea discovers calls that need no learned model at all, just a rule. The boundary must stay explicit in any future synthesis or skill-synthesis pass to avoid the two ideas drifting into the same build.
- A call site that *looks* rule-shaped on historical data could still fail on inputs outside the sampled distribution — the profiler's agreement estimate is only as good as how representative the historical sample is.
- Teams may resist swapping LLM judgment for a rule even with strong evidence, out of concern for edge cases the rule can't articulate — the project's value is partly organizational (making the case), not purely technical.
- If Openlayer or a similar vendor adds a discovery/profiling feature on top of its existing manual-swap "jevals" tool, this idea's standalone value narrows quickly.
