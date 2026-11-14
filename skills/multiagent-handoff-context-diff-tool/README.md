# Boundary Diff: Handoff Content-Loss Report

Paste this whole document into any AI chat tool (Claude, ChatGPT, Gemini, Copilot Chat, etc.) along with your two payloads, and it will diff them for you. No installation, API, or framework integration needed.

## What this is for

You're running a multi-agent AI pipeline — one agent's output becomes the next agent's input (a research agent handing off to a writer, a retrieval agent handing off to a planner, a triage agent routing to a specialist, built on LangGraph, CrewAI, AutoGen/AG2, or a custom orchestrator). Something downstream went wrong — a missing citation, a forgotten constraint, a hallucinated detail, a plan that contradicts something an earlier agent already established — but nothing crashed, errored, or triggered an alert. That's the hard case: the pipeline looks healthy because nothing broke in a liveness sense, the *content* just silently changed or shrank between two specific agents.

This prompt diffs exactly what one agent sent against exactly what the next agent received, and tells you precisely what was dropped, truncated, or transformed — instead of you eyeballing two blobs of text and guessing.

This is a one-shot diff of a single handoff you already suspect. It is not a monitoring tool and does not watch a live pipeline — you run it once per suspect handoff, by hand, whenever you need it. If you have a long multi-hop chain and don't yet know *which* handoff is the culprit, localize that first (by other means), then come back here with the two specific payloads at that handoff.

## What to hand over

You need two things, pasted in full:

1. **Sender payload** — exactly what the upstream agent emitted. Paste the raw text or JSON/object exactly as produced — don't clean it up or summarize it yourself first.
2. **Receiver payload** — exactly what the downstream agent's input actually contained when it ran. Not what you assume it should have contained — the actual input.

Optional but very helpful:

3. Whether a deliberate transformation step runs between the two agents — summarization, reformatting, field redaction/mapping — and what that step is supposed to do. Without this, a legitimate summarization and silent data loss can look identical on the page.
4. Which framework produced the run (LangGraph, CrewAI, AutoGen/AG2, custom, or none). This only changes the report's terminology, not the diff logic.

If you only have one side of the handoff, get the other side first — a half-diff isn't useful and the prompt should refuse to guess at the missing half.

## The procedure to follow

1. **Normalize both payloads.** Check if each one parses as valid JSON/structured data, or if it's plain text. If one side is structured and the other isn't, that format mismatch is itself worth flagging — a structured-to-prose (or prose-to-structured) conversion is a common place for content to quietly vanish.

2. **Compute the size delta.** Character count and a rough token estimate (characters ÷ 4, or words × 1.3 — pick one and say which) for both sides, and the percent change between them. This number alone never decides severity — it's just context for the findings below.

3. **If both sides are structured (JSON/dict), diff field by field:**
   - A field present in the sender and missing in the receiver, with nothing explaining why, is a candidate **dropped field**.
   - A field present in both, where the receiver's value is a prefix of the sender's cut off mid-word or mid-element, is **truncation** — quote the exact cutoff point on both sides.
   - A list/array with fewer elements in the receiver and no stated filtering reason — name which specific elements are missing.
   - A field that reappears under a different key or shape with the same content is a **transformation**, not a loss — lower severity, unless the content also changed.
   - A field that appears only in the receiver (injected metadata, routing info) is usually benign — just note it.

4. **If either side is plain text, find where they diverge.** Locate the longest stretch where sender and receiver text match, then look at what happens right after that point:
   - Receiver just stops while sender keeps going → **truncation**. Check whether the cutoff lands cleanly at a sentence/paragraph boundary (more consistent with intentional shortening) or mid-word/mid-clause (a strong truncation signature) — and whether it lands suspiciously close to a round number like exactly 4000, 8000, or 16000 characters/tokens, which usually means a hard length limit, not an edit.
   - Receiver keeps going but says something different → **content change** — quote both versions side by side, this is not simply "shorter."
   - Receiver is shorter but still covers the same ground with a proper ending (a closing sentence, a conclusion) → looks like **summarization**, not loss, unless it actually contradicts the sender.
   - **A declared transformation step never excuses skipping this check.** Even if you were told a summarization step is expected here, list out every distinct fact, number, date, name, or constraint in the sender payload and verify each one actually shows up somewhere in the receiver payload before calling the handoff benign. If even one concrete fact is genuinely missing despite the declared step, classify that specific gap as `FIELD_DROP` or `CONTENT_CHANGE` at `HIGH` severity anyway — being told a step is "supposed to" preserve the key facts is not the same as confirming it did.

5. **Classify every single finding** into exactly one bucket — don't leave anything unclassified:
   - `TRUNCATION` — abrupt cutoff, no closing structure, often at a round-number boundary.
   - `FIELD_DROP` — a structured field is simply gone with no explanation.
   - `TRANSFORMATION` — reshaped but equivalent content.
   - `SUMMARIZATION` — shorter but complete and faithful to the sender's content.
   - `CONTENT_CHANGE` — receiver says something different, not just less.
   - `AMBIGUOUS` — genuinely can't tell from the text; say so rather than forcing a guess.

6. **Assign severity to each finding:**
   - If the user told you a transformation step is expected and this finding matches what that step is supposed to do, mark it `EXPECTED — benign`.
   - Otherwise: any `TRUNCATION` or `FIELD_DROP` finding is `HIGH`. A `TRANSFORMATION` that could plausibly break a downstream lookup (e.g. a renamed field a later step keys off of) is `MEDIUM`. Everything else, including faithful `SUMMARIZATION`, is `LOW`.
   - Never call something `HIGH` just because the overall size dropped a lot — every `HIGH` finding needs a specific, quoted cutoff point or named dropped field behind it, not just a percentage.

7. **Write up the findings** in the exact report format below. If the two payloads are actually identical, say that in one line — don't manufacture findings to pad the report.

## Output format

Produce exactly this structure:

```
## Boundary Diff Report

**Sizes**: sender ~<N> chars / ~<M> tokens (est.) → receiver ~<N'> chars / ~<M'> tokens (est.) — <+/-X%>
**Format**: <both structured / both text / mismatch — note it>
**Declared transformation step**: <what was stated, or "none declared">
**Overall verdict**: <NO LOSS DETECTED | EXPECTED TRANSFORMATION ONLY | SUSPECTED UNINTENTIONAL LOSS>

### Findings
1. [TRUNCATION|FIELD_DROP|TRANSFORMATION|SUMMARIZATION|CONTENT_CHANGE|AMBIGUOUS] (HIGH|MEDIUM|LOW|EXPECTED)
   - What: <specific — field name, or exactly where the text diverges>
   - Evidence: "<quoted sender excerpt>" → "<quoted receiver excerpt, or '(absent)'>"
   - Why this classification: <one line>
(repeat, most severe first)

### Recommendation
<what to check or fix if HIGH/MEDIUM findings exist — e.g. "the receiver's input looks capped near 8000 tokens; check for a message-truncation or context-window setting between these two steps." If nothing HIGH/MEDIUM turns up, say plainly that this handoff is probably not the cause of the downstream problem — don't hedge into a non-answer.>
```

## Rules this must follow

- Never invent or infer content that isn't actually present in one of the two pasted payloads — every finding must quote real text from the sender or receiver.
- Never fall back on "the model just made a mistake" when a difference between the two payloads already explains the downstream behavior — finding that difference is the entire point.
- Only mark a finding `EXPECTED` when the user explicitly described a transformation step and the finding matches what that step is known to do — not just because nobody flagged it as a problem.
- Never proceed with only one payload. If the other side is missing, ask for it and stop.
- Never issue a `HIGH` verdict from an aggregate size-delta percentage alone — pair it with a specific, quoted cutoff point or a named dropped field.
- If the two payloads are in genuinely incompatible, unparseable formats (e.g. one is binary), say so and stop rather than forcing a diff that can't mean anything.
- This handles one handoff at a time. If you don't yet know which handoff in a longer chain is responsible, figure that out first — this tool doesn't localize across multiple hops.
