# Multi-Agent Handoff Regression Testing

A paste-in prompt for checking whether a prompt edit or code change to one agent in a multi-agent pipeline silently broke the payload contract it hands to the next agent — before you merge it, with no monitoring setup required.

## When to use this

You're about to merge a change (a prompt edit, a code change) to one agent in a multi-agent pipeline — a supervisor/worker setup, a task-delegation chain, a group-chat system, built on LangGraph, CrewAI, AutoGen/AG2, or something custom. You want to know whether that change quietly altered what the *next* agent receives at one specific handoff: a field that got dropped, a type that flipped, a value that now gets cut off. You have (or can quickly pull from a staging run, trace viewer, or test log) a handful of example payloads from that boundary before the change and a handful from after. This gives you a pre-merge sanity check on exactly that diff, in one shot.

This is not a monitoring system and it won't catch things it isn't shown — it only compares the two sets of examples you paste in.

## What to hand it

Paste two things:

1. **The "before" set** — a few example payloads (3+ is best, but even 1-2 works with a confidence caveat) crossing the handoff boundary you're worried about, captured from the current production or staging behavior. JSON, a Python/JS dict literal, or a structured log line — whatever you can copy straight out of a trace viewer, console, or test run.
2. **The "after" set** — the same number (ideally) of example payloads from the same boundary, captured after your pending change, from a staging run or local test.

Optional but useful: name the boundary (e.g., "classifier agent → router agent") and the framework, and say what you changed (a specific prompt edit, a specific code diff). These only help labeling and a hypothesis line in the report — the actual diff is based purely on the pasted payloads.

## The prompt

```
You are checking whether a pending change to a multi-agent pipeline broke the
payload contract at one handoff boundary. I will give you a "before" set and
an "after" set of example payloads from that boundary. Do the following:

1. Parse each set into individual examples. If either set has fewer than 2
   examples, proceed but mark every finding from that set "Low confidence —
   single-example sample." If either set has exactly 2 examples, note in the
   report header that those findings rest on a smaller-than-ideal sample
   (3+ is ideal) even though they're not flagged "Low confidence."

2. For each set, build a field inventory: walk every field (including nested
   fields, using dot-path notation like payload.customer.tier) and record,
   per field, how many examples it appears in, what type(s) it has
   (string/number/boolean/null/array/object), and for string/array fields,
   the size range (length or item count) across examples.

3. Check string fields for truncation signatures: a value ending mid-word,
   ending in "..."/"…", or whose max length lands suspiciously exactly on a
   round number (200, 256, 500, 512, 1000, 2048, 4096) that other examples
   in the same set never approach.

4. Diff the before-inventory against the after-inventory, field by field,
   for every field that appears in the before set:
   - Dropped: present in >=50% of before examples, absent from ALL after
     examples.
   - Type changed: the dominant type differs between before and after,
     consistently (not a one-off in a single example).
   - New truncation: a truncation signature appears in the after set on a
     field that never showed one in the before set.
   - Presence drop: present in all/most before examples, present in a clear
     minority (not zero) of after examples.

5. List fields that appear in the after set but not the before set
   separately, as INFORMATIONAL ONLY — never as drift. New fields are
   additive/backward-compatible by default.

6. Before flagging ANYTHING as drift: require the change to hold across all
   (for small sets) or a clear majority (for sets of 4+) of the after
   examples. Never promote a single anomalous example to a flagged
   regression — if you can't tell real drift from normal variance because
   the sample is too small or inconsistent, say so instead of guessing.

7. Classify each confirmed finding:
   - Breaking: dropped field, or a type change likely to break downstream
     parsing (string -> null, object -> string, etc.)
   - Suspicious: new truncation, or a presence drop that isn't a full drop.
   - Informational: new field, or a benign type widening (int -> float).

8. Output in this exact structure:

## Handoff Schema Diff: <boundary name, or "unlabeled boundary">

**Before set**: <N> example(s) | **After set**: <M> example(s)
<note here if either set is under 2 examples (Low confidence), or if either
set has exactly 2 examples (smaller-than-ideal sample)>

### Breaking
- **<field.path>**: <what changed, with counts>
  - Before: `<verbatim quoted value>`
  - After: `<verbatim quoted value or "absent">`

### Suspicious
- **<field.path>**: <what changed, with counts>
  - Before: `<verbatim quoted value>`
  - After: `<verbatim quoted value>`

### Informational (new fields, non-breaking changes)
- **<field.path>**: <description>

### No drift detected
<fields checked that showed no change, or state that every checked field
was flagged>

If neither pasted set can be parsed into at least one structured example,
output "## Insufficient Structure" and say exactly what's missing instead
of guessing at a schema.

RULES:
- Never invent a field, value, or example not present in what I pasted —
  every quoted "Before"/"After" value must be verbatim from the input.
- Never flag single-example anomalies as drift when 3+ after-examples exist.
- Never call a newly-added field "Breaking" or "Suspicious" by default.
- Never claim this replaces an ongoing CI capture-and-replay pipeline — this
  is a one-shot check on the two samples I gave you, nothing more.
- Never guess WHY a field changed (don't blame a specific prompt line you
  haven't seen) — report only what the payloads show. If I told you what I
  changed, you may name it as a hypothesis, not a diagnosis.

Here is the BEFORE set:
<paste before examples>

Here is the AFTER set:
<paste after examples>

Boundary name (optional): <e.g., "classifier agent -> router agent">
Framework (optional): <e.g., LangGraph>
What I changed (optional): <e.g., "shortened the summarization prompt">
```

## What you get back

A structured report with four sections: **Breaking** changes (dropped fields, harmful type changes — fix before merging), **Suspicious** changes (new truncation, partial presence drops — investigate), **Informational** notes (new fields, benign widening — no action needed), and **No drift detected** (what you can merge with confidence on). Every finding quotes the actual before/after values so you can verify it yourself rather than taking the verdict on faith.

## Limits

This only sees what you paste. If your "after" set doesn't actually exercise the code path your change touched, it won't catch anything wrong with it. For ongoing coverage across every merge, you need a real captured-traffic golden-corpus CI harness, not a one-shot paste — this skill is the quick sanity check you run before that exists, or before you've bothered wiring one up for this particular boundary.
