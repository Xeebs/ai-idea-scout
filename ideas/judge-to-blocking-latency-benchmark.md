# Fast Lane: A Judge-to-Blocking Latency Distillation Benchmark

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: AI safety & guardrails in production
- **Source**: research/2026-11-12-ai-safety-and-guardrails-in-production-pass2.md · P3
- **Maturity verdict**: PARTIAL — the detection-vs-enforcement distinction is already articulated by multiple vendors/practitioners (Weaviate's evals-vs-guardrails post, Arize's online-evals-for-monitoring guidance, MindStudio's judge-gates-execution pattern, a practitioner's "Crabtrap" judge-proxy demo with fail-closed timeout behavior), but these are vendor blog claims and single-author demos, not an independently evaluated, benchmarked solution for real-time, low-latency LLM-judge blocking at production scale.
- **Format**: BOTH

## The Gap
`awslabs/open-agentic-platform` issue #144 names the problem precisely: issue #104 shipped continuous LLM-as-judge evaluation over live traces, but "it detects, it cannot block — the judge runs after the response has already been returned, on a sampled fraction of traces. That is the right design for quality measurement and the wrong tool for enforcement." The issue was filed specifically to build the enforcement half that #104's evaluation work structurally cannot provide. No benchmarked reference exists for how much of a judge's catch-rate survives when it's forced into the synchronous critical path.

## The Project
A benchmark harness and reference middleware that measures the catch-rate-vs-latency trade-off when converting an async LLM-as-judge pattern into something that can actually block a response before it reaches the user: distilled small-model proxies, cached/precomputed partial judgments, fail-closed timeout wrappers (the "Crabtrap" pattern), and deterministic pre-filters feeding a judge only on ambiguous cases. The deliverable is a reusable comparison — same harmful-content test set, same judge, measured at full async latency vs. each distillation strategy — so a team can pick a synchronous-blocking configuration with a known, quantified catch-rate cost instead of guessing.

## Tangible Impact
**Population**: platform teams that have already shipped an LLM-as-judge continuous-evaluation pipeline (the `awslabs/open-agentic-platform` category, and any team following the same "evals for quality, not enforcement" architecture documented by Weaviate and Arize) and now need some of that judge's coverage to actually block, not just detect.
**Mechanism**: teams currently either accept that judge-based safety signal is detection-only (missing real-time harm) or hand-roll a single ad hoc distillation/timeout strategy (like the solo Crabtrap demo) with no comparison point. A benchmarked reference lets a team choose a synchronous-blocking configuration with a known catch-rate/latency trade-off instead of shipping an unvalidated guess.
**Measure**: catch-rate retained at a fixed p99 latency budget (e.g., 95% of full-judge catch-rate at under 300ms) versus the team's current fully-async baseline; number of previously-undetected-in-time harms that would have been blocked under the synchronous configuration on a replay of real incident traces; adoption-time cost (engineering hours) to wire a chosen strategy into an existing gateway versus building one from scratch.

## Why Now
The specific "evaluation can't enforce" framing surfaced as a live, acknowledged backlog item in the OAP thread this month, and distillation/caching techniques for LLM judges are now cheap and well-understood enough (small-model proxies, fail-closed timeouts) to benchmark systematically rather than treat as a one-off engineering trick.

## Skill Angle
Trigger: a team hands over their current judge prompt/rubric, a sample of labeled traces (harmful vs. benign), and their latency budget. The skill runs the comparison — full judge vs. 2-3 distillation strategies — on the provided sample and recommends a configuration with its measured trade-off, as a one-shot decision aid before committing to build the always-on middleware. The project is the production middleware implementing the chosen strategy in the request path; the skill is the one-time selection exercise that precedes it.

## MVP Sketch
Assemble a labeled test set of harmful/benign agent responses (reusing an open jailbreak/harm benchmark), run the full-judge baseline for catch-rate and latency, then implement and measure three distillation strategies: a distilled small classifier, a deterministic keyword/pattern pre-filter escalating only ambiguous cases to the judge, and a fail-closed timeout wrapper. Single experiment: plot catch-rate vs. p99 latency for each strategy against the full-judge baseline and publish the harness so others can re-run it against their own judge.

## Risks & Open Questions
- This may overlap conceptually with severity-tiered composition (see the Tier Gate idea) — the differentiator here is specifically converting one async judge into a synchronous primitive, not composing multiple already-synchronous checks; needs to stay narrow to avoid redundancy.
- A gateway vendor (litellm, Portkey) could ship a built-in "sync judge mode" quickly once the pattern is named, shrinking the addressable gap.
- Distillation quality is highly judge- and domain-specific; the benchmark's conclusions may not transfer cleanly across different harm categories.
- Evidence for demand is one GitHub thread plus general vendor commentary — real validation requires a team adopting a specific strategy in production, not just benchmark numbers.
