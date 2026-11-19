---
name: medical-llm-guideline-grounding-middleware
description: Checks a draft medical-LLM response claim-by-claim against a pasted clinical guideline excerpt, flagging each distinct clinical claim as grounded, ungrounded, or contradicted. Use when a developer is building or QA-testing a medical LLM tool for low-resource/frontline deployment and needs to know, before shipping, whether the model's output is actually backed by the guideline it's supposed to follow.
---

# Guideline Gate: Claim-by-Claim Grounding Check

## When to use this
A developer is iterating on a medical LLM tool (chatbot, triage assistant, patient-education generator) meant for frontline, non-specialist, or low-resource deployment, and has a draft model response in hand. They need a development-time/QA check — not a live production system — that tells them which specific clinical claims in that response are actually supported by the clinical guideline the tool is supposed to follow, before they trust it enough to show a frontline worker or ship a build. Reach for this skill whenever someone pastes a model's medical-advice-shaped output and asks "is this grounded in our guideline?", "can I trust this response?", or "check this against the protocol."

This is explicitly a one-shot, human-in-the-loop development aid — not an always-on inline middleware. It has no access to a live corpus or retrieval index; everything it reasons over must be pasted into the conversation.

## Inputs
**Data source**: Manual — the user pastes (a) the draft model response to be checked, and (b) the relevant clinical guideline excerpt(s) it should be grounded in (e.g., a WHO IMCI protocol section, a Ministry of Health guidance excerpt, an ADA/WHO/CDC guideline passage). There is no mature cross-region API that serves "the locally-applicable clinical guideline" uniformly, so this cannot be CONNECTED — the guideline text must always be supplied by the user for the specific region/protocol in play.

Required for a usable run:
1. The full draft response text (the thing being checked).
2. The guideline excerpt(s) it's meant to comply with — paste the actual passage, not a summary or a link. If the user only has a link or filename, ask them to paste the relevant text before proceeding; do not proceed on a guideline you haven't actually seen.
3. (Optional but recommended) The clinical domain/condition and target deployment context (e.g., "diabetes screening, community health worker, low-bandwidth clinic") — this sharpens what counts as an in-scope claim vs. general background information.

If either (1) or (2) is missing, stop and ask for it. Do not guess at guideline content from general medical knowledge and present that as "grounded" — that defeats the entire purpose of the check.

## Procedure
1. **Decompose the response into atomic clinical claims.** Split the draft response into the smallest independently-checkable factual/clinical assertions (dosages, diagnostic criteria, referral thresholds, contraindications, timelines, red-flag symptoms, treatment steps). Skip purely conversational filler, disclaimers, and non-clinical phrasing — list only the substantive claims.
2. **For each claim, search the pasted guideline excerpt for direct support.** A claim is:
   - **GROUNDED** — the guideline excerpt states this claim directly or via a clear, unambiguous logical restatement. Quote the exact supporting line(s).
   - **CONTRADICTED** — the guideline excerpt says something different or stricter/looser than the claim (e.g., response says "refer if fever > 38.5°C" but guideline says "> 38°C"). Quote the conflicting line and state the discrepancy explicitly.
   - **UNGROUNDED** — the claim is not addressed anywhere in the pasted excerpt at all (not even partially). This is the default for anything not found — never upgrade a claim to GROUNDED on the basis of general medical plausibility or outside knowledge not present in the pasted text.
3. **Do not fill gaps with your own medical knowledge.** If the guideline excerpt is silent on a claim, the claim is UNGROUNDED regardless of whether you believe it to be medically correct. The entire point of this check is "does this guideline say so," not "is this true."
4. **Flag ambiguous or multi-part claims separately.** If a single sentence bundles a grounded sub-claim with an ungrounded one (e.g., "give amoxicillin [grounded] twice daily for 7 days [not in excerpt]"), split it and score each part independently rather than averaging.
5. **Compute an overall grounding score**: `grounded claims / total claims`, reported alongside the count of CONTRADICTED claims called out separately (a contradiction is worse than an absence and must never be hidden inside the score alone).
6. **Write an explicit recommendation line**: if any claim is CONTRADICTED, or the grounded fraction is below roughly two-thirds, recommend against shipping/using the response as-is and say why in one sentence.

## Output format
Produce exactly this structure:

```
## Grounding Check: <short label for the response, e.g. "Diabetes screening response v2">

| # | Claim (verbatim or lightly trimmed) | Verdict | Evidence from guideline excerpt |
|---|---|---|---|
| 1 | <claim text> | GROUNDED | "<quoted guideline line>" |
| 2 | <claim text> | UNGROUNDED | (no matching passage found in the pasted excerpt) |
| 3 | <claim text> | CONTRADICTED | "<quoted guideline line>" — discrepancy: <one-line explanation> |

**Grounding score**: X/Y claims grounded (Z%)
**Contradictions**: <count> — <list claim numbers, or "none">
**Recommendation**: <SHIP AS-IS / REVISE BEFORE USE / DO NOT USE> — <one-sentence reason>
```

Always include every claim found in step 1, even ones that turn out trivially grounded — an evaluator needs the full accounting, not a filtered summary.

## Guardrails
- Never mark a claim GROUNDED on the strength of outside medical knowledge, training data, or "this is generally true in medicine" — only the pasted guideline excerpt counts as evidence. This skill checks guideline compliance, not medical correctness.
- Never proceed without an actual pasted guideline excerpt. A guideline name, citation, or link is not sufficient — if the user hasn't pasted the text, ask for it rather than reasoning from a assumed/recalled version of that guideline, which may be outdated or region-mismatched.
- Never collapse a CONTRADICTED claim into the UNGROUNDED bucket — a contradiction is a more urgent, actively-misleading failure mode than silence, and burying it inside one aggregate score is exactly the false-trust failure this check exists to prevent.
- Never present this one-shot check as equivalent to the always-on production middleware described in the parent project — this skill is a development-time/QA aid run by a builder while iterating; it has no retrieval system, no live corpus, and does not run automatically on every production response.
- Never soften "UNGROUNDED" to something like "likely fine" or "probably standard practice" in the output — the verdict column exists precisely so a non-specialist reader doesn't have to make that judgment call themselves.
