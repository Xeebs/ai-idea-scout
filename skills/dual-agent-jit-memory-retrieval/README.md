# Split Mind: Curator/Task Memory-Split Design Review

A portable prompt for reviewing a long-running single AI agent — a coding agent, a research agent, a support or ops agent — that keeps resending its full conversation and tool-call history into every prompt, and drafting a concrete design for splitting it into two roles: a **curator agent** that owns and indexes the full history, and a **task agent** that only ever receives a small, just-in-time retrieved slice each turn. This is a design review, not a build: it's for deciding whether the split is worth building before anyone spends engineering time on it.

Works in any AI chat tool. No special setup, no library install.

## When to use this

Use it when you're describing a long-running agent that either (a) is visibly getting worse over a long session — forgetting earlier decisions, repeating mistakes, misusing stale context — or (b) hasn't hit that wall yet but you want to know whether it will, and what a fix would actually look like, before you build it.

Don't use it for short sessions. If your agent's sessions typically run under ~20 turns or ~20K tokens of accumulated context, the split isn't worth its own overhead (it roughly doubles your per-turn LLM calls) — a good response will tell you that and stop rather than design something you don't need.

## What to give it

1. **Task domain and typical session length** — what the agent does, and how long its sessions typically run (turn count and/or token count by the end).
2. **What currently gets resent each turn** — full transcript, a running summary, a sliding window — and which framework it runs on (Claude Code, LangGraph, a custom loop, something else).
3. *(Optional, but makes the review sharper)* A sample transcript excerpt — even partial or redacted — showing where things seem to go wrong.

If you leave out (1) or (2), a good response asks for them rather than guessing at your session length or architecture.

## How to use it

Paste the prompt below into any AI chat tool, then provide the three inputs above.

---

### The prompt

> You are reviewing a long-running single-agent system that resends its full conversation/tool-call history into every prompt, and designing whether and how to split it into a curator agent (owns and indexes full history) and a task agent (receives only a bounded, just-in-time retrieved slice each turn).
>
> First, check the stated session length. If it's under roughly 20 turns or 20K accumulated tokens, respond only with a short "Not recommended yet" verdict explaining that the split's overhead (a second LLM call every turn, for curator retrieval) isn't worth it at this session length, and stop there.
>
> Otherwise, produce a design memo in exactly this structure:
>
> ```
> ## System Summary
> <domain, session length, current context-assembly strategy, framework>
>
> ## Degradation Evidence
> <cited turns/behavior from the transcript if one was given, or "based on reported description, no transcript provided">
>
> ## Curator Design
> - Indexes: <what it indexes — raw turns, tool-call results, decisions/commitments, artifacts>
> - Method: <embedding-based, keyword, symbol/AST-aware for code, or hybrid — justify the choice against the stated domain, don't default to embeddings without considering alternatives>
> - Update cadence: <per-turn or batched, justified against the stated session length>
>
> ## JIT Query Interface
> Query schema: <a concrete structured schema the task agent issues each turn>
> Example query (at some turn N, in this domain): <a worked example, not a placeholder>
> Example response: <a worked example of the bounded slice the curator returns>
>
> ## Token Budget
> Current baseline: ~<N> tokens by end of session, estimated from the stated session length
> Proposed JIT slice budget: ~<N> tokens/turn
> Estimated savings at the stated session length: <N>
>
> ## Integration Adapter
> <Claude Code session-transcript hook, LangGraph checkpointer wrapper, or a generic conversation-log wrapper — matched to the framework named in the input; ask rather than assume if no framework was named>
>
> ## Retrieval Risk Flags
> 1. <a concrete scenario specific to this domain where the curator could plausibly miss something the task agent needs> — mitigation: <concrete mitigation, e.g. a small "pinned" item set that bypasses retrieval scoring>
> 2. <a second concrete scenario> — mitigation: <concrete mitigation>
>
> ## Go/No-Go
> <a recommendation, explicitly naming the per-turn cost/latency tradeoff of running two agents instead of one, plus the single smallest experiment to run before building the live two-agent middleware — e.g. replaying the same task with retrieval simulated by hand vs. full history and comparing accuracy at the same turn count>
> ```
>
> Never invent transcript content, turn counts, or framework details that weren't given — ask for what's missing instead of guessing. Never claim this design has been validated against any published benchmark; it is an unvalidated design review, and the memo must end with a concrete validation experiment, not a claim of proven results.
>
> Here is the system to review:
> [paste: task domain + typical session length, current context-assembly strategy + framework, and optionally a sample transcript excerpt]

## Why this exists

Chroma's "context rot" finding — every tested model degrades past roughly 50K tokens even inside a 1M-token window — has turned "just use a bigger context window" into a non-fix, and a dual-agent curator/task split (a pattern a research lab called GAM shipped as a one-off academic artifact, not a reusable library) is the proposed answer. But going from "this pattern exists in one lab's repo" to "here's exactly how my coding/research/support agent should split" is its own design problem, and most teams facing real context rot don't have research-lab time to reverse-engineer it from a paper. This prompt does that one-shot design review — what to index, what query to issue, what to budget, what could go wrong — so a team can decide whether the live two-agent middleware is worth building before committing to it.

Full project context, evidence, and a sketch of the runtime (library) version of this idea: see [`ideas/dual-agent-jit-memory-retrieval.md`](../../ideas/dual-agent-jit-memory-retrieval.md) in the [ai-idea-scout](https://github.com/Xeebs/ai-idea-scout) repo.
