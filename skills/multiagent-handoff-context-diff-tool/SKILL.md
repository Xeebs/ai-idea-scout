---
name: multiagent-handoff-context-diff-tool
description: Diffs the exact payload one AI agent emitted against the exact payload the next agent actually received at a single suspect handoff, flagging silent truncation, dropped fields, or transformations distinct from declared summarization. Use when a multi-agent pipeline (LangGraph, CrewAI, AutoGen/AG2, or similar) produced a downstream quality problem and you suspect content was lost between two specific agents, but nothing crashed or errored.
---

# Boundary Diff: Handoff Content-Loss Report

## When to use this
A multi-agent pipeline has one agent (the sender) that produced an output, and a next agent (the receiver) that consumed it as input — and something downstream went wrong (a missing citation, a forgotten constraint, a hallucinated detail, a plan that ignores something earlier agents established) even though no error, exception, or crash occurred anywhere in the run. You have, or can obtain, the sender's actual output text/object and the receiver's actual input text/object for that one handoff, and you want to know precisely what changed between them before assuming the receiving agent's model just "made a mistake."

This is a one-shot forensic diff of a single suspect handoff, not a monitoring system. It does not watch a live pipeline, does not require instrumentation, and does not diagnose which handoff in a multi-hop chain is the culprit if you don't already have a specific one in mind — for that, use a handoff correlation/localization tool first, then bring the two payloads it points to here.

## Inputs
**Data source**: Manual — the user pastes the sender's full output text (or structured object, e.g. JSON) and the receiver's actual received input text/object, for one specific handoff. No API, framework export, or trace format is required; copy exactly what each side produced/consumed, even mid-conversation.

Required:
1. **Sender payload** — exactly what the upstream agent emitted (full text, or a JSON/dict block).
2. **Receiver payload** — exactly what the downstream agent's input actually contained (not what you assume it should have contained).

Strongly recommended, ask for if missing:
3. **Whether a deliberate transformation step runs between them** — summarization, reformatting, redaction, field-mapping — and what it's supposed to do. Without this, legitimate compression and silent data loss can look identical from the text alone.
4. The framework (LangGraph, CrewAI, AutoGen/AG2, custom) — only affects terminology in the report, not the diff logic.

If either payload is missing, do not guess or proceed with half a diff — ask for the missing side and stop.

## Procedure

1. **Normalize both payloads.** Determine if each is structured (valid JSON/dict — attempt a parse) or unstructured text. If one parses as JSON and the other doesn't, note the format mismatch itself as a finding (a structured→prose or prose→structured transformation is a loss-risk point by itself).

2. **Compute the size delta.** Character count and a rough token estimate (≈ characters ÷ 4, or word count × 1.3 — state which you used) for both payloads. Report the percentage change. This number alone does not determine severity — pair it with steps 3–5.

3. **Structured diff (if both parse as JSON/dict).** Walk every key present in the sender payload:
   - **Dropped field**: present in sender, absent in receiver, with no corresponding note (e.g. a `"[redacted]"` placeholder or a stated field-mapping rule) — flag as a candidate loss.
   - **Truncated field**: present in both, but the receiver's value is a prefix of the sender's value cut off mid-word, mid-sentence, or mid-array-element — flag as truncation, quote the exact cutoff point from both sides.
   - **Array shortened**: a list field has fewer elements in the receiver with no corresponding filter/dedup explanation — report which elements (by index and content) are missing.
   - **Renamed/restructured field**: same apparent content under a different key or shape — flag as transformation, not loss, unless content also changed.
   - **Added field**: present only in receiver — usually benign (injected metadata, routing info) but note it.

4. **Unstructured diff (if either payload is plain text).** Find the longest common prefix between sender and receiver text. At the point they diverge:
   - If the receiver's text simply stops (sender has more content after the divergence point, receiver has nothing) — this is **truncation**. Check whether the cutoff lands on a clean sentence/paragraph boundary (more consistent with deliberate shortening) or mid-word/mid-clause/mid-list-item (strong truncation signature). Also check whether the cutoff point lands near a suspicious round number (e.g. exactly 4000, 8000, 16000 characters or tokens) — a strong signal of a hard length limit, not intentional editing.
   - If the receiver's text continues but says different things — this is a **content change**, not truncation; quote both versions side by side.
   - If the receiver's text is shorter but covers the same topics in fewer words with closing structure (a conclusion, a final sentence) intact — this looks like **summarization**, not loss; flag as such unless it contradicts the sender's content.
   - **A declared transformation step never exempts this check.** Even when the user says a summarization/compression step is expected, enumerate every distinct fact, number, date, name, or constraint stated in the sender payload and confirm each one actually survives somewhere in the receiver payload before classifying the handoff as benign. If even one such fact is genuinely absent from the receiver despite the declared step, classify that specific missing fact as `FIELD_DROP` or `CONTENT_CHANGE` at `HIGH` severity regardless of the declaration — "a summarization step runs here" describes intent, not evidence that nothing of substance was actually lost.

5. **Classify every finding** into exactly one of:
   - `TRUNCATION` — abrupt cutoff, no closing structure, often at a round-number boundary.
   - `FIELD_DROP` — structured field vanished with no explanation.
   - `TRANSFORMATION` — reshaped but equivalent content (lower severity).
   - `SUMMARIZATION` — shorter but complete, closing structure intact, consistent with sender content.
   - `CONTENT_CHANGE` — receiver says something different, not just less.
   - `AMBIGUOUS` — can't confidently place in another bucket from the text alone; say so rather than forcing a classification.

6. **Assign severity.** If the user declared an expected transformation step (input #3) and a finding is consistent with what that step is supposed to do, mark it `EXPECTED — benign`. Otherwise:
   - `HIGH`: any `TRUNCATION` or `FIELD_DROP` finding, or combined loss exceeding roughly 15% of sender content with no `SUMMARIZATION`/`TRANSFORMATION` explanation.
   - `MEDIUM`: `TRANSFORMATION` findings that could plausibly alter downstream meaning (e.g. a constraint field renamed in a way that a simple key-lookup downstream wouldn't recognize).
   - `LOW`: everything else, including all `SUMMARIZATION` findings that preserve the sender's substance.

7. **Write the report** per the Output format below. If sender and receiver are identical, say so plainly in one line — do not manufacture findings to fill out the report.

## Output format

```
## Boundary Diff Report

**Sizes**: sender ~<N> chars / ~<M> tokens (est.) → receiver ~<N'> chars / ~<M'> tokens (est.) — <+/-X%>
**Format**: <both structured / both text / mismatch — note it>
**Declared transformation step**: <what the user said should happen, or "none declared">
**Overall verdict**: <NO LOSS DETECTED | EXPECTED TRANSFORMATION ONLY | SUSPECTED UNINTENTIONAL LOSS>

### Findings
1. [<TRUNCATION|FIELD_DROP|TRANSFORMATION|SUMMARIZATION|CONTENT_CHANGE|AMBIGUOUS>] (<HIGH|MEDIUM|LOW|EXPECTED>)
   - What: <one line, specific — field name, or the exact point text diverges>
   - Evidence: "<quoted sender excerpt>" → "<quoted receiver excerpt, or '(absent)')"
   - Why this classification: <one line>
(repeat per finding, ordered HIGH → LOW severity)

### Recommendation
<one or two sentences: what to check or fix if HIGH findings exist — e.g. "receiver's input appears capped near 8000 tokens; check the framework's context-window or message-truncation setting between these two nodes." If no HIGH/MEDIUM findings, say explicitly that this handoff is not the likely cause of the downstream problem.>
```

## Guardrails
- Never invent or infer content that isn't present in either pasted payload — every finding must quote text that actually appears in the sender or receiver payload given.
- Never default to "the model made a mistake" as an explanation when a content difference between the two payloads itself explains the downstream behavior — that is exactly the failure mode this skill exists to catch.
- Never classify a finding as benign/EXPECTED solely because the user didn't flag it as a problem — only mark EXPECTED when the user explicitly described a transformation step whose known behavior matches the finding.
- Never proceed with only one payload; ask for the missing side instead of speculating about what it "probably" contained.
- Never report a HIGH severity verdict based on size delta alone — pair every HIGH finding with a specific, quoted cutoff point or dropped field, not just an aggregate percentage.
- If the two payloads are in incompatible formats you cannot meaningfully compare (e.g. one is binary/opaque), say so and stop rather than forcing a text diff on unparseable input.
- This is a single-handoff tool: never try to reconstruct which of several handoffs in a longer chain is responsible — that requires a different diagnostic step before this one applies.
