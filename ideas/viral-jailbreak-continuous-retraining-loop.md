# Fresh Fence: A Continuous Jailbreak-Feed Retraining Loop for Guardrail Classifiers

- **Status**: PUBLISHED — [writeup](../published/viral-jailbreak-continuous-retraining-loop.md) (promoted 2026-11-13 cycle 49: recurrence — same stale-corpus-freshness gap resurfaced independently as P8 in research/2026-11-13-ai-safety-guardrails-in-production.md)
- **Date**: 2026-11-12
- **Topic**: AI safety & guardrails in production
- **Source**: research/2026-11-12-ai-safety-and-guardrails-in-production-pass2.md · P8
- **Maturity verdict**: PARTIAL — the academic "JailbreaksOverTime" paper (arXiv 2504.19440) shows weekly self-training on drifting jailbreaks cuts false-negative rate from 4% to 0.3%, a "rapid response" paper (arXiv 2411.07494, RapidResponseBench) proposes defending via proliferation of observed jailbreaks, and vendor 0DIN's "SusFactor" classifier trains on a continuously-growing, bug-bounty-sourced feed. None of this specifically targets hours-scale social-media viral spread, and the results are academic-only or self-reported, not production-proven at that cadence.
- **Format**: BOTH

## The Gap
An industry guide cited by WebSearch states that "users share working jailbreaks on Reddit within hours of discovery" — faster than typical model-update or classifier-retraining cycles, leaving a window where production guardrails are already bypassed by a publicly known technique before any defender has retrained against it. No cited product or OSS project wires a continuously-refreshed jailbreak-corpus feed directly into a production classifier's decision boundary at that cadence; the gap surfaces only as an observation in vendor explainer content, distinct from the general "keep classifiers fresh against drift" problem that has active academic work but no hours-scale production answer.

## The Project
A feed-to-retraining pipeline that monitors public jailbreak-disclosure surfaces (security-research feeds, disclosed red-team writeups, an opt-in community-submission channel modeled on 0DIN's bug-bounty-sourced intake) for newly circulating techniques, clusters and triages them by novelty against the classifier's current training set, and runs a scheduled (daily, not quarterly) self-training or few-shot-augmentation pass — applying the JailbreaksOverTime weekly-retraining result at a tighter cadence matched to observed viral spread speed, with a held-out eval gate so a bad retraining pass can't ship automatically.

## Tangible Impact
**Population**: teams operating production guardrail classifiers that rely on a static or infrequently-retrained model (the same `NeMo Guardrails`/`Guardrails AI`/`LLM Guard` user base, combined ~18k GitHub stars, as a proxy for deployment scale) whose coverage decays specifically against fast-circulating, publicly known jailbreak techniques rather than slow organic drift.
**Mechanism**: a classifier trained on a snapshot stays blind to a jailbreak technique for as long as the gap between disclosure and the next retraining cycle — often weeks to months — even though the JailbreaksOverTime result shows weekly retraining closes most of that gap. A feed tuned to hours-to-days cadence, with automated clustering and a held-out eval gate, closes the window specifically for techniques that are already circulating publicly, rather than waiting for the next scheduled model refresh.
**Measure**: time from a jailbreak technique first appearing in the monitored feed to the classifier being retrained and passing the held-out eval gate against it (target: single-digit days, down from a team's current retraining cadence); false-negative rate on a held-out set of newly disclosed techniques over time, replicating the JailbreaksOverTime 4%→0.3% result at a tighter cadence; false-positive rate added to legitimate traffic after each retraining pass (must stay flat or improve, not regress).

## Why Now
JailbreaksOverTime and RapidResponseBench both published in 2025/2026 showing retraining-against-drift works at a weekly cadence, and the specific hours-scale viral-spread observation is current 2026 industry commentary — the missing piece is wiring an intake feed and automated retraining loop at a cadence matched to the actual spread speed, which neither paper nor 0DIN's product does today.

## Skill Angle
Trigger: a team hands over their classifier's current training/eval cutoff date and a handful of recently disclosed jailbreak examples they're worried about. The skill assesses exposure (would these likely bypass the current classifier, based on technique similarity to the training set) and recommends retraining priority and cadence, as a one-shot audit before committing to the always-on feed-and-retrain infrastructure. The project is the continuous intake-cluster-retrain-eval pipeline; the skill is the point-in-time exposure assessment that justifies building it.
## MVP Sketch
A scheduled job that ingests a curated set of public jailbreak-disclosure sources, de-duplicates and clusters new submissions against the classifier's existing training examples (flagging genuinely novel clusters), triggers a self-training pass per the JailbreaksOverTime method on novel clusters only, and gates the retrained model behind a held-out eval before promotion. Single experiment: backtest against a known jailbreak-disclosure timeline (e.g., a documented technique's public-disclosure date) and measure how quickly the pipeline would have retrained and closed the gap versus the team's actual historical retraining cadence.

## Risks & Open Questions
- This overlaps with the decay-monitoring idea (Guard Drift) — the differentiator is active, feed-driven retraining at hours-to-days cadence versus passive detection/alerting of decay; needs to stay positioned as the correction loop Guard Drift's monitor would trigger, not a competing product.
- Automated retraining on scraped/community-submitted jailbreak examples is itself a poisoning vector if the intake isn't curated carefully.
- Evidence for the specific hours-scale claim is a single industry-guide citation, not a measured dataset — needs real disclosure-to-bypass timing data to validate the urgency.
- A held-out eval gate adds latency to the retraining loop that could itself become the bottleneck if not kept fast.
