---
name: voice-bot-dialect-telephony-stress-test-bench
description: Turns a team's pasted voice-bot failure logs/support tickets into a prioritized dialect x telephony-condition test matrix — which combinations to stress-test first. Use before committing to a full dialect/line-condition regression bench, when a team has real complaints but no systematic way to decide what to test first.
---

# Dialect x Telephony-Condition Failure Triage

## When to use this
A team running a voice bot/IVR into dialect-diverse, telephony-degraded markets has a pile of real failure signal — support tickets, call-QA notes, escalation logs — and wants to know *which dialect x line-condition combinations to test first*, before building or running a full stress-test bench (see the sibling project idea for the full bench). This is the triage step that comes before that commitment, not a replacement for it.

## Inputs
**Data source**: Manual — the user pastes raw text: support tickets, call-QA notes, escalation summaries, or transcript excerpts. This skill never reaches into a telephony or ASR vendor API directly; pulling degraded call audio automatically via a connector (e.g. Twilio Voice Insights) is the full bench's roadmap-only CONNECTED upgrade, not something this skill does.

The user provides:
1. A batch of failure entries (one ticket/note/excerpt per entry — paste as many as they have; works with as few as 5, more reliable above ~15).
2. *(Optional)* Which dialects/regions and which line-condition categories (e.g. "mobile static", "dropped call", "codec garble") are already known to matter for their deployment, to normalize labeling — if omitted, labels are derived from whatever vocabulary the entries themselves use.

## Procedure
1. **Read every entry.** For each one, extract two independent signals, each only if *explicitly stated or directly quoted* in that entry's text:
   - **Dialect/accent/region tag** — only from an explicit statement in the text itself (e.g. "caller spoke Tamil-accented English", "regional Hindi dialect", "customer said bot couldn't follow their Telugu-English code-switching"). **Never infer dialect/accent/ethnicity from a caller's name, phone number, or location field alone** — that is fabricated demographic signal, not evidence.
   - **Telephony-condition tag** — only from an explicit description of line/audio quality (e.g. "static on the line", "call kept dropping", "sounded garbled/robotic", "mobile network, kept cutting out", "customer had to repeat themselves 4 times due to noise"). A bare "bot didn't understand me" with no audio-quality description is NOT a condition tag.
2. **Classify each entry** into exactly one of three buckets:
   - **Full signal** — both a dialect tag and a condition tag present → goes into the matrix.
   - **Partial signal** — only one of the two present → goes into a separate partial-signal list (by axis), never forced into a matrix cell.
   - **Untaggable** — neither present, or the complaint is unrelated (billing, routing, unrelated bug) → counted but excluded, listed as examples only if asked.
3. **Build the matrix**: rows = distinct dialect tags found, columns = distinct condition tags found, cell value = count of full-signal entries landing in that cell. Add a severity flag to a cell if any of its entries used escalation language (repeat complaint, "demanded a human", explicit safety/compliance mention, churn threat).
4. **Rank cells**: primary sort by count descending, secondary tiebreak by presence of a severity flag (flagged cells rank above unflagged cells of equal count).
5. **State confidence honestly**: if total full-signal entries < 15, say explicitly that ranking is directional only, not statistically robust, and that single-digit cell counts can flip order with a handful more tickets.
6. **Recommend next step**: name the top 3–5 cells as what to run first in the full stress-test bench (or manual spot-check if no bench exists yet), each with a one-line rationale quoting or closely paraphrasing the evidence.

## Output format
```
## Priority Test Matrix (full-signal entries only)

| Dialect \ Condition | <condition A> | <condition B> | ... |
|---|---|---|---|
| <dialect 1>          | <count>[⚠ if flagged] | <count> | ... |
| <dialect 2>          | ...            | ...     | ... |

## Top combinations to test first
1. <Dialect> x <Condition> — <count> entries[, flagged] — "<short quoted/paraphrased evidence>"
2. ...
(up to 5)

## Partial-signal entries (one axis only — not placed in matrix)
- Dialect known, condition unknown: <n> entries (e.g. <dialect list>)
- Condition known, dialect unknown: <n> entries (e.g. <condition list>)

## Untaggable: <n> entries excluded (no explicit dialect or condition signal, or unrelated)

## Confidence note
<explicit statement of sample size and whether ranking should be treated as directional>
```

## Guardrails
- Never infer a dialect, accent, or ethnicity from a name, phone number, or location alone — only from an explicit statement in the entry's own text. This is the single most important rule; violating it fabricates demographic signal the user never gave.
- Never invent a condition tag from a vague "didn't work" complaint — require an actual audio/line-quality description.
- Never force a partial-signal entry into a matrix cell by guessing its missing axis.
- Never present a small-N ranking as statistically confident — always state the sample size and its limits.
- Never claim this triage output is a substitute for actually running the stress-test bench — it only tells a team where to point the bench first.
