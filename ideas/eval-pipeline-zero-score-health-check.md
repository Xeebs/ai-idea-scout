# Dead Pipeline Alarm: A Zero-Score Health Check for Production Eval Pipelines

- **Status**: EXPLORING (promoted 2026-11-13 cycle 57: evidence density — ≥2 independent threads, the triggering dev.to post corroborated independently by gorelik.net's "When your LLM pipeline silently returns zero" and tianpan.co's on-call postmortem, all three describing the same silent zero-score failure)
- **Date**: 2026-11-13
- **Topic**: LLM evaluation & observability
- **Source**: research/2026-11-13-llm-evaluation-observability.md · P5
- **Maturity verdict**: OPEN — multi-channel search (GitHub + WebSearch for monitoring/alerting products and for the specific failure mode) found only after-the-fact blog write-ups of the failure (the triggering dev.to post, plus `gorelik.net`'s "When your LLM pipeline silently returns zero" and `tianpan.co`'s on-call postmortem) and generic DIY advice (DeepEval's docs mention exporting scores to Prometheus, but that's wiring, not a built-in sanity check). No vendor (Langfuse, Braintrust, Confident AI, FutureAGI) advertises a dedicated zero-score/dead-pipeline health check as a feature.
- **Format**: BOTH
- **Data Sources**: CONNECTED — reads the eval run's score output directly from the eval framework's own existing export surfaces: promptfoo/deepeval's local JSON/SQLite run output, or an OTel GenAI metrics exporter already configured for a production eval pipeline (DeepEval's docs already document exporting scores to Prometheus this way). Those export surfaces are mature and already exist today; the zero-score/dead-pipeline health-check logic sitting on top of them — the actual product here — does not exist yet and is what this idea builds.

## The Gap

A dev.to post titled "I switched on production evals for my LLM app and they scored nothing" describes turning on evaluation against live production traces and having the pipeline run without error while producing no usable scores — a silent failure the eval tool itself never surfaced as an alert. Two independent corroborating write-ups (`gorelik.net`'s "When your LLM pipeline silently returns zero" and `tianpan.co`'s on-call postmortem) describe the same pattern as a cautionary tale discovered only after the fact. No eval or observability vendor searched advertises a built-in "is my eval pipeline actually scoring anything" check — teams are left to notice a flat line on a dashboard they may not be watching.

## The Project

A small, framework-agnostic sidecar that watches an eval pipeline's own run output (via the existing JSON/SQLite/OTel export surfaces promptfoo, deepeval, and OTel-GenAI-instrumented pipelines already produce) and flags three specific dead-pipeline signatures: (1) a run completes with 0% of samples receiving any score, (2) a run's score distribution collapses to a single constant value across all samples (a classic silent-null-coerced-to-zero bug), and (3) a scheduled/cron eval run silently stops firing at all. Each signature triggers a configurable alert (Slack/PagerDuty webhook, exit code for CI) with the specific signature named, not a generic "eval failed."

Core components: (1) a thin parser/adapter per supported export format (promptfoo JSON, deepeval JSON, OTel GenAI metrics); (2) a rolling-baseline comparator that distinguishes "scores are legitimately low" from "scores didn't compute at all"; (3) an alerting webhook layer; (4) a CLI `dead-pipeline-check <run-dir-or-endpoint>` for ad hoc or CI-gated use.

## Tangible Impact

**Population**: engineering teams running scheduled or CI-gated LLM evaluation against production traces using promptfoo, deepeval, or a custom OTel-instrumented pipeline — the same population the dev.to post, `gorelik.net`, and `tianpan.co` write-ups all describe discovering this failure the hard way. These are specifically teams who already invested in eval infrastructure and still got burned by it going quietly dark.

**Mechanism**: converts a failure mode that today surfaces only as a post-incident blog post into an immediate, named alert at the moment the pipeline first produces zero/constant scores, closing the exact gap (no vendor advertises this check) identified in the gap-analyst's verdict.

**Measure**: time from a pipeline going dead to an alert firing (target: within one run cycle, not weeks); false-positive rate on the "legitimately low scores vs. didn't compute" distinction (target: comparable to a standard anomaly-detection baseline); number of distinct dead-pipeline signatures caught in a backtest against the three documented real incidents cited as evidence.

## Why Now

The triggering dev.to post and its two corroborating write-ups all surfaced within this digest's 30-day window, and the gap-analyst's multi-channel search confirms the DIY-Prometheus-wiring advice that exists today stops short of actually implementing the check — there is a validated, newly-visible gap with no incumbent racing to close it yet.

## Skill Angle

A Claude Code skill, separable from the running sidecar, that performs a one-time diagnostic review of an eval pipeline's config and recent run logs to assess dead-pipeline risk before the sidecar is ever installed. **Trigger**: a developer pastes their eval pipeline's config (promptfoo YAML, deepeval test file, or OTel exporter config) plus the output of their last few runs. **Inputs**: the config file and 2-3 recent run outputs, pasted verbatim. **Output**: a short report flagging specific risk patterns (e.g. a scorer that silently returns `null` on a particular error path, a cron schedule with no completion check) and a concrete fix recommendation. This differs from the project: the project is the always-on monitoring sidecar; the skill is a one-shot audit a team can run immediately, before they've wired up any ongoing monitoring at all.

## MVP Sketch

Two to three weeks, 1-2 people: build the promptfoo JSON adapter and the zero-score/constant-score detector first (the two most mechanically simple and most-cited signatures), wire a Slack webhook alert, and validate against a synthetic reproduction of the dev.to post's exact failure (a judge call that silently returns `null` on a particular input shape) plus a real promptfoo project the builders run themselves in CI for two weeks.

## Risks & Open Questions

- Strongest reason this might already be solved: a vendor could ship this as a dashboard feature at any time — it's a small, obvious addition for an incumbent to add, so differentiation may be short-lived.
- Distinguishing "legitimately low/zero scores because the system under test is actually bad" from "the eval pipeline itself is broken" is the hard part and risks false positives that erode trust if not tuned carefully.
- Open question: whether OTel GenAI metrics export is standardized enough yet across frameworks to build one adapter, or whether each framework needs a bespoke parser (increasing scope).
- Open question: whether teams would actually install a separate sidecar vs. wanting this folded into the eval framework they already run (promptfoo/deepeval upstream contribution path vs. standalone product).
