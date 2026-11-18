---
name: agent-memory-anchoring-gate
description: Reviews an existing memory-augmented agent's retrieval/injection logic for anchoring risk (blind top-k injection with no task-boundary check), using real example turns, and sketches a task-signature gate fix. Use when a memory-enabled agent confidently answers the wrong thing after memory kicks in, or before shipping a new memory integration.
---

# Memory Anchoring-Risk Review

## When to use this
Reach for this when someone is building or maintaining a memory-augmented agent (Mem0, Letta, Zep, langmem, a custom vector-store retrieval layer, etc.) and either:
- Notices the agent confidently answers a *different* question than the one asked right after a memory got retrieved and injected — a silent failure, not a crash — and wants to know if memory is the cause.
- Wants a design check before enabling or shipping memory retrieval: "does this retrieval/injection logic have any protection against injecting the wrong memory?"

This is a one-shot design review, not an install — it does not wire in a running gate. It operationalizes a documented failure mode: MemTrapBench (arXiv 2608.20202) found five production-shaped memory frameworks (FullText, LightMem, MemOS, SimpleMem, EverMemOS) all scored worse on multi-turn business dialogue than a no-memory baseline, because retrieved "relevant" memories anchor the model to the wrong, previous task.

## Inputs
**Data source**: Manual — the user pastes or describes their current memory retrieval/injection logic (code, pseudocode, or prose) and 2-3 example turns where memory was retrieved.

Specifically needed:
1. The retrieval + injection logic: the code (or a clear prose description) showing how memories are fetched (top-k? similarity threshold? re-ranking?) and how they get inserted into the prompt sent to the model.
2. 2-3 example turns, each with: the current user message, which memory/memories were retrieved for it, and what the agent actually answered. Ideally at least one example where the answer seemed off-topic or stuck on a prior context.
3. Optional: which memory backend is in use (Mem0 / Letta / Zep / langmem / custom store) — helps make the fix sketch concrete.

If fewer than 2 example turns are provided, say so explicitly and label the analysis low-confidence rather than inventing additional examples.

## Procedure
1. **Find the injection point.** Read the retrieval logic and identify exactly where retrieved memories enter the prompt (system message, prepended context block, tool result, etc.). If the pasted logic doesn't show this clearly, say so rather than guessing.
2. **Classify the existing safeguard level**, based only on what's actually in the code/description:
   - `NONE` — blind top-k injection, no filtering beyond vector similarity to the query text itself.
   - `PARTIAL` — some mitigation exists (recency weighting, re-ranking, a relevance score cutoff) but nothing that compares the memory's *original task context* to the *current turn's task context*.
   - `SIGNATURE-AWARE` — there is already an explicit check comparing the current turn's task/intent to the memory's original task/intent before injecting.
3. **Per-turn anchoring analysis.** For each example turn provided:
   a. State the current turn's task/intent in one short phrase (e.g., "asking about a new billing date").
   b. State each retrieved memory's original task/intent in one short phrase (e.g., "memory was written during a subscription-cancellation conversation").
   c. Rate task overlap: `HIGH` / `MEDIUM` / `LOW`.
   d. If overlap is `LOW` or `MEDIUM`, check the agent's actual answer in that example: did it visibly carry over the wrong framing, a stale fact, or the wrong customer/account context? Mark `CONFIRMED ANCHORING` if yes, `POTENTIAL ANCHORING` if the mismatch exists but the answer wasn't visibly affected, or `NO ISSUE` if overlap was HIGH.
4. **Overall risk rating** for the stack as reviewed:
   - `HIGH` — safeguard level NONE and at least one CONFIRMED ANCHORING example.
   - `MEDIUM` — safeguard level NONE/PARTIAL with only POTENTIAL ANCHORING examples, or too few examples to confirm.
   - `LOW` — safeguard level SIGNATURE-AWARE, or all examples show HIGH overlap / NO ISSUE.
5. **Sketch a task-signature check**, concrete to the stack described: where in the existing code it would slot in (e.g., "wrap `memory.search()`'s return before it's appended to the prompt"), what a cheap check would compare (one-line task-signature of the current turn vs. the memory's original turn, via embedding cosine similarity or a short classifier prompt), and what happens below the threshold (withhold the memory, or down-weight/annotate it rather than deleting it).
6. **State caveats explicitly** — this review is qualitative judgment on the examples given, not a benchmark run; any accuracy-delta numbers belong to MemTrapBench's own evaluation of specific frameworks, not to this review.

## Output format
A single markdown report with these sections, in order:
1. **Injection Point Found** — where in the pasted/described logic memories enter the prompt (or "not visible in what was provided").
2. **Current Safeguard Level** — `NONE` / `PARTIAL` / `SIGNATURE-AWARE`, with the one-line reason.
3. **Per-Turn Anchoring Analysis** — a table: Turn | Current task | Retrieved memory's original task | Overlap | Verdict.
4. **Overall Risk Rating** — `HIGH` / `MEDIUM` / `LOW`, with the rule that produced it.
5. **Suggested Task-Signature Check** — a concrete, stack-specific sketch (prose + a short pseudocode/code snippet of where it slots in), not a generic essay on memory gating.
6. **Caveats** — confidence level given example count, and an explicit note that no accuracy numbers are being claimed.

## Guardrails
- Never fabricate what the user's retrieval code or logic does. If a step can't be answered from what was pasted, say exactly what's missing instead of guessing.
- Never state or imply an accuracy-delta percentage (e.g., "this closes 80% of the gap") — those figures belong to MemTrapBench's benchmark of specific named frameworks, not to this qualitative review.
- Never recommend disabling memory entirely as the fix — the fix is gating injection on task-signature match, not removing memory.
- Do not write and hand over full working gate code unless the user explicitly asks for it ("write the code" / "implement this"); the default deliverable is the review + design sketch above.
- If fewer than 2 example turns are supplied, say the analysis is low-confidence and ask for more before giving a firm Overall Risk Rating, rather than rating confidently off one data point.
