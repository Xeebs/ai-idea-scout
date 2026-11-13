# Quiet Break: Post-Deploy Behavioral Regression Detection Without an LLM Judge

- **Status**: EXPLORING
- **Date**: 2026-11-11
- **Topic**: LLM evaluation & observability
- **Source**: research/2026-11-11-llm-evaluation-observability.md · P1
- **Maturity verdict**: PARTIAL — WebSearch found Apgar (github.com/oimo-ai/apgar, 9★/2 forks, single maintainer) plus `agentevals` (OTel-trace scoring, no re-run, no judge) and a June 2026 arXiv paper on a deterministic eval harness; no second *maintained, adopted* production-trace-baseline-diff tool found — the gap is real but a build here is differentiated, not greenfield.
- **Format**: PROJECT — continuous trace ingestion and release-to-release baseline comparison is a running service, not a one-shot prompt task.

## The Gap
Show HN "Apgar – Catch agent regressions without an LLM judge" (2026-10-29, 3 points; repo 9★/2 forks/29 commits) diffs production-trace metrics — tool-error rate, retry/loop counts, call volume, answer length, cost, latency — between an agent's current release and its prior baseline, flagging "quiet" degradation that never crashes and never trips a standard error alert. It's a single early-stage, single-maintainer project; no second maintained implementation of this specific no-judge, trace-baseline-diff approach turned up in the same search window.

## The Project
A baseline-diff service that ingests OTel/Langfuse spans tagged by release version, snapshots the five-to-six core metrics per release window, and runs a statistical drift check (e.g., CUSUM or distribution-shift test) against the trailing baseline — entirely deterministic, with zero LLM calls in the detection path itself. On breach, it posts a concrete "release N regressed metric X by Y%" report to the team's alert channel instead of waiting for a crash or a support ticket.

Components: OTel-compatible span ingester; per-release metric snapshotter; drift-detection engine (CUSUM/z-score); alert/report formatter; a small dashboard comparing release N vs N-1 metric distributions.

## Tangible Impact
**Population**: Engineering teams operating production LLM agents that ship prompt or model changes at least weekly without a dedicated eval engineer — per LangChain's State of AI Agents survey (1,300+ professionals, Dec 2024), ~51% of respondent companies already run agents in production; the target is the subset (realistically thousands of teams, mostly under ~50 engineers) past that adoption curve but before building their own eval tooling.
**Mechanism**: Today a quiet regression — a tool starting to retry more, answers getting longer, cost creeping up — has no alert path and surfaces only when a user complains or a support ticket lands days later. A deploy-triggered baseline diff turns that into a same-day, named-metric report, giving on-call a concrete signal instead of a vibe, and giving the team a rollback trigger before user impact compounds.
**Measure**: (1) median time from deploy to regression detection drops from days (user complaint) to under 2 hours on pilot teams; (2) share of "silent" regressions (no crash, no error-rate spike) caught before user impact rises from near-zero to a majority; (3) number of rollback decisions per month backed by a concrete metric-diff report rather than anecdote, tracked per pilot team.

## Why Now
OTel's GenAI semantic conventions and tracing backends (Langfuse, etc.) matured enough in 2026 that per-span metrics like tool-error rate and retry counts are available without bespoke instrumentation. Apgar's emergence on 2026-10-29 shows the pattern is tractable with today's tooling — nothing here waits on a future model capability.

## MVP Sketch
Ingest OTel spans tagged by release/version into ClickHouse or Postgres; compute five metrics per release window; run a CUSUM/z-score drift check against the trailing baseline; post a Slack alert on breach. Experiment: replay one pilot team's real prompt-change history and confirm the system flags at least one known-bad past deploy without false-alarming on a known-good one. 3 weeks, 1–2 people.

## Risks & Open Questions
- Apgar or `agentevals` could mature quickly and absorb this niche — a direct early-stage competitor already exists.
- Picking thresholds that avoid alert fatigue on noisy, low-volume services is unsolved and could kill adoption on its own.
- Teams without release-tagged traces can't use this without an instrumentation pass first.
- Conceptually adjacent to golden-eval-set drift detection (a separate pattern in the same digest): this idea is judge-free and deploy-triggered, that one is traffic-vs-eval-set and periodic — worth confirming in practice they stay genuinely distinct products.
