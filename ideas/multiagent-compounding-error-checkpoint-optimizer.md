# Break Point: A Compounding-Error Checkpoint Optimizer for Chained Agent Pipelines

- **Status**: PROPOSED
- **Date**: 2026-11-13
- **Topic**: Multi-agent architectures
- **Source**: research/2026-11-13-multi-agent-architectures-ii.md · P5
- **Maturity verdict**: PARTIAL — the compounding-math critique is repeated across many vendor blogs; one academic mitigation (COCO, arXiv:2508.13815, asynchronous oversight decoupled from execution, +6.5% avg. benchmark improvement) is a narrow single paper, not a maintained/adopted tool, and practitioners openly disagree on which mitigation works — no shipped, validated measurement/correction tool exists.
- **Format**: BOTH
- **Data Sources**: Project — CONNECTED, reads step-level success/failure data from the team's own tracing platform (LangSmith, Langfuse, or generic OpenTelemetry GenAI spans), which already exist maturely; this idea builds the compounding-analysis layer on top. Skill MVP — MANUAL, the user pastes a description of their pipeline's steps plus 10–20 recent failure/success log excerpts verbatim.

## The Gap
A widely repeated critique (zeli.app and multiple vendor blogs, per the digest) argues that chaining N agents at an independent error rate doesn't average errors out via "wisdom of crowds" — it compounds them. The one academic mitigation found, COCO, is a single unmaintained paper, and practitioners openly disagree on remedies (some see mid-chain verification as adding latency without value). No tool measures how much a *specific* team's pipeline actually compounds, or where to put a checkpoint to fix it cheaply.

## The Project
A diagnostic/benchmarking harness that takes a team's actual multi-step agent pipeline (e.g. research → draft → review → finalize) plus a labeled test set of tasks with known-correct outputs, and empirically measures: the per-step error rate, the actual end-to-end failure rate, and the marginal error-rate reduction per added verification checkpoint at each candidate insertion point. Instead of the generic 1-(1-ε)^N formula, the team sees their own chain's real compounding curve — which is often worse than naive independence predicts, because step errors correlate — and a ranked, cost-aware recommendation of where one added checkpoint buys the most error reduction per unit of added latency/cost.

Components: a pipeline-step instrumentation adapter (reads step-level outcomes from the team's own tracing system or a replayed log); an error-compounding model fit to observed per-step rates vs. observed end-to-end rate; a checkpoint-placement recommender weighing error-rate reduction against added latency/cost.

## Tangible Impact
**Population**: teams building production sequential multi-agent pipelines (research-synthesis-review chains, document-processing pipelines, coding-agent review chains) currently deciding "should we add another verification step" by gut feel or a generic blog formula — distinct from the parallel-ensemble/voting population already served by this repo's majority-vote-verifier idea, which addresses consensus-overturning, not sequential chain-length compounding.
**Mechanism**: replacing a hand-wavy "errors compound, add more review" instinct with a measured curve and a ranked, cost-aware recommendation stops teams both over-adding redundant checkpoints that add latency without reducing errors, and under-verifying chains where one well-placed checkpoint would have caught most of the compounding failure.
**Measure**: predicted vs. actual end-to-end success-rate improvement after adopting the top-ranked checkpoint recommendation, on held-out tasks; latency/cost added per percentage point of error-rate reduction, vs. a naive "checkpoint after every step" baseline; agreement between the fitted compounding model and the team's measured per-step correlation (showing whether the real chain compounds worse or better than naive independence).

## Why Now
Agent pipelines went from 2–3-step demos to production chains of 5+ specialized agents through 2026, and tracing platforms (LangSmith, Langfuse, OpenTelemetry GenAI conventions) now expose step-level success/failure data, making it newly feasible to fit an empirical compounding model to a real pipeline without hand-instrumenting from scratch.

## Skill Angle
For teams without a live tracing setup: paste a description of your pipeline's steps plus a sample of 10–20 recent failure/success logs, and the skill estimates each step's error contribution, flags which steps compound the most, and recommends where a checkpoint would help — a lightweight first pass before committing to the full connected benchmarking harness. The skill differs from the project in scope, not depth: it's a one-shot estimate from pasted data, not a live, continuously re-run benchmark against a tracing system.

## MVP Sketch
Pick one real or synthetic 4-step pipeline (extract → summarize → classify → finalize), run it against a 50–100 task labeled test set with per-step correctness checked, fit the empirical vs. theoretical compounding curve, and test whether a checkpoint at the harness's top-recommended position measurably beats one at a naive midpoint. Stack: Python, pandas for the error-rate fitting, a simple cost/latency estimator, CLI output. Single experiment: does the recommended checkpoint placement beat a naive placement on held-out tasks?

## Risks & Open Questions
- Per-step "correctness" is often ambiguous (a drafting step has no binary pass/fail) — the harness may need task-type-specific scoring rubrics rather than one generic definition.
- Practitioners in the evidence itself disagree whether mid-chain verification helps at all; the harness must be willing to report "no checkpoint helps here" rather than bias toward always recommending one.
- COCO's asynchronous-oversight approach may be a stronger foundation to build on than a from-scratch model — worth evaluating before ignoring the one piece of prior art.
- Correlated errors (steps failing together from a shared upstream cause, e.g. bad retrieval) break the independence assumption and could be misdiagnosed as pure chain-length compounding.
