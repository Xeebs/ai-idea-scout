---
name: dual-agent-jit-memory-retrieval
description: Reviews a long-running single-agent system's current context-assembly pattern and drafts a concrete curator/task-agent memory split (what gets indexed, the structured JIT query interface, token budget, integration adapter, and retrieval-risk mitigations) before anyone commits to building the live two-agent middleware. Use when someone describes an autonomous agent that resends full conversation/tool-call history every turn and is seeing accuracy degrade over long sessions.
---

# Split Mind: Curator/Task Memory-Split Design Review

## When to use this
Someone describes a long-running single-agent system — a coding agent, a research agent, a support or ops agent — that keeps accumulating full conversation and tool-call history into every prompt, and either (a) reports it getting worse, forgetting earlier decisions, or repeating mistakes as the session goes on, or (b) is proactively worried about hitting that wall before it happens, and wants a design for splitting the system into a curator agent (owns and indexes full history) and a task agent (receives only a bounded, just-in-time retrieved slice each turn) — without yet committing engineering time to build it.

Do not use this for sessions that are already short (under roughly 20 turns or 20K tokens of accumulated context) — say so and recommend against the split; it adds a second LLM call per turn and is not worth it below the regime where context rot actually bites.

## Inputs
**Data source**: Manual — this skill operates on what the user pastes or types: (1) a description of the system's task domain and typical session length (turn count and/or token count at session end), (2) a description of what currently gets resent to the model each turn (full transcript, a summary, a sliding window, etc.) and which framework it runs on (e.g. Claude Code, LangGraph, a custom loop), and (3) optionally, a sample transcript excerpt (can be partial or redacted) showing where things seem to go wrong. The parent project this skill is scoped from is Connected in its live form — it hooks into the host framework's own session/checkpointer store so a running curator agent can index history automatically — but this is a one-shot design-review skill, not that live middleware, so it only needs what's pasted above; it does not read any connector itself.

If (1) and (2) are missing, ask for them before producing a design — scoring a split on an unstated session length or an unstated current-context strategy is a guess, not a review. (3) is optional; its absence is not a blocker, but note that risk-flagging in step 7 below is weaker without it.

## Procedure
1. **Characterize the current system.** State the task domain, typical session length (turns and/or tokens), and exactly what gets resent each turn under the current design (full history / summary / sliding window). If the stated session length is under ~20 turns or ~20K accumulated tokens, stop here and recommend against the split (see guardrails) rather than proceeding to design one.
2. **Locate the degradation evidence.** If a transcript excerpt was given, point to the specific turn(s) or tool-call(s) where the agent appears to lose track of an earlier decision, repeat itself, or misuse stale context. If no transcript was given, state plainly that this step is based on the user's own description rather than observed evidence.
3. **Design the curator agent.** Specify what it indexes (raw turns, tool-call results, decisions/commitments made, artifacts produced) and recommend an indexing method fitted to the domain — e.g. embedding-based semantic search for open-ended research/support text, symbol/AST-aware or file-path-keyed retrieval for a coding agent, hybrid for anything mixing both. State the update cadence (every turn vs. batched) and justify it against the stated session length.
4. **Design the JIT query interface.** Write the actual structured query schema the task agent issues each turn (e.g. `{current_step, entities_in_play, lookback_hint}`) and what the curator returns (a bounded, ranked slice — not a token count the task agent controls). Give one concrete worked example using the user's own domain, not a generic placeholder.
5. **Set a token budget.** Estimate the current full-history baseline token cost at the stated session length, and propose a per-turn JIT-slice budget (a concrete number, e.g. "cap retrieved slice at 4K tokens regardless of session length"), with the resulting estimated savings at the user's stated session length.
6. **Recommend an integration adapter.** Match to the framework named in the inputs: Claude Code session transcript hook, LangGraph checkpointer wrapper, or a generic conversation-log wrapper if neither is named. If the framework isn't stated, ask rather than assuming one.
7. **Flag retrieval-risk points.** Name at least two concrete scenarios specific to this domain where the curator's retrieval could plausibly miss something the task agent needs (e.g. a decision made in turn 3 that matters again at turn 40, a constraint stated once and never repeated), and propose a mitigation for each (e.g. a small "pinned" set of items that bypass retrieval scoring entirely and are always included).
8. **Give a go/no-go recommendation** with the single smallest validation experiment to run before building the live middleware (e.g. "replay the same task with the curator's retrieval simulated by hand/truncation vs. full history, and compare accuracy at the same turn count") — not a recommendation to just go build it.

## Output format
A single structured design memo, in this order:
```
## System Summary
<domain, session length, current context-assembly strategy, framework>

## Degradation Evidence
<cited turns/behavior from transcript, or "based on reported description, no transcript provided">

## Curator Design
- Indexes: <what>
- Method: <embedding / keyword / symbol-based / hybrid, with justification>
- Update cadence: <per-turn / batched, with justification>

## JIT Query Interface
Query schema: <concrete schema>
Example query (turn N of this domain): <worked example>
Example response: <worked example, bounded>

## Token Budget
Current baseline: ~<N> tokens by end of session
Proposed JIT slice budget: ~<N> tokens/turn
Estimated savings at stated session length: <N>

## Integration Adapter
<Claude Code / LangGraph / generic wrapper, and what hook point it uses>

## Retrieval Risk Flags
1. <scenario> — mitigation: <concrete mitigation>
2. <scenario> — mitigation: <concrete mitigation>

## Go/No-Go
<recommendation + the one validation experiment to run first>
```
If the session length is below the threshold in step 1, output only a short "Not recommended yet" verdict with the reason, skipping the remaining sections.

## Guardrails
- Never recommend the split for a session under ~20 turns / ~20K tokens — say so and stop; this skill exists to stop people over-engineering a problem they don't have yet, not to produce a design regardless of need.
- Never invent transcript content, turn counts, or framework details that weren't given — ask for what's missing instead of filling gaps with plausible-sounding guesses.
- Never claim this design has been validated against any published benchmark (including Chroma's or GAM's own) — it is an unvalidated design review; always end with a concrete validation experiment, not a claim of proven results.
- Always name the per-turn cost/latency tradeoff explicitly (two LLM calls instead of one) in the Go/No-Go section — never present the split as free.
- Always fit the indexing method recommendation to the stated domain; never default to "use embeddings" without considering whether the domain (e.g. code, structured data) has a better-fitting retrieval method.
