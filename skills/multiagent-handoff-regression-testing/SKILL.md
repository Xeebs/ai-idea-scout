---
name: multiagent-handoff-regression-testing
description: Given a pasted "before" set and "after" set of example agent-to-agent handoff payloads from a multi-agent pipeline (LangGraph, CrewAI, AutoGen/AG2, or similar), infers the implicit schema each set satisfies and flags any field dropped, type changed, or truncation introduced in the "after" set that the "before" set never exhibited. Use as a pre-merge sanity check on a prompt or pipeline-code change, before any continuous capture/CI pipeline exists.
---

# Multi-Agent Handoff Regression Testing

## When to use this

A team is about to merge a prompt edit or pipeline-code change to one agent in a multi-agent pipeline (a supervisor/worker, task-delegation, or group-chat system), and wants to know whether that change silently broke the payload contract at a handoff boundary — a field quietly dropped, a type that flipped, a value that now gets truncated — before merging, without first wiring up a continuous trace-capture/CI harness. The user has (or can quickly pull) a handful of example payloads crossing that boundary from before the change and a handful from after. This is a one-shot, pre-merge diff of two payload samples, not a monitoring system and not a replacement for an ongoing golden-corpus regression suite — it answers "did this specific change break this specific boundary," once.

## Inputs

**Data source**: Manual — the user pastes two sets of example handoff payloads: a "before" set (captured from the current production/staging behavior at one specific agent-to-agent boundary) and an "after" set (captured from the same boundary after the pending change, from a staging run or local test). Payloads can be pasted as JSON objects, Python/JS dict literals, or structured log lines — whatever was copied out of a trace viewer, console, or test run. No API, no OTel export, no correlation IDs required.

Also helpful but optional:
- The name of the boundary (e.g., "classifier → router") and the framework (LangGraph, CrewAI, AutoGen/AG2, custom) — used only for labeling the report, not required to run the diff.
- What specifically changed (a prompt edit, a code change) — helps the report state a likely cause, but the diff itself only reasons from the pasted payloads, never from a guess about the change.

## Procedure

1. **Parse each set into individual payload examples.** Split the "before" paste and the "after" paste into discrete examples (one object/record per handoff instance). If a set has fewer than 2 examples, proceed but flag every finding in that set's section as **Low confidence (single-example sample)** — a single example cannot distinguish a real break from normal variance. If either set has fewer than 3 examples (even if ≥2), note the exact count of each set in the report header regardless — a finding confirmed across only 2 examples is still real evidence, but rests on less evidence than one confirmed across a larger set, and the reader should see both counts to judge that for themselves.
2. **Build a field inventory per set.** Walk each example's structure (including nested objects, using dot-path notation like `payload.customer.tier`) and record, per field path, across that set's examples: presence rate (appears in N of M examples), the type(s) observed (string, number, boolean, null, array, object), and for string/array fields, a size envelope (min/max length or item count).
3. **Check for truncation signatures** on string fields: a value that ends mid-word, ends in `...`/`…`, or whose max length across examples lands suspiciously exactly on a round number (200, 256, 500, 512, 1000, 2048, 4096) that other examples in the same set never approach — these are truncation evidence, not just "shorter."
4. **Diff the before-schema against the after-schema**, field by field, for every field path present in the before set:
   - **Dropped** — present in ≥50% of before examples, absent from *all* after examples.
   - **Type changed** — the dominant type in before differs from the dominant type in after, consistently (not a one-off).
   - **New truncation** — the after set shows a truncation signature (step 3) on a field that the before set never truncated.
   - **Presence drop** — present in all/most before examples, present in a clear minority of after examples (but not zero — that's "Dropped" instead).
5. **Separately list fields that are new in the after set but absent from before** — report these as **informational**, never as drift. A new field is additive and backward-compatible by default; only call it out as a concern if the user's framing (or an explicit before/after contract they pasted) makes clear a receiving agent would choke on an unexpected field.
6. **Apply the consistency guardrail before flagging anything as drift**: a finding only counts as drift if it holds across *all* (or, for sets of 4+, a clear majority of) the after examples — never promote a single after-example anomaly to a flagged regression. If the after set is too small or too inconsistent to tell real drift from noise, say so explicitly instead of guessing.
7. **Classify each confirmed finding's severity**:
   - **Breaking** — Dropped field, or a type change likely to throw/mis-parse downstream (e.g., string → null, object → string).
   - **Suspicious** — New truncation, or a presence-rate drop that isn't a full drop.
   - **Informational** — New field added, or a benign type widening (e.g., int → float).
8. **Write the report** per the Output format below, quoting the actual before/after values that support each finding.

## Output format

```
## Handoff Schema Diff: <boundary name or "unlabeled boundary">

**Before set**: <N> example(s) | **After set**: <M> example(s)
<if either N or M < 2: "Low confidence — sample too small to separate real drift from normal variance.">
<if either N or M is 2: one line noting that set's findings rest on a smaller sample than ideal (3+ recommended).>

### Breaking
- **<field.path>**: <what changed — e.g., "present in 3/3 before examples, absent from all 3 after examples">
  - Before: `<quoted example value>`
  - After: `<quoted example value or "absent">`

### Suspicious
- **<field.path>**: <what changed, e.g., new truncation signature>
  - Before: `<quoted example value>`
  - After: `<quoted example value>`

### Informational (new fields, non-breaking changes)
- **<field.path>**: <e.g., "new field, present in 2/3 after examples, absent from before set">

### No drift detected
<list field paths checked that showed no change, or "none — all checked fields showed at least one flagged change" if applicable>
```

If neither set is parseable into at least one structured example each:
```
## Insufficient Structure
<what's missing — e.g., "the 'after' paste has no field boundaries I can match to the 'before' set's structure; paste the raw payload objects, not a summary of them.">
```

## Guardrails

- Never invent a field, value, or example that wasn't in the pasted text — every "Before"/"After" quote in the report must be a verbatim value from the input.
- Never flag a change as drift based on a single after-example when the after set has 3+ examples — require the change to hold across all (small sets) or a clear majority (larger sets) of after examples first.
- Never report a newly-added field as "Breaking" or "Suspicious" by default — additions are informational unless the user's own framing establishes the receiving agent is strict/unknown-field-intolerant.
- Never claim this is a substitute for a continuous capture-and-replay CI pipeline — this is explicitly a one-shot pre-merge check on two pasted samples; say so if the user asks for ongoing coverage.
- Never guess at *why* a field was dropped or truncated (don't attribute it to a specific line of a prompt you haven't seen) — report what changed in the payloads, and only name the user-stated cause (if they provided one) as a hypothesis, not a diagnosis.
