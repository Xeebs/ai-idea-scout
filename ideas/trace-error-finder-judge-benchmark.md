# Judge Arena: An Independent Benchmark for Specialist Trace-Error-Finders vs. Prompted LLM Judges

- **Status**: PROPOSED
- **Date**: 2026-11-14
- **Topic**: LLM evaluation & observability
- **Source**: research/2026-11-14-llm-evaluation-observability.md · P5
- **Maturity verdict**: PARTIAL — Laminar (`lmnr-ai/lmnr`, 3,488 GitHub stars, YC S24) shipped "flow-1," a real RL-trained model matching this pattern, with a company-reported 20–23x cost advantage over prompted judges, but this is a single-vendor launch from Oct 19 2026 with unverified installation/weights per third-party reporting and active comment-thread debate (59 points/35 comments on the HN launch) over whether the approach actually beats prompted judges — unevaluated independently.
- **Format**: BOTH — the reusable benchmark harness and leaderboard is persistent infrastructure; running the harness once against a team's own small labeled trace set is a separable one-off task.
- **Data Sources**: CONNECTED — pulls labeled failure-trace data from existing open benchmarks (`sierra-research/tau-bench` and `tau2-bench`, actively maintained public repos) and calls judge/model APIs directly (OpenAI/Anthropic/Gemini for prompted judges; Laminar's flow-1, if its API is publicly reachable, as the specialist-model entrant) — the benchmark datasets and major LLM APIs are mature today; whether flow-1's API is open enough to include as a tested entrant rather than relying solely on Laminar's own self-reported numbers is the main open integration question.

## The Gap
Hacker News, "Launch HN: Laminar (YC S24) – RL-trained model that finds errors in agent traces" (2026-10-19, 59 points, 35 comments), shows meaningful engagement and active debate for a fresh Show/Launch post — commenters are actively arguing whether a specialist trained model genuinely beats the dominant "ask GPT/Claude to grade this trace" approach, but the only numbers in circulation are Laminar's own self-reported 20–23x cost claim. No independent, reproducible head-to-head exists comparing a specialist error-finder against a range of prompted judges on a shared, public dataset.

## The Project
An open, reproducible benchmark harness that runs a fixed set of agent-execution traces with known, labeled errors (drawn from tau-bench/tau2-bench's sandboxed retail/airline failure cases, supplemented with synthetic seeded failures) through multiple approaches — several prompted LLM judges at different model tiers, and any specialist error-finder with a reachable API or open weights — and reports precision, recall, cost-per-trace, and latency for each, side by side, on infrastructure the vendor doesn't control. The point isn't to crown a winner once; it's to give buyers and builders a standing, re-runnable answer to "does a specialist model actually beat a prompted judge for my kind of trace, and by how much," replacing the current single self-reported number with an ongoing leaderboard.

Components: a labeled trace dataset loader (tau-bench/tau2-bench plus a synthetic seeded-failure generator); pluggable judge/model adapters (prompted-judge adapters for major LLM APIs, a specialist-model adapter for any reachable trained error-finder); a scoring harness computing precision/recall/cost/latency per entrant; a public leaderboard page re-runnable on demand as new entrants or model versions appear.

## Tangible Impact
**Population**: Engineering and eval-platform teams deciding whether to adopt a specialist trace-error-finder product (like Laminar's flow-1) over their current prompted-LLM-judge setup — a decision currently made on vendor marketing numbers alone, plus the broader observability-tool-buying audience the digest's dev.to market sweep shows is already actively comparing tools.
**Mechanism**: Today a team evaluating "should we switch from prompted judges to a specialist model" has only the vendor's own self-reported cost/accuracy claim to go on, with an active HN comment thread showing real uncertainty about whether it holds up. An independent, reproducible benchmark replaces that single data point with a transparent, re-runnable comparison the team can trust or even re-run on their own trace style.
**Measure**: (1) precision/recall gap between the specialist model and the best prompted judge on the shared labeled dataset, reported with confidence intervals, not a single point estimate; (2) cost-per-trace and latency for each entrant under identical conditions, directly testing the claimed 20–23x advantage; (3) adoption signal — number of external teams who re-run the harness against their own trace sample within the first few months of release.

## Why Now
Laminar's October 2026 launch put a concrete, debated, self-reported claim into public discussion this month, and tau-bench/tau2-bench are actively maintained (commits as recent as the digest's own research date) public datasets with exactly the kind of ground-truth-labeled tool-call failures this benchmark needs — meaning the data and the comparison subjects both already exist; only the neutral, reproducible harness connecting them is missing.

## Skill Angle
Trigger: a team has a handful of their own traces with known errors and wants a quick read on whether a specialist model or a prompted judge would catch more, without installing the full benchmark harness. Inputs: 5–10 traces with a human-labeled note on what actually went wrong in each. Output: a small comparison table scoring each configured judge/model on that specific sample, with a plain-language recommendation and an explicit caveat about sample size. This is the one-off, small-sample version; the project is the full public, reproducible leaderboard against the shared labeled dataset.

## MVP Sketch
Load tau-bench's existing labeled failure cases, wire two prompted-judge adapters (GPT-4-class and Claude-class) and one specialist baseline (an open fine-tuned small model trained on a subset of the same failure types, if Laminar's own API isn't reachable), run all three against the same 50-trace sample, and publish precision/recall/cost/latency as a static comparison table. Experiment: confirm the harness produces stable, repeatable scores across two separate runs before treating any single number as meaningful. 3 weeks, 1–2 people.

## Risks & Open Questions
- If Laminar doesn't expose a usable public API or weights, the specialist-model side of the comparison may have to rely on an independently trained stand-in rather than flow-1 itself, weakening the direct claim-verification value.
- tau-bench/tau2-bench's failure modes are narrow (sandboxed retail/airline domains) and may not generalize to the broader range of agent trace failures teams actually see in production.
- A benchmark score is only as credible as its labeling — constructing or extending a labeled failure set beyond tau-bench's existing cases is nontrivial scope creep risk.
- The underlying debate may not have a single universal answer (specialist models could win on cost but lose on recall for novel failure types) — the deliverable should be a transparent breakdown, not a single verdict, to avoid becoming just another self-reported-sounding claim.
