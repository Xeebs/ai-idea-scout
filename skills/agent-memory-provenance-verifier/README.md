# Agent Memory Provenance Verifier

A paste-into-any-AI-chat-tool prompt for answering one narrow question: **did this AI agent's claimed memory actually happen, according to the evidence I have, or did it make it up?**

This exists because the obvious cheap fix — asking an LLM to judge whether a claimed memory "sounds" genuine — has already been shown to fail. In a recent test, three separate LLM judges performed no better than chance at telling a real agent memory from a fabricated one, and an independent grant-funded replication reported the same near-chance result for its own detection method. This prompt replaces that guess with a deterministic, evidence-cited check: it never asks "does this sound true," it only asks "does the specific text I was given actually say this."

## When to use this

Use it when you have one specific thing an AI agent claims to remember — "I remember you told me your deadline was Friday," "I recall checking your balance last week and it was $400," "the agent's memory log says the user approved this change on the 12th" — and you also have the execution trace, transcript, or tool-call log it's supposedly drawn from. You want to know: is this memory genuinely backed by that evidence, or not?

Do not use this for:
- **Reconstructing why an agent took some consequential action across a whole chain of memory writes and sessions** — that's a bigger, multi-hop incident investigation, a different exercise.
- **Live, automatic, cryptographically tamper-proof memory verification wired into a running system** — this prompt only reasons over text you paste into the chat right now; it cannot check hashes, verify a trace store hasn't been edited, or run continuously. If you need that, you need actual infrastructure built into your memory backend's write path, not a chat prompt.

## What to hand it

Before running the prompt, gather:

1. **The memory claim, verbatim.** The exact text of what the agent says it remembers. If it's a compound claim ("the user told me X and prefers Y"), that's fine — the prompt will split it into separate checkable pieces.
2. **The trace or transcript excerpt it's claimed to come from.** This can be a raw tool-call log, a chat transcript, retrieved document text, or any combination — whatever form you have it in. If you have a huge log and know roughly which session or time window is relevant, narrow it down first; a smaller, relevant excerpt gets a more reliable check than a huge dump.
3. *(Optional)* **A claimed timestamp or session reference** for when the memory supposedly originated — useful for checking whether your trace excerpt even covers the right window at all.

If you don't have any trace or transcript to check the claim against, this exercise can't run — there's nothing to verify it with. Get that first.

## The prompt

Paste this into any AI chat tool along with your memory claim and trace excerpt:

```
You are verifying whether a specific AI agent's claimed memory is genuinely
backed by evidence, or was fabricated/confabulated. I will give you: (1) the
exact text of the memory claim, and (2) a trace or transcript excerpt it is
claimed to derive from.

Do the following, in order:

1. Break the memory claim into separate atomic assertions if it contains more
   than one distinct fact. Verify each one independently — do not round a
   half-true compound claim up to fully supported.

2. For each assertion, search the trace/transcript I gave you for every
   segment that is topically relevant. Quote each candidate segment exactly
   as written, with its locator (line number, timestamp, message index, or
   tool-call ID) so I can find it myself.

3. For each assertion, decide:
   - SUPPORTED — a quoted segment's actual content directly entails the
     assertion (not just "is about the same topic" — it actually says this).
   - CONTRADICTED — a quoted segment directly conflicts with the assertion.
   - UNSUPPORTED — nothing in the trace addresses this assertion at all.
   - UNVERIFIABLE — the trace is ambiguous, truncated, or doesn't cover the
     relevant time window; say exactly why.

4. This is the most important check: if the claim (or whatever is being
   audited) points to a specific, real trace segment as its source, re-read
   that segment word-for-word and confirm it actually says what's claimed.
   A real segment being cited but misrepresented is CONTRADICTED or
   UNSUPPORTED — never count "a segment exists" alone as support.

5. Give one overall verdict for the whole claim:
   - SUPPORTED: every assertion is SUPPORTED.
   - PARTIALLY SUPPORTED: a mix of SUPPORTED and UNSUPPORTED/UNVERIFIABLE,
     none CONTRADICTED.
   - UNSUPPORTED: no assertion found any supporting evidence.
   - CONTRADICTED: at least one assertion directly conflicts with the trace
     (this overrides the others — one contradiction sinks the whole claim).

6. Note any caveats plainly — an incomplete or truncated trace should lower
   your confidence and you should say so, not quietly treat thin evidence as
   conclusive.

7. Before you finalize, double-check every quote you used is copy-paste
   verbatim from what I actually gave you. If you can't point to exactly
   where a quote came from, delete it and mark that assertion UNVERIFIABLE
   instead of asserting it.

Give me your answer in this format:

# Memory Provenance Verification — <one-line summary>

## Memory claim (verbatim)
<the claim>

## Assertions
| # | Assertion | Verdict | Cited trace segment (verbatim + locator) |
|---|---|---|---|

## Overall verdict: SUPPORTED | PARTIALLY SUPPORTED | UNSUPPORTED | CONTRADICTED

## Reasoning
<2-4 sentences, explicitly naming any "real citation, misrepresented content"
finding if one happened>

## Caveats
<trace gaps or ambiguity that would change the verdict with more evidence>

Here is the memory claim:
<paste it>

Here is the trace/transcript excerpt:
<paste it>
```

## What you get back

A table scoring each atomic piece of the memory claim against evidence you actually provided, an overall SUPPORTED / PARTIALLY SUPPORTED / UNSUPPORTED / CONTRADICTED verdict, and an explicit flag if the "evidence" turned out to be a real-but-misrepresented citation rather than genuinely missing. Every quote in the output should be traceable back to text you pasted — if it isn't, that's a sign the check wasn't done properly and you should push back and ask it to redo that step.

## What this doesn't do

It does not verify that the trace itself hasn't been tampered with or edited after the fact — it only checks logical consistency between the claim and whatever text you hand it. It does not run automatically or continuously; it's a one-time check of the specific material in front of it. And it does not reconstruct a longer causal chain across multiple memory writes to explain why an agent did something — it only answers whether one specific claimed memory is backed by the specific evidence you gave it.
