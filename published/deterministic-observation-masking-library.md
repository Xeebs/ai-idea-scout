# Mask Don't Summarize: A Deterministic, No-Extra-LLM-Call Context Eviction Library for Long-Horizon Agents

Every long-running coding or research agent eventually fills its context window, and the mainstream fix — fire off an LLM call to summarize the history and keep going — is itself becoming a known failure mode. OpenAI's Codex team has publicly named the problem: compaction lands mid-task, exactly when the agent has the least slack to notice and correct a mistake the summarization pass introduces. The fix several serious engineering teams have converged on independently is to stop summarizing and start masking — deterministically, with no model call at all. Nobody has packaged it yet.

## The Gap

Atlassian's Rovo Dev engineering blog and a DEV Community write-up citing OpenAI's Codex team both describe the same shift: structure-aware pruning and observation masking in place of a blocking LLM summarization call when the context window fills. The Codex team's own framing is the sharpest indictment of the status quo — automated compaction "gradually hurt performance over time" precisely because it fires at the worst possible moment in a task's lifecycle, when the agent has the least budget left to catch whatever the summarizer gets wrong. JetBrains Research backs the technique with numbers, not just engineering folklore: their arXiv paper (2508.21433, "The Complexity Trap") measures observation masking landing at roughly half the cost of LLM-summarization compaction at a matching-or-better task solve rate.

What's missing is the boring, valuable part: a library. Every team that has acted on this finding has built its own internal version from scratch. A June 2026 preprint proposes a more formal masking lifecycle but ships no code. The only public tooling that surfaced in a multi-channel search is a plain-FIFO Rust framework (`ambi`, which doesn't do structure-aware masking at all) and a 31-star Claude skill library — nowhere near the mainstream, framework-agnostic, swappable library this gap calls for.

## The Project

The core idea is to intercept tool-call outputs before they re-enter context on a later turn, and decide what to evict using fixed rules instead of a model's judgment. Three structural signals drive the rule engine: how many turns old an output is, what type of content it is (raw log and search-result dumps get masked more aggressively than small structured results), and a simple reference-tracking heuristic — was this output ever quoted or referenced again in a later turn? Masked content doesn't get paraphrased into a summary; it gets replaced with a fixed placeholder (type, size, "N turns old, masked") while the full original stays recoverable from the underlying log. The live context view just stops carrying it.

The centerpiece is what this approach refuses to do: spend a model call on the eviction decision. Eviction runs in milliseconds, on rules, which is the direct rebuttal to the Codex team's finding that model-driven compaction mid-task is itself a source of errors — you can't introduce a summarization mistake if there's no summarization step.

Planned components: a tool-output interception hook with framework adapters (Claude Agent SDK and LangGraph first), a configurable rule engine for age/type/reference-tracking thresholds, a masked-placeholder renderer, and an unmask/restore CLI for pulling a masked output back on demand.

## Tangible Impact

**Population**: Teams running long-horizon agentic coding or research sessions — multi-hour, many tool calls — who've hit either compaction-induced cost and latency spikes or compaction-induced task regressions. This is the same population named in both the Atlassian and OpenAI Codex sources, narrowed to the subset who haven't already built an internal masking fix and are still running default LLM-summarization compaction.

**Mechanism**: Right now, every context-window-full event triggers either an expensive, blocking, occasionally-inaccurate LLM summarization pass mid-task, or — for the handful of teams who've already built their own fix — a bespoke internal script with no shared maintenance burden spread across the ecosystem. A drop-in deterministic masking library removes the LLM call from the eviction path entirely, turning a cost-and-latency-and-risk event into a near-free, rule-based one. That's JetBrains' measured ~2x cost reduction at matched solve rate, but available as adoptable infrastructure instead of something every team re-derives on its own.

**Measure**: (1) Token cost and wall-clock latency per long-horizon task session, masking versus standard LLM-summarization compaction, at matched task-success rate — replicating JetBrains' own benchmark design on a held-out task suite. (2) Rate of "agent needed masked content back" recovery events via the unmask CLI, as a proxy for over-aggressive masking. (3) Count of compaction-triggered mid-task errors, before versus after, following the exact failure mode the Codex team named.

## Why Now

The research case and two independent production engineering teams converging on the same technique inside the last 30 days establishes real, validated demand and feasibility at the same time. What's missing — a mainstream, swappable, framework-agnostic library — is a pure execution gap, not a research gap: nothing here waits on a new model capability, just on someone building it.

## Risks

Worth being upfront about the two biggest reasons this might not pan out as described. A near-identical idea already in this project's backlog ("Prune Once," a model-judged per-output pruning approach) targets the same population; this project only earns its place by staying clearly differentiated as the deterministic, no-extra-LLM-call alternative, and the two ought to eventually be benchmarked against each other, not just against baseline compaction. More fundamentally, rule-based eviction has no semantic understanding of what actually matters — a reference-tracking heuristic can miss content that only becomes relevant many turns later with no prior reference, which risks reproducing compaction's own "silently lost it" failure mode through a different mechanism. There's also the standing platform risk common to this whole space: a mainstream framework could ship an equivalent built-in masking feature quickly once the pattern is named widely enough.

---

Surfaced from `research/2026-11-20-context-engineering-memory.md`, pattern `P2`.
