# Blast Radius: Structure-Aware Code Context Retrieval for Agents

- **Status**: PROPOSED
- **Date**: 2026-11-11
- **Topic**: Context engineering & memory
- **Source**: research/2026-11-11-context-engineering-and-memory.md · P8
- **Maturity verdict**: PARTIAL — active research and early tooling exists (CodeCompass, DyRetriever, GraphCodeAgent, commercial Codegraph), but Thoughtworks' Technology Radar (Nov 2026) places "graph-grounded codebase reasoning" in "Trial" status and notes research showing agents sometimes perform *worse* with graph context than plain grep/find. Real, contested gap, no dominant proven approach.
- **Format**: PROJECT (was BOTH — downgraded 2026-11-12: skill-synthesizer NOVELTY_FAIL, blast-radius-PR-review skill angle is saturated by `tirth8205/code-review-graph`, 32.7k stars, actively maintained, plus `sverklo/sverklo` and `dancingteeth/unified-code-review`)

## The Gap
r/ContextEngineering's "Have we become too dependent on text search for understanding code?" (2026-10-14) names a real limitation: a simple change can ripple through inherited methods, call chains, and cross-file dependencies that text search and embedding similarity don't surface, because they match tokens, not relationships. The gap-analyst confirmed active academic and early commercial attempts, but also found evidence the obvious fix (hand agents a dependency graph) doesn't reliably beat plain text search in practice — the problem is open precisely because the naive solution underperforms.

## The Project
A structure-aware code context tool that builds a lightweight call-graph/inheritance index per repo (not a full static-analysis engine) and, critically, decides *when* graph context helps versus when plain text search is sufficient — the decision layer is the centerpiece, not the graph itself, directly answering the Thoughtworks-flagged failure mode where graph context sometimes makes agents worse. For a given change or query, it returns either a ranked blast-radius summary (what calls/inherits/depends on the touched code) or defers to text search, based on a learned or rule-based judgment about which retrieval mode fits the query shape.

Components: incremental call-graph/inheritance indexer (language-server-protocol-based, not a bespoke parser); a routing layer that picks graph-retrieval vs text-search per query; an MCP server exposing both; an eval harness comparing agent task outcomes (correct blast-radius identification, regressions introduced) across graph-only, text-only, and routed modes.

## Tangible Impact
**Population**: Engineering teams running AI coding agents against large, highly interconnected codebases — object-oriented or microservice systems with deep inheritance/call chains (the exact shape named in the source thread) — where a single agent-authored change risks breaking code the agent never saw because it wasn't textually nearby.
**Mechanism**: Today, an agent using only text search or embeddings can miss a dependent caller or overridden method several hops away, shipping a change that looks locally correct but breaks something structurally connected; a retrieval layer that surfaces the actual blast radius when it matters (and stays out of the way when it doesn't) reduces agent-introduced regressions without the known cost of graph context sometimes degrading performance.
**Measure**: (1) Regression rate in agent-authored PRs (bugs traced to a missed dependency) before versus after adoption on a pilot codebase. (2) Agent task success rate on a blast-radius identification eval (does it find all affected call sites for a given change) compared against plain-text-search and graph-only baselines. (3) Reviewer time spent catching dependency-related issues in agent PRs, self-reported before/after.

## Why Now
Thoughtworks' November 2026 Radar placing this in "Trial" status, alongside multiple concurrent arXiv/alphaxiv attempts in the last 30 days (CodeCompass, DyRetriever, GraphCodeAgent), signals the field has converged on the problem being real but the solution being unsettled — a routing layer that actually measures when graph context helps is the differentiated angle none of the cited attempts take.

## Skill Angle
Given a proposed code change (diff or description) and access to the codebase, trace the likely blast radius — callers, overriders, and cross-file dependents of the touched code — and produce a short risk summary flagging what else might need review. This is useful as a standalone PR-review step even without the persistent graph index, by having the agent reason directly over the codebase's existing structure (imports, class hierarchy) for the specific change at hand.

## MVP Sketch
An LSP-based indexer for one language (e.g., TypeScript or Python) producing a call/inheritance graph, a simple router (query mentions "what calls X" / "what inherits from Y" → graph; everything else → text search), and an eval of 15–20 real changes from an open-source repo, scoring blast-radius completeness against a human-verified ground truth. Experiment: if routed mode beats both graph-only and text-only baselines on the eval, the routing hypothesis holds — if text-only wins outright, that itself replicates and extends the Thoughtworks finding, which is a valid, useful negative result. 3–4 weeks for 1–2 people.

## Risks & Open Questions
- The Thoughtworks-cited research that graph context sometimes hurts is the strongest reason this might not be solvable by adding more graph data — the routing decision itself may be the hard, unsolved part, not a detail.
- Maintaining an incrementally-updated graph index across active development adds infrastructure cost that may not pay off on smaller or less interconnected codebases.
- Commercial Codegraph (34-tool MCP server) or a well-resourced IDE vendor could ship an equivalent routing layer before independent validation lands.
- LSP-based indexing varies in quality and completeness across languages, so results may not generalize beyond the first target language.
