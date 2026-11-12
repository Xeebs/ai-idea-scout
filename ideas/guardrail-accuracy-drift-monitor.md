# Guard Drift: Continuous Decay Monitoring for Guardrail Classifiers

- **Status**: EXPLORING
- **Date**: 2026-11-12
- **Topic**: AI safety & guardrails in production
- **Source**: research/2026-11-12-ai-safety-and-guardrails-in-production.md · P3
- **Maturity verdict**: PARTIAL — generic drift-monitoring building blocks exist (IBM runtime-monitoring dashboards, Galileo's threshold-based drift alerts) and several vendor posts restate the gap (Decagon, Arize, FutureAGI, a DEV Community post titled "Your guardrails are decaying and you aren't measuring it"), but no product or repo specifically monitors guardrail-check accuracy itself as a drifting metric, as opposed to model-output drift or agent-behavior drift.
- **Format**: BOTH

## The Gap
Decagon's glossary entry on guardrail evaluation states plainly that a guardrail which passed evaluation six months ago may no longer hold against today's input patterns — framed as a known, unaddressed gap. Everything else found (Arize, FutureAGI, IBM, Galileo, Dynamo AI) is adjacent generic drift tooling pointed at models or agent trajectories, or opinion content restating the problem. Nobody has pointed drift monitoring specifically at the guardrail classifiers themselves.

## The Project
A monitoring pipeline that treats guardrail check accuracy as the metric under surveillance, the way model-quality dashboards treat output quality: it periodically samples recent traffic that each guardrail category passed or blocked, re-scores a stratified subset with a stronger reference judge (or routes a slice to periodic human spot-check), computes a rolling precision/recall estimate per category, and alerts when a category's estimated accuracy crosses a configured threshold — surfacing which specific check is decaying and against what kind of input, with enough lead time to recalibrate before a real incident or user complaint forces the issue.

## Tangible Impact
**Population**: ops and trust-safety teams operating production LLM guardrail stacks whose input traffic shifts over time (customer support platforms, content moderation vendors, agent platforms) — specifically teams built on NeMo Guardrails, Guardrails AI, or LLM Guard (combined ~18k GitHub stars, a proxy for deployment scale) who today re-tune guardrails only reactively, after an incident or complaint.
**Mechanism**: guardrails evaluated once against a traffic snapshot silently lose accuracy as real input patterns shift (new jailbreak phrasing, new product surfaces, new user populations); without a dedicated decay signal, teams discover failures only after a missed-harm incident or an over-blocking complaint. A continuous monitor gives the specific decaying category and lead time to recalibrate proactively.
**Measure**: lead time between a decay alert firing and the next real incident/complaint tied to that category (goal: alert precedes incident); reduction in mean time-to-detect guardrail decay versus the team's prior reactive baseline; number of recalibrations triggered proactively by the monitor vs. reactively by an incident, post-adoption.

## Why Now
Decagon, Arize, Galileo, and IBM all published 2026 writeups naming the guardrail-decay gap explicitly, and the underlying building blocks — embedding-drift detectors, cheap reference-judge models — are now commodity and cheap enough to run on a continuous schedule rather than as a one-off evaluation.

## Skill Angle
Trigger: a team hands over a sample export of recent guardrail decision logs (inputs, verdicts, timestamps) spanning several months. The skill runs a point-in-time audit, re-scoring a stratified sample against a stronger reference judge and reporting which categories show accuracy drift and against what kind of input, as a one-shot diagnostic a team can run before committing to always-on monitoring. The project is the scheduled, always-on monitoring service with dashboards and alerting that the skill's audit logic runs continuously.

## MVP Sketch
A small service that ingests guardrail decision logs, samples a stratified subset weekly, re-judges the sample with a stronger reference model (or a periodic human-labeled gold slice), computes per-category precision/recall trend lines, and fires a dashboard/Slack alert on threshold breach. Experiment: backtest against a guardrail deployment with a known history of an emerging jailbreak technique and show the monitor would have flagged decay before the documented incident date.

## Risks & Open Questions
- Establishing "ground truth" to re-judge against is itself close to the guardrail problem — risk of circularity unless periodic human-labeled gold slices anchor the comparison, which adds cost.
- Could be dismissed as duplicating generic eval/drift tooling if the guardrail-specificity isn't kept front and center in the product.
- Needs real production-scale decision logs with real history to validate; a synthetic backtest is a weaker proof than a live deployment.
- Vendors already building generic drift dashboards (Galileo, IBM) could extend into this specific niche quickly once named.
