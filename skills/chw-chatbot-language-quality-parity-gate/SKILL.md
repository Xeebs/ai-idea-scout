---
name: chw-chatbot-language-quality-parity-gate
description: Audits exported community-health-worker chatbot Q&A logs for clinically meaningful gaps between a local-language answer and the same chatbot's English answer to the same question, and ranks the riskiest discrepancies for a clinical supervisor to review. Use when a CHW program wants a periodic or post-complaint quality audit of local-language chatbot answers, not a live production filter.
---

# CHW Chatbot Language-Quality Parity Gate

## When to use this
A clinical supervisor, program manager, or M&E staffer on a community-health-worker (CHW) chatbot deployment (WhatsApp/Telegram/SMS, any LLM backend) has exported a batch of past conversations and wants to know: did the chatbot's answer in the local language ever say something clinically different — missing a dosage, softening a referral warning, dropping a danger sign — from what it told the same question in English? Use this skill to run that batch audit. Typical triggers: a scheduled weekly/monthly quality review, a CHW or patient complaint that a local-language answer seemed "off," or validating a chatbot before scaling it to a new local language.

This is a retrospective, human-in-the-loop audit tool, not a live message filter. It does not intercept or block anything in production — it tells a human reviewer where to look.

## Inputs
**Data source**: Manual — the user pastes a batch of question-answer transcript pairs exported from their chatbot's logs. No connector exists (or is implied) for this; the idea file omitted an explicit Data Sources line, so this is inferred directly from its Skill Angle section, which describes "a pasted batch of CHW chatbot Q&A transcript pairs."

For each item in the batch, the user must supply:
1. The clinical question as a CHW actually asked it, in the local language.
2. The chatbot's answer to that question, in the local language.
3. The same question re-asked in English (either a direct re-ask of the chatbot or a faithful translation of item 1) — must be the *same underlying clinical question*, not a paraphrase that changes scope.
4. The chatbot's answer to that English re-ask.

Optional but useful if available:
- A topic/category tag per question (e.g., "neonatal danger signs," "malaria dosing," "ANC referral").
- The local language name (e.g., Kinyarwanda, Chichewa, Hindi).
- Any known ground-truth fact (e.g., the correct dosage) if the supervisor already has it — the skill will use it to sanity-check both answers, not just compare them to each other.

If fewer than 2 complete pairs are supplied, or any pair is missing one of the four required fields, do not score it — list it under "Incomplete / excluded" instead of guessing.

## Procedure
1. **Parse the batch** into individual question pairs, numbered in the order given. Exclude and list separately any pair missing a required field (see above).
2. **Check pairing validity** for each remaining pair: confirm the English re-ask is actually the same clinical question as the local-language question (same symptom, same patient context, same specific ask — e.g., "what dose" vs "should I refer"). If scope clearly differs, mark the pair "pairing uncertain" and exclude it from scoring rather than comparing mismatched questions.
3. **Extract key clinical facts** from the English answer first (it's the reference side for this comparison, not because it's assumed correct — see guardrails): named medications/treatments, numeric values (doses, ages, durations, temperatures, measurements), referral/danger-sign thresholds, urgency/timing language ("today," "immediately," "if it persists"), and any hedging or uncertainty language ("may," "should," "always," "never").
4. **Check each extracted fact against the local-language answer**: present and matching, present but altered (wrong number, wrong urgency word, weaker hedge), or absent entirely.
5. **Score each pair's severity** using this rubric, taking the single worst finding in the pair:
   - **CRITICAL**: a numeric/dosage value differs, a danger sign or referral threshold is missing or downgraded, or urgency language is weakened (e.g., English says "go to clinic today," local-language says "go to clinic if needed").
   - **MAJOR**: a clinically relevant fact is missing or clearly softer, but no number/urgency has been altered (e.g., a named complication dropped, a caveat removed).
   - **MINOR**: wording/tone/structure differs but no clinical fact, number, or urgency changed.
   - **SAFE**: no meaningful content difference found.
6. **Rank the batch** CRITICAL first, then MAJOR, then MINOR, then SAFE.
7. **Write a plain-language explanation for every CRITICAL and MAJOR pair**: quote the specific fact from the English answer and the specific gap in the local-language answer, in one or two sentences a non-technical clinical supervisor can act on without reading model internals.
8. **Look for clustering** across the batch: same topic tag, same type of gap (numbers vs. urgency vs. missing danger signs), or same language recurring across multiple CRITICAL/MAJOR pairs. Note this as a pattern, not just a list of isolated incidents.
9. **Compute summary counts**: total scored, excluded/incomplete, and count per severity tier.

## Output format
A single markdown report with these sections, in this order:

```
# Language Parity Audit — <N> pairs reviewed

## Summary
- Scored: <n> | Excluded (incomplete/pairing uncertain): <n>
- CRITICAL: <n> | MAJOR: <n> | MINOR: <n> | SAFE: <n>

## Flagged Pairs (ranked, worst first)
| # | Severity | Topic | What's wrong |
|---|----------|-------|---------------|
| 7 | CRITICAL | Malaria dosing | English: "5mg/kg every 8 hours." Local: dose number missing entirely. |
...

## Detail: CRITICAL and MAJOR pairs
### Pair #7 — CRITICAL
- **Question**: <as given>
- **English answer excerpt**: <quoted>
- **Local-language answer excerpt**: <quoted or translated-back excerpt>
- **Gap**: <plain explanation of exactly what's missing/altered and why it matters clinically>

(repeat per flagged pair)

## Patterns Observed
<1-4 bullets naming recurring topics, languages, or gap types across the batch — this is what program staff act on structurally, beyond fixing one answer>

## Excluded / Incomplete
<list of pair numbers excluded, with the reason>

## Disclaimer
This is a consistency check between two chatbot outputs, not a medical-accuracy check against ground truth — if both the English and local-language answers are wrong in the same way, this audit will mark that pair SAFE. Every CRITICAL/MAJOR finding requires review by a qualified clinical supervisor before any chatbot behavior, protocol, or CHW guidance is changed.
```

## Guardrails
- Never score a pair without all four required fields present — list it as excluded instead of inferring a missing answer.
- Never treat a "pairing uncertain" case as scorable — mismatched questions produce meaningless comparisons and must be excluded, not force-fit.
- Never downgrade a numeric/dosage/urgency discrepancy below CRITICAL, even if it looks minor in wording — these are exactly the gaps the underlying research (Rwanda CHW study) found have direct patient-safety consequences.
- Never claim or imply this output has verified medical accuracy — it only verifies agreement between two chatbot outputs. State the disclaimer every time, not just once in the skill description.
- Never present this skill as a live/production filter — it is a retrospective batch audit a human runs on exported logs. If asked to "wire this into WhatsApp live," say explicitly that this skill's output format and manual-review step are not designed for that; that is the separate always-on middleware version described in the parent idea's Project section, not this skill.
- Never invent clinical facts not present in the pasted answers (e.g., don't supply the "correct" dosage from general training knowledge unless the user explicitly supplied it as a known ground truth) — stick to comparing what the two answers actually said.
