# Repair Match: Classifying Multi-Agent Failures Against a Verified-Repair Dataset

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Multi-agent architectures
- **Source**: research/2026-11-12-multi-agent-architectures.md · P2
- **Maturity verdict**: PARTIAL — ARIA (arXiv 2610.20780, github.com/LabRAI/ARIA) built a 3,953-pair verified-repair dataset from 24,000+ trajectories, but the repo has 1 star and was last pushed 2026-10-12 — a brand-new, unadopted research snapshot. Related datasets (AgentFail — 307 logs, StateMAS, SymFail) confirm an active research niche, but no tool built on top of any of them exists yet.
- **Format**: BOTH

## The Gap
An October 2026 preprint, "ARIA," introduced a data-driven framework and dataset pairing failed multi-agent runs with verified repairs, explicitly positioned as an alternative to relying on ad hoc post-mortems per incident. It is reported purely as a fresh research artifact — no GitHub project or commercial offering built on the dataset appeared in either engine run, and the repo itself shows no adoption (1 star, one month old). The raw material for a repair-matching tool now exists for the first time, but nobody has built the living lookup service on top of it.

## The Project
A classifier + lookup tool: ingest a multi-agent run's failure trace, extract a structured failure signature using taxonomies from ARIA (and the related AgentFail/StateMAS/SymFail corpora), and retrieve the nearest matching verified-repair pattern(s) with an explanation of why that repair applied in the matched case. Unlike ARIA's frozen snapshot, the centerpiece is an ongoing feedback loop: teams that apply a suggested repair record whether it worked, growing a living, de-duplicated, community-corrected superset of the one-time dataset — the maintenance layer that turns a research artifact into a usable tool.

Components: trace ingestion adapters (OpenAI/Anthropic SDK call logs, LangGraph/CrewAI state dumps); failure-signature extractor; nearest-neighbor retrieval over the combined, deduped corpus; repair-suggestion ranking; a feedback loop that records repair outcomes and corrects/grows the corpus.

## Tangible Impact
**Population**: Engineering teams operating multi-agent systems in production who currently debug new failures via ad hoc, from-scratch post-mortems — the pattern ARIA was explicitly built to replace — realistically the same large population of LangGraph/CrewAI production users whose inter-agent-misalignment failures already show up at scale in existing failure taxonomies (32.3% of 1,642 annotated traces per the Ema/Redis/orq.ai data cited elsewhere in this pipeline's research).
**Mechanism**: Today a multi-agent failure means manually tracing logs, hypothesizing a cause, and trying a fix with no record of whether a similar failure elsewhere was already solved. Matching against a maintained, growing verified-repair corpus turns "diagnose from scratch" into "check if this failure shape has a validated fix first," cutting time-to-repair for the likely large share of failures that are variations on previously-seen patterns.
**Measure**: (1) Share of a pilot team's new failures that match an existing repair above a confidence threshold, vs. requiring fresh diagnosis. (2) Median time-to-repair for matched vs. unmatched failures. (3) Repair-suggestion acceptance/success rate reported back by users, tracked as a corpus-quality signal over time.

## Why Now
ARIA just produced the first large-scale verified-repair dataset for exactly this problem within the last 30 days, but as a one-star, one-time research snapshot with zero lookup tooling built on it. The raw material exists for the first time; building the living, feedback-corrected tool on top of it is newly possible and currently unclaimed.

## Skill Angle
Given a single failed trace pasted in (tool calls, messages, error state), apply the extraction-and-matching pipeline against the static bundled corpus and return the best-matching repair suggestions with confidence scores — a one-shot diagnostic useful without the always-on, continuously-updated service running. The project differs by integrating into a team's observability pipeline continuously and growing the corpus via the feedback loop; the skill is a single-trace, on-demand lookup.

## MVP Sketch
Load ARIA's public dataset, build an embedding-based nearest-neighbor matcher over failure descriptions, wrap it in a CLI that takes a trace file and returns the top-3 matching repairs with confidence scores. Experiment: run it against 10-15 real multi-agent failures from a pilot team or public GitHub issue reports; if matches are mostly irrelevant, the taxonomy granularity is wrong and the project should narrow scope or stop. 2-3 weeks, 1-2 people.

## Risks & Open Questions
- ARIA's dataset may skew toward failure types from its specific collection methodology/frameworks and not generalize to a given team's stack.
- A 1-star, month-old repo could be absorbed into a vendor's observability product before this gets traction.
- Matching failure traces across different frameworks' log formats requires significant per-framework adapter work.
- Without real user feedback loops closing quickly, the corpus risks staying frozen and stale, just like ARIA itself.
