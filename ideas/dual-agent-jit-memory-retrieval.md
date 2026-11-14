# Split Mind: A Portable Dual-Agent Just-In-Time Memory Architecture Against Context Rot

- **Status**: PROPOSED
- **Date**: 2026-11-13
- **Topic**: Context engineering & memory
- **Source**: research/2026-11-13-context-engineering-memory.md · P7
- **Maturity verdict**: PARTIAL — GAM has a public implementation (`github.com/VectorSpaceLab/general-agentic-memory`, linked from arXiv 2511.18423, with MemoryAgent/ResearchAgent code and LoCoMo/RULER eval scripts), but it's a single academic lab's release with no independent reproduction or fork-level adoption; `gh search repos` found only forks/derivatives (`proxi666/general-agentic-memory-langgraph`, a vibe-coded fusion repo), narrow and unproven outside its own benchmarks.
- **Format**: BOTH — the two-agent runtime (curator agent, task agent, JIT retrieval store) is persistent infrastructure; reviewing an existing single-agent system's context and designing the curator/task split for it is a separable one-shot task. See Skill Angle.
- **Data Sources**: CONNECTED — hooks into the host agent framework's own session/conversation history store (e.g. Claude Code's session transcript, LangGraph's checkpointer, or a generic conversation log wrapper around any agent loop) so the curator agent can index full history while the task agent only ever receives the JIT-retrieved slice. These hook points are mature today in Claude Code and LangGraph; no new external connector needs to be built, only the integration adapter.

## The Gap
VentureBeat's coverage of GAM (dual-agent memory architecture) frames the pattern as a direct response to Chroma's finding that "every tested model degraded as input length grew even at 50K tokens within a 1M-token window" — i.e., accumulating full message history into context is itself the failure mode, not just a cost problem. GAM's own repo exists and runs its own benchmarks, but no independent team has adopted, forked meaningfully, or ported the dual-agent JIT-retrieval pattern into a production agent framework — it remains one lab's artifact rather than a reusable library.

## The Project
A portable library implementing the dual-agent pattern as a drop-in wrapper around an existing single-agent setup: a curator agent that owns the full conversation/tool-call history and is responsible for indexing it incrementally, and a task agent that never sees that full history — each turn, it receives only the slice the curator retrieves as relevant to the current step. The centerpiece is the retrieval interface between the two agents: a structured "what does the task agent need right now" query the curator answers from its index, rather than the task agent ever accumulating raw history itself. This is deliberately framework-agnostic, unlike GAM's own fixed research scaffold.

Components: a curator-agent harness (owns history, builds/maintains an index — embedding-based, keyword, or hybrid); a JIT query interface (task agent asks a structured need, curator returns a bounded slice); adapters for Claude Code sessions, LangGraph state, and a generic conversation-log wrapper; a context-rot eval harness measuring task accuracy as a function of session length/step count, reproducing Chroma's degradation curve with and without the split.

## Tangible Impact
**Population**: Solo developers and small teams building long-horizon autonomous coding or research agents that run for hours and currently accumulate full conversation history into every prompt — the cohort whose agents hit the exact 50K-token-and-up degradation Chroma documented, but who lack the research-lab engineering capacity to reproduce GAM's own scaffold from its arXiv paper and code.
**Mechanism**: Today, every additional turn a long-running single agent takes adds to the full history it re-sends on the next turn, so accuracy degrades monotonically with session length regardless of how good the model is at that context length — splitting curation from execution means the task agent's actual working context size stays roughly constant per turn, independent of how long the session has run, converting a worsening accuracy curve into a flat one.
**Measure**: (1) Task accuracy as a function of session length/step count, before (single agent, full history) vs. after (dual-agent, JIT slice), reproducing a Chroma-style degradation benchmark. (2) Tokens actually sent to the task agent per turn under JIT retrieval versus the full-history baseline. (3) Task completion rate on multi-hour sessions designed to force 20+ turns.

## Why Now
Chroma's degradation finding (every tested model worsens past 50K tokens even within a 1M-token window) reframes "just use a bigger context window" as a non-fix, and GAM's public code + eval scripts give a concrete reference implementation to port from rather than reproducing the architecture from a paper description alone — the pattern is validated but still locked inside one lab's artifact.

## Skill Angle
Given a description of an existing single-agent system's task and its typical session length (or a sample transcript), review it and draft a curator/task split design: what the curator should index and how, what structured query the task agent should issue each turn, and a rough JIT-slice token budget. A one-shot design task useful before anyone commits to building the live two-agent middleware.

## MVP Sketch
A Python wrapper around Claude Code's session transcript: a curator process that incrementally embeds each turn and tool-call result into a local vector index, and a task-agent prompt template that queries the curator for "what's relevant to this step" instead of receiving the raw transcript. Experiment: run the same 20+-turn coding task with full-history (baseline) vs. dual-agent JIT retrieval, and measure accuracy and token cost at each turn to see whether the degradation curve flattens. 3-4 weeks for 1-2 people.

## Risks & Open Questions
- The curator's retrieval quality is itself a new failure surface — a bad JIT query or a miss in the curator's index could starve the task agent of something it actually needed, trading context rot for context loss.
- GAM's own lab, or a major framework vendor (Anthropic, LangChain), could ship a maintained open-source port first and absorb this idea's differentiation.
- Running two agents instead of one roughly doubles the per-turn LLM call count (curator indexing/retrieval plus task execution), so the architecture needs to prove its accuracy win is worth the added latency/cost, not just assume it.
- No independent reproduction of GAM's own benchmark numbers exists yet — the MVP's first job is confirming the underlying claim (dual-agent JIT retrieval actually beats full-history accumulation) holds outside GAM's own eval scripts, not just building the wrapper.
