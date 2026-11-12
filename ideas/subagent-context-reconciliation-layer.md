# Reconcile: A Consistency-Reconciliation Layer for Isolated Sub-Agent Context

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Context engineering & memory
- **Source**: research/2026-11-12-context-engineering-memory-ii.md · P2
- **Maturity verdict**: OPEN — GitHub search for "agent context reconciliation" / "subagent merge conflict resolution" returned zero results. Isolation itself is well-covered (Claude Code sub-agents, Cursor 2.0's 8-parallel-agent git-worktree mode), but no named, packaged reconciliation layer exists — only scattered, unimplemented practitioner suggestions in blog comments and a March 2026 aggregator noting "empirical evidence is thin" on whether isolation's benefits clear its coordination overhead.
- **Format**: BOTH — the conflict-detection middleware is runtime infrastructure; reviewing a specific pipeline's isolation plan and drafting a reconciliation policy is a one-shot judgment task.
- **Data Sources**: CONNECTED — reads sub-agent invocation transcripts and return messages directly from the host orchestration framework at runtime (e.g. Claude Agent SDK's Task-tool sub-agent results, LangGraph node outputs, a custom fan-out loop's collected summaries). No third-party API is involved; a small per-framework adapter needs to be built, since no cross-framework connector exists today.

## The Gap
Engineering blogs (tianpan.co's "Four Strategies for Engineering Agent Context"; levelup.gitconnected's "why more context makes AI coding agents worse") describe splitting messy exploratory work — search, backtracking, failed attempts — into isolated sub-agent windows that each return only a short digested answer, keeping the lead agent's own context clean. One of the sourced guides states flatly that "isolation solves the context length problem but creates a consistency problem," with no named production-ready resolution; a DEV.to commenter floats a "lightweight conflict-detection step before merging" and another suggests verification sub-agents propose patches rather than edit directly — both unbuilt suggestions, not shipped tools.

## The Project
A middleware layer that sits between a lead agent and its sub-agents: every sub-agent's digested return is compared against the others (and against the lead's own running assumptions) for contradiction before it's folded into the lead's context. Detection runs on the returned summaries, not full transcripts, so it stays cheap — an embedding-similarity pass flags candidate conflicts, and an LLM-judge pass confirms genuine contradictions versus surface-level wording differences. On a confirmed conflict, the layer applies a declared policy: block-and-ask-lead, spin up a tie-breaking verification sub-agent, or merge-with-flag so the human/lead sees the disagreement instead of silently inheriting one sub-agent's answer.

Components: a summary-comparison engine (embedding pre-filter + LLM-judge confirm); a pluggable resolution-policy interface (block/verify/flag-and-merge); adapters for Claude Agent SDK's Task tool and LangGraph fan-out nodes; a conflict-injection test harness that seeds deliberately contradictory sub-agent outputs and scores detection precision/recall.

## Tangible Impact
**Population**: Teams building multi-sub-agent isolation pipelines — directly on Claude Code's Task-tool sub-agents, Cursor 2.0's 8-parallel-agent git-worktree mode, or custom LangGraph/CrewAI fan-out — a pattern that has spread fast since practitioner blogs began citing (unverified) a 90.2% lead-agent-performance improvement attributed to Anthropic's own multi-agent isolation design; this is now a default architecture choice, not a niche one, for any team running parallel research/coding sub-agents.
**Mechanism**: Today, when two isolated sub-agents explore independently and return conflicting digested conclusions, the lead agent either silently picks one (often the most recent or most confidently-worded) or merges both into a contradictory plan — a failure that's invisible until it surfaces downstream as a wrong action. A reconciliation layer turns that silent failure into a detected, policy-governed event before the lead agent acts on it.
**Measure**: (1) Precision/recall of conflict detection on a labeled benchmark of deliberately contradictory sub-agent summary pairs. (2) Lead-agent task success/regression rate with the layer enabled versus a measured baseline on the same multi-sub-agent pipeline. (3) Added latency/cost overhead from the comparison pass, targeted at a small fraction of total sub-agent invocation cost.

## Why Now
Sub-agent isolation has gone from a research idea to a default production pattern in under a year (Claude Code's Task tool, Cursor 2.0's parallel mode), and the consistency problem it introduces is now being named explicitly in practitioner writing with zero shipped tooling to reach for — the gap is wide open at exactly the moment the pattern it targets is becoming standard.

## Skill Angle
Given a description of a multi-sub-agent pipeline (what each sub-agent explores, what it returns to the lead) plus two or more actual sub-agent outputs pasted in, flag whether they conflict, classify the conflict type (factual contradiction, scope mismatch, stale assumption), and recommend which resolution policy fits this pipeline shape. Useful standalone as a one-off audit before a team invests in the full middleware.

## MVP Sketch
A Python library wrapping Claude Agent SDK's Task-tool invocation: collects N sub-agent returns for one lead-agent step, runs the embedding-prefilter + LLM-judge-confirm comparison, and applies a configurable policy. Experiment: build a 15–20 scenario conflict-injection suite (half genuinely contradictory, half superficially different but consistent) and measure detection precision/recall; if precision is too low to be useful (false-conflict rate swamps real catches), the detection approach needs rework before the policy layer matters. 2–3 weeks for 1–2 people.

## Risks & Open Questions
- The March 2026 aggregator's note that "empirical evidence is thin" on whether isolation even nets a benefit over coordination overhead could mean reconciliation is solving a problem whose root cause (isolation itself) should just be abandoned for many workloads.
- LLM-judge-based conflict confirmation is itself an imperfect, non-deterministic step — false positives could make the layer more annoying than the silent-merge status quo it replaces.
- Anthropic, Cursor, or LangChain could ship a native reconciliation step inside their own sub-agent primitives, absorbing this before an independent library gains traction.
- Detection on short digested summaries (by design, ~150 tokens) may miss conflicts that only become visible in the sub-agents' full reasoning traces, which the isolation pattern deliberately discards.
