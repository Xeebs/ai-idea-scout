# Memory Anchoring-Risk Review (portable prompt)

Paste the block below into any AI chat tool (ChatGPT, Claude, Gemini, etc.) along with your memory retrieval code and example turns. No installation, repo, or prior context needed — this is fully self-contained.

## When to use this

Use this when you're building or maintaining an agent that has a memory layer (Mem0, Letta, Zep, langmem, or a custom vector-store retrieval setup) and either:

- You've noticed the agent confidently answers a *different* question than the one actually asked, right after a memory got pulled in — it doesn't crash, it just quietly answers the wrong thing.
- You want a design check before turning memory retrieval on in production: "does this logic have any protection against injecting a memory that will mislead the model?"

This checks for a documented failure mode called **anchoring**: a 2026 benchmark (MemTrapBench, arXiv 2608.20202) found five production-shaped memory frameworks all performed *worse* than having no memory at all on multi-turn business dialogue, because a retrieved "relevant" memory from a past, now-irrelevant task anchors the model's framing of the new turn. Nothing crashes — the agent just answers the wrong question confidently.

This is a one-shot design review. It does not write or install a running gate for you (unless you explicitly ask it to write the code at the end).

## What to hand over

1. **Your retrieval + injection logic** — paste the actual code if you have it, or describe it in prose: how do memories get fetched (top-k? similarity cutoff? re-ranking?), and exactly how do they get inserted into the prompt sent to the model?
2. **2-3 example turns**, each with: the user's message, which memory (or memories) got retrieved for it, and what the agent actually answered. Try to include at least one example where the answer felt off-topic or stuck on an old context.
3. *(Optional)* Which memory backend you're using — Mem0, Letta, Zep, langmem, or something custom. Not required, but it makes the suggested fix more concrete.

If you only have one example turn, say so — the review will flag itself as low-confidence rather than pretend otherwise.

## The prompt to paste

```
Act as a memory-anchoring-risk reviewer for my agent's memory retrieval/injection logic. Here is my retrieval/injection logic (code or description):

[PASTE YOUR CODE OR DESCRIPTION HERE]

Here are 2-3 example turns where memory was retrieved:

Turn 1:
- User message: [...]
- Memory retrieved: [...]
- Agent's answer: [...]

Turn 2:
- User message: [...]
- Memory retrieved: [...]
- Agent's answer: [...]

(Turn 3 if available)

My memory backend (optional): [Mem0 / Letta / Zep / langmem / custom / unsure]

Please do the following, in order, and give me back a single report with these exact sections:

1. Injection Point Found — identify exactly where in my logic retrieved memories get inserted into the prompt sent to the model. If you can't tell from what I gave you, say so explicitly rather than guessing.

2. Current Safeguard Level — classify as NONE (blind top-k injection, no check beyond similarity to the query text), PARTIAL (some mitigation like recency weighting or re-ranking, but nothing that compares the memory's original task context to the current turn's task context), or SIGNATURE-AWARE (there's already an explicit task/intent match check before injecting). State the one-line reason for your classification.

3. Per-Turn Anchoring Analysis — for each example turn I gave you, in a table: state the current turn's task/intent in one short phrase, the retrieved memory's original task/intent in one short phrase, rate the overlap between them as HIGH/MEDIUM/LOW, and give a verdict of CONFIRMED ANCHORING (overlap was low/medium AND my actual answer visibly carried over the wrong framing, a stale fact, or wrong context), POTENTIAL ANCHORING (overlap was low/medium but the answer wasn't visibly affected), or NO ISSUE (overlap was high).

4. Overall Risk Rating — HIGH if safeguard level is NONE and at least one turn is CONFIRMED ANCHORING; MEDIUM if safeguard level is NONE/PARTIAL with only POTENTIAL ANCHORING or too few examples to confirm; LOW if safeguard level is SIGNATURE-AWARE or every turn is NO ISSUE. State which rule produced the rating.

5. Suggested Task-Signature Check — sketch a concrete, minimal check for my specific stack: where in my existing code/flow it would slot in, what it would compare (a cheap one-line task-signature of the current turn vs. the memory's original turn — via embedding cosine similarity or a short classifier prompt), and what happens when similarity is below threshold (withhold or down-weight the memory, don't delete it from storage).

6. Caveats — note my analysis's confidence level given how many example turns I gave you, and explicitly state that you are not claiming any accuracy-percentage improvement — that any such numbers belong to MemTrapBench's own benchmark of named frameworks, not to this review.

Rules for your response:
- Never invent details about my code/logic beyond what I gave you — flag gaps instead of guessing.
- Never state an accuracy-delta percentage as if it applies to my specific stack.
- Don't tell me to just disable memory — the fix is gating injection, not removing memory.
- Don't write full working gate code unless I explicitly ask you to in a follow-up — give me the design sketch first.
- If I gave you fewer than 2 example turns, tell me the analysis is low-confidence and ask for more before giving a firm Overall Risk Rating.
```

## What you get back

A single markdown report in the six sections above: where memories get injected in your logic, how protected that injection point currently is, a per-turn table showing exactly which retrieved memories risked anchoring the model and why, an overall HIGH/MEDIUM/LOW risk rating with the rule behind it, a design sketch for the minimal fix tailored to your actual stack, and caveats about confidence and what isn't being claimed.

## What this is not

This is not a benchmark run and not an installed gate — it's a design review based on the examples you provide. If you want the always-on version (middleware that actually intercepts every retrieval call before it gets to the model), that's a separate build, not something a chat prompt can wire into your running system.
