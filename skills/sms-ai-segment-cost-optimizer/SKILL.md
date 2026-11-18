---
name: sms-ai-segment-cost-optimizer
description: Audits a batch of already-sent AI-chatbot SMS responses and reports what fraction crossed a billed segment boundary unnecessarily (161 chars costing 2 segments instead of 1), with concrete before/after rewrites that preserve safety-critical content, plus a cost-savings estimate. Use before committing engineering time to build or adopt segment-compression middleware for an SMS-based AI chatbot.
---

# SMS-AI Segment Cost Auditor

## When to use this
A team running (or planning to run) an AI chatbot over SMS — for users without mobile internet access, often in low-income or low-bandwidth markets — wants to know how much billed SMS cost their AI responses are wasting before they invest engineering time building or buying segment-compression middleware. The trigger moment is specifically: "we have a batch of real AI-generated SMS responses already sent (or ready to send) and want a number, not a guess, on how many are crossing a segment boundary they didn't need to." This is a one-time audit/decision aid, not the compression middleware itself — it produces the business case for building that middleware, it doesn't replace it.

Do NOT use this for: live, per-message compression in production (that's a runtime middleware service sitting between the LLM call and the SMS gateway send — out of scope for a prompt-driven skill); auditing SMS marketing campaigns with no AI-generated content (several generic "SMS text optimizer" skills already cover plain marketing-copy shortening — this skill is specifically about chatbot response pipelines and segment-boundary math, not generic tone/brevity editing); or any message containing safety-critical content the skill should rewrite without a human reviewing the result first.

## Inputs
**Data source**: CONNECTED (preferred) — mirrors the parent idea's classification: Twilio's Message resource API (`GET /2010-04-01/Accounts/{SID}/Messages.json`) and Africa's Talking's delivery-reports/SMS API are both mature, already-live connectors in exactly the SMS-AI deployments this skill targets, and either can be queried directly (e.g. via `curl` in Claude Code) for a date-ranged batch of sent message bodies and their segment counts. **MANUAL fallback** (what to paste when API credentials aren't available to whoever is running the audit): a plain-text log, one message per line, each line containing at minimum the literal AI-generated response text that was actually sent; optionally a timestamp and the gateway's own reported segment/unit count per message if known.

Required:
1. The batch of messages (via API fetch or pasted log) — minimum ~10 messages for the stats to mean anything, realistically 50-500 from a day/week of chatbot traffic.
2. The target encoding assumption, if known: GSM-7 (default, for English/most Latin-script languages) or UCS-2 (required for many non-Latin scripts and any message containing emoji — ask if unsure, since this changes the per-segment character budget from 160/153 to 70/67).

Optional, improves the output:
3. A per-segment billing rate (e.g. "$0.012/segment") and active-user count, to produce a dollar cost-savings estimate rather than just a segment-count estimate.
4. A list of content categories that must never be trimmed (e.g. "dosage instructions", "appointment dates", "account balances") — if not given, the skill defaults to flagging any number, date, unit (mg, ml, %), or warning-like phrase ("do not", "must", "immediately", "within X days") as safety-critical and excludes it from rewrite.

## Procedure
1. **Ingest the batch.** If connected to Twilio/Africa's Talking, fetch the date-ranged message log via its API and extract each message body plus any gateway-reported segment count. Otherwise, parse the pasted log into one record per message.
2. **Determine encoding per message**, not per batch. Default GSM-7. Flag UCS-2 if the message contains any character outside the GSM-7 default+extension tables (any emoji, most non-Latin scripts, several accented characters depending on language). Record the per-segment character budget: single-segment is 160 (GSM-7) or 70 (UCS-2); any message needing more than one segment drops to a per-segment budget of 153 (GSM-7) or 67 (UCS-2) because of the concatenation header.
3. **Compute actual segments** for each message: `segments = 1` if length ≤ single-segment budget, else `ceil(length / multi-segment budget)`.
4. **Classify each message**:
   - **Clean** — already at the minimum possible segment count for its content (no waste).
   - **Boundary waste** — crosses into one more segment than needed by a small margin: flag when trimming ≤20 characters (or ≤15% of the message length, whichever is larger) would pull the message back under the previous segment boundary.
   - **Not evaluated** — message too short to ever cross a boundary (clean by default, still counted in totals).
5. **For every "boundary waste" message**, scan it for safety-critical content (numbers, dates, units, dosages, warning phrases, or anything the user listed in their "never trim" categories). If found, do not draft a rewrite — mark it "cannot safely compress" and state exactly what content blocks the trim. Otherwise, draft a concrete rewrite: cut filler words, redundant phrasing, or restate more tersely, with the explicit goal of landing at or under the previous segment's character budget while preserving every fact in the original.
6. **Aggregate statistics**: total messages audited, count/percent "boundary waste" vs "clean" vs "cannot safely compress", average billed segments per message before vs. the audited-optimal after, total segments saved across the batch.
7. **If a per-segment rate and user count were given**, extrapolate: (segments saved per message × message volume implied by the batch period) × rate = estimated cost saved over that period, scaled to a monthly figure. Label every dollar figure with the rate and assumptions used so it's auditable, never a bare number.
8. **Write the report** (format below). Never silently skip step 5's safety check to get a tidier-looking savings number.

## Output format
```
# SMS-AI Segment Cost Audit

**Batch**: <n> messages, <date range or "pasted log, no dates given">
**Encoding mix**: <n> GSM-7, <n> UCS-2

## Summary
| Metric | Before | Audited-optimal |
|---|---|---|
| Avg. segments/message | X.XX | X.XX |
| Total segments (batch) | N | N |
| Messages crossing a boundary unnecessarily | N (X%) | — |
| Messages flagged "cannot safely compress" | N | — |

## Boundary waste — rewrite suggestions
For each flagged message:
**Original** (N chars, N segments): "<text>"
**Rewrite** (N chars, N segments): "<text>"
**Saved**: N segment(s)

## Cannot safely compress
For each: **Original**: "<text>" — **Blocked by**: <the specific safety-critical content found>

## Cost impact estimate
(Only if a rate was supplied — otherwise state "No rate supplied; segment counts only.")
<formula shown: segments saved × volume × rate = estimate, with all assumptions named>

## Recommendation
One paragraph: is the boundary-waste rate high enough (rule of thumb: >15% of messages) to justify building/adopting compression middleware, or is the batch already close to optimal?
```

## Guardrails
- Never draft a rewrite that removes or alters a number, date, unit, dosage, or warning-like phrase — flag it as "cannot safely compress" instead, even if that message is the single biggest segment-saving opportunity in the batch.
- Never invent a per-segment carrier rate or user count — if none is supplied, report segment counts only and say so explicitly rather than assuming a placeholder rate.
- Never assume GSM-7 encoding for a language/script without checking — misjudging encoding silently produces wrong segment math, which is the entire point of this skill.
- Never claim this audit is a substitute for the compression middleware itself (the idea's PROJECT half) — its job is to produce the evidence a team needs to decide whether that middleware is worth building, not to run in production.
- Never overwrite or "clean up" the user's original pasted log or API response — the report is new output, not a modification of their data.
