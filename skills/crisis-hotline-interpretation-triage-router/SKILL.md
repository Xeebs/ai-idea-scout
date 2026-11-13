---
name: crisis-hotline-interpretation-triage-router
description: Pre-deployment reliability audit for machine translation on a crisis or volunteer hotline — flags script degradation, urgency distortion, and meaning-drop failures in a sample batch, then recommends a go/no-go verdict and escalation threshold for a specific language pair before it goes live.
---

# Crisis Hotline MT Triage Audit

## When to use this
A crisis-response org, volunteer hotline, humanitarian NGO, or disaster-response coordinator is deciding whether to let machine translation (MT) handle a specific language pair unsupervised, or how much of it to route to human interpreters. They have (or can collect) a batch of real or representative MT outputs for that pair and want a structured, evidence-based answer to "is this safe enough to deploy, and if not, what's the triage rule?" — before committing scarce human-interpreter capacity or risking a silently-wrong answer reaching someone in crisis.

This is a **one-time or periodic audit**, run before deployment or when adding a new language pair/domain. It is not a live call-routing system — it does not process real-time calls or messages.

## Inputs

**Data source**: Manual — the user pastes a batch of source-language messages paired with their MT outputs (and ideally a back-translation or bilingual reviewer's accuracy note for each). There is no live connector: this skill only evaluates what is handed to it.

Required before running:
1. **Language pair** — source language → target language (e.g., Haitian Creole → English, Dari → English).
2. **Crisis context/domain** — one of: medical/health triage, logistics/shelter/evacuation, missing-persons/family reunification, emotional support/mental health, general information. Domain changes how severely a given failure is scored.
3. **Sample batch** — at minimum 20-30 message pairs, each with:
   - The original source-language message (or a close gloss if the reviewer can't paste native script)
   - The MT output as actually produced
   - Ideally, one of: a back-translation of the MT output into the source language, OR a bilingual reviewer's one-line accuracy note, OR a known ground-truth urgency label ("this is a life-threatening emergency" vs. "routine request")
4. Optional but useful: which MT system/model produced the output (e.g., Google Translate API, NLLB, Llama3.2-1B, X-ALMA, a commercial vendor) — contextualizes which known failure modes are most likely.

If fewer than 20 pairs are provided, proceed but mark the final verdict's confidence as LOW and say so explicitly. If no source text or accuracy signal is provided at all (just MT output alone), do not assess accuracy — ask for the source text first.

## Procedure

1. **Confirm inputs.** Restate the language pair, domain, sample size, and MT system (if known). If sample size <20, flag low-confidence mode now, not just at the end.
2. **Score each message pair** against this failure taxonomy:
   - **Script degradation**: garbled characters, incomplete rendering of the target script, mixed-script artifacts, token repetition/truncation, or output that isn't actually in the stated target language.
   - **Urgency distortion**: the MT output's perceived urgency differs from the source — hedging added ("must evacuate" → "may want to leave"), modal/tense downgrades, dropped time-critical markers ("immediately," "right now," a deadline), or an emergency reframed as routine (or vice versa, which wastes scarce response capacity).
   - **Meaning drop / content error**: negation flips, numeric or quantity errors (critical for medication dosage, headcounts, addresses), dropped named entities (locations, medications, person names), or a swapped subject/object that reverses who needs help.
   - **Confidence calibration gap**: if the MT system's own confidence/log-prob score was supplied, check whether low-confidence outputs correlate with the failures above. If no confidence score exists, note this as a visibility gap rather than guessing.
3. **Assign a per-message risk level** — HIGH, MEDIUM, or LOW — weighted by domain:
   - In medical/health and emotional-support/mental-health domains, any urgency distortion or meaning drop is at least MEDIUM, and any that could delay or misdirect emergency response is HIGH.
   - In logistics/shelter domains, numeric/address errors are at least MEDIUM; wording ambiguity alone is LOW.
   - In general-information domains, most issues are LOW unless they invert meaning.
4. **Aggregate findings**: compute the percentage of HIGH/MEDIUM/LOW across the batch, identify the 1-3 most common failure types for this specific language pair, and check whether failures cluster in a particular domain or message type within the batch.
5. **Recommend an escalation rule**: a concrete, specific threshold an org could actually operate (e.g., "escalate to a human interpreter any message in the medical domain, plus any message flagged MEDIUM or HIGH by [these keyword/pattern cues]") rather than a vague "use judgment."
6. **Issue a go/no-go verdict** with an explicit confidence qualifier tied to sample size and evidence quality (never present a HIGH-confidence verdict off a small or unverified sample).

## Output format

A single audit report with these sections, in this order:

```
# MT Reliability Audit — <language pair> / <domain>
Sample size: <n> message pairs | MT system: <name or "unspecified">
Confidence in this verdict: HIGH / MEDIUM / LOW (driven by sample size + whether accuracy signals were provided)

## Flagged Messages
| # | Source (excerpt) | MT Output (excerpt) | Failure Type(s) | Risk |
|---|---|---|---|---|
(only messages with a flag — do not list every clean message)

## Summary
- Risk distribution: X% HIGH, Y% MEDIUM, Z% LOW
- Most common failure type(s) for this pair: ...
- Pattern(s) noticed: ...

## Recommendation
- Go/No-Go for unsupervised MT: <verdict>
- Escalation rule: <specific, operable rule>
- What would raise confidence in this verdict: <e.g., "a larger sample," "a bilingual reviewer validating the back-translations," "a field pilot with logged outcomes">
```

## Guardrails

- Never issue a "go" (fully unsupervised MT, no escalation) verdict for the medical/health or emotional-support/mental-health domains, regardless of how clean the sample looks — recommend human-in-the-loop escalation for at least the highest-risk message types in those domains always. The cost of a missed emergency vastly outweighs the cost of an unnecessary human review.
- Never assess translation accuracy from MT output alone with no source text, back-translation, or bilingual reviewer note — say so and ask for one of those instead of guessing at correctness.
- Never report a HIGH-confidence go/no-go verdict from a sample under 20 messages — cap confidence at LOW and say why.
- Never treat automatic metrics (BLEU, chrF, etc.) as sufficient evidence of safety if that's all that's supplied — flag the absence of human/bilingual validation as a limitation, don't silently accept the metric as proof.
- Never present this as a live call-routing or real-time triage system — it is a pre-deployment/periodic audit of a sample batch. If the user describes wanting real-time routing of live calls, say this skill is the pre-deployment audit step, not the always-on middleware, and that the latter is a larger build.
- Never invent failure examples, percentages, or language-specific linguistic claims not grounded in the actual pasted sample — every flagged row must trace to a specific message in the batch the user provided.
