# Dead Pipeline Alarm: A Zero-Score Health Check for Production Eval Pipelines

You wire up evaluation against your production LLM traces, watch the first few runs come back green (or at least present), and move on. Weeks later you discover the pipeline has been running flawlessly — and scoring nothing. No crash, no error, no red banner. Just a dashboard that's been flat for a while, quietly telling you nothing at all. That's exactly what happened to the developer behind a dev.to post titled "I switched on production evals for my LLM app and they scored nothing," and it's not an isolated story: two more engineers independently wrote up the same failure — `gorelik.net`'s "When your LLM pipeline silently returns zero" and `tianpan.co`'s on-call postmortem — all within the same month. Three unrelated teams, same silent death.

## The Gap

The failure mode is specific and nasty: an eval pipeline runs to completion, exits with no error, and produces zero usable scores — or worse, a suspiciously constant score across every sample, the kind of thing a silently-null-coerced-to-zero bug produces. Nothing about that looks broken from the outside. No vendor searched — not Langfuse, not Braintrust, not Confident AI, not FutureAGI — advertises a dedicated "is my eval pipeline actually scoring anything" health check as a feature. The closest thing to help is DeepEval's documentation on exporting scores to Prometheus, which is wiring, not a sanity check; it tells you how to pipe the numbers somewhere, not how to notice when there aren't any. The gap-analyst's search (GitHub plus web, for monitoring products and the specific failure mode) came back with exactly the same shape of result: after-the-fact blog posts describing the incident, and generic DIY advice for building your own alerting from scratch. Nobody has shipped the check itself.

What makes this worth building rather than just complaining about: teams hitting this aren't eval-tooling novices. These are people who already invested in running evaluation against production traces — the exact population you'd expect to have caught this — and they still got burned, because the tools they adopted don't watch themselves.

## The Project

The idea is a small, framework-agnostic sidecar that reads an eval pipeline's own existing output — the JSON/SQLite run files that promptfoo and deepeval already produce, or the OTel GenAI metrics a production pipeline may already export — and watches for three specific dead-pipeline signatures instead of one vague "something's wrong":

1. A run completes with 0% of samples receiving any score at all.
2. A run's score distribution collapses to a single constant value across every sample — the fingerprint of a scorer silently returning `null` on some error path that then gets coerced to zero.
3. A scheduled or cron-triggered eval simply stops firing, with no run showing up where one was expected.

Each signature fires a named alert — "zero-score run detected," not a generic "eval failed" — through a configurable webhook (Slack, PagerDuty) or as a CI exit code. Under the hood it's four pieces: a thin parser per supported export format (promptfoo JSON, deepeval JSON, OTel GenAI metrics), a rolling-baseline comparator whose entire job is telling "scores are legitimately low" apart from "scores didn't compute at all," an alerting webhook layer, and a CLI (`dead-pipeline-check <run-dir-or-endpoint>`) for running it ad hoc or gating it in CI.

The reason this isn't a feature bolted onto something else: the comparator *is* the product. Catching a zero is trivial; catching a zero without crying wolf on every day your model under test genuinely performs badly is the actual engineering problem, and it's the one piece nobody in the evidence trail — vendor or DIY — has built yet.

## Tangible Impact

**Population**: engineering teams running scheduled or CI-gated LLM evaluation against production traces using promptfoo, deepeval, or a custom OTel-instrumented pipeline — the same population the dev.to post, `gorelik.net`, and `tianpan.co` write-ups all describe discovering this failure the hard way. These are specifically teams who already invested in eval infrastructure and still got burned by it going quietly dark.

**Mechanism**: converts a failure mode that today surfaces only as a post-incident blog post into an immediate, named alert at the moment the pipeline first produces zero/constant scores, closing the exact gap (no vendor advertises this check) identified in the gap-analyst's verdict.

**Measure**: time from a pipeline going dead to an alert firing (target: within one run cycle, not weeks); false-positive rate on the "legitimately low scores vs. didn't compute" distinction (target: comparable to a standard anomaly-detection baseline); number of distinct dead-pipeline signatures caught in a backtest against the three documented real incidents cited as evidence.

Worth being honest about the risks here rather than glossing them: the hardest technical problem — telling "the system under test actually got worse" apart from "the eval pipeline itself broke" — is exactly the part most likely to generate false positives that erode trust if it's not tuned carefully, and it's also the single reason this might not stay open for long. This is a small, obvious feature for an incumbent observability vendor to ship; any of Langfuse, Braintrust, Confident AI, or FutureAGI could add a version of this to their dashboard at any time, and the differentiation window for a standalone build may be short. There's also a live open question about whether OTel GenAI metrics export is standardized enough across frameworks yet to build one adapter, or whether promptfoo and deepeval each need bespoke parsers — and whether teams would rather install a separate sidecar at all versus wanting this folded into the eval framework they already run.

## Try It

A companion Claude Code skill exists at `skills/eval-pipeline-zero-score-health-check/`: *"One-shot diagnostic audit of an LLM eval pipeline's config and recent run output to catch silent zero/constant-score failures before they go unnoticed in production."* It's the one-time audit version of this idea, separate from the always-on sidecar — you paste in your pipeline's config (promptfoo YAML, deepeval test file, or OTel exporter config) plus the output of your last 2-3 runs, and it flags specific risk patterns — a scorer that silently returns `null` on some error path, a cron schedule with no completion check — before you've ever wired up ongoing monitoring at all.

To use it: paste the contents of `skills/eval-pipeline-zero-score-health-check/README.md` into any AI chat tool along with the config and run output it asks for, or, if you use Claude Code, drop the whole `eval-pipeline-zero-score-health-check/` folder into `~/.claude/skills/` so Claude can reach for it automatically next time you're reviewing an eval pipeline.

---

Surfaced from `research/2026-11-13-llm-evaluation-observability.md`, pattern `P5`.
