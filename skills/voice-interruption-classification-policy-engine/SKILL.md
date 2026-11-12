---
name: voice-interruption-classification-policy-engine
description: Turns a voice-agent team's use-case description into a per-category barge-in/interruption policy (correction, backchannel, noise, DTMF, silence-timeout, safety-escalation) plus a logging checklist, instead of leaving them with a single binary "stop on any sound" toggle. Use when a team is configuring or reviewing how their voice AI agent should react to callers talking over it.
---

# Barge Triage Policy Reviewer

## When to use this
Use this when a team is building, configuring, or reviewing a voice AI agent (IVR, telehealth triage line, insurance/benefits intake, support line, outbound sales/collections line) and needs to decide how the agent responds when a caller talks while it's speaking. The trigger moment is specifically: they currently have (or are about to ship) a single binary interruption setting — "stop the instant any sound is detected" or "never stop until finished" — and need a differentiated policy instead, before or alongside wiring up an actual real-time classifier or configuring a vendor platform's barge-in settings (LiveKit, Pipecat, Retell, Vapi, etc.). This is a design/decision aid, not the running classifier itself — it does not listen to audio, does not ship code, and does not replace testing against real call recordings.

## Inputs
**Data source**: Manual — the user describes their own use case in prose; there is no API or connector involved. Specifically the user provides (or is asked to provide, with reasonable defaults flagged if omitted):
1. **Domain/use case** — e.g. telehealth triage, insurance intake, debt collections, outbound sales, crisis/non-emergency support line.
2. **Caller population notes** — any known skew toward older callers, non-native speakers, noisy environments (call center floor, car, outdoors), or distressed callers. If unknown, say "unknown" rather than guessing.
3. **Risk tolerance** — which failure mode is worse for this use case: cutting the agent off on a false signal (over-sensitive), or the agent talking over a real correction/distress signal (under-sensitive)?
4. **Non-interruptible content** — any specific message types that must play in full regardless of caller behavior (legal disclaimers, payment/consent confirmations, required opt-out notices, dosage/safety instructions).
5. **Current behavior** (optional) — what the agent does today, if anything, so the output can state what changes.

## Procedure
1. Restate the use case back in 1-2 sentences to confirm understanding, and explicitly list which of the 5 inputs above were missing — note the assumption made for each rather than silently guessing.
2. For each of these six interruption categories, derive a recommended action — one of `stop-and-listen`, `continue-and-acknowledge`, `ignore-as-noise`, `route-to-DTMF-handler`, `treat-as-timeout`, `escalate-to-human`:
   - **Correction** (caller is actively changing/contradicting what was just said, e.g. "no, I meant Tuesday")
   - **Backchannel** (caller is signaling they're listening, e.g. "mm-hm", "okay", "right")
   - **Noise** (non-speech audio: cough, background TV, line static)
   - **DTMF** (keypad tone during a menu or form-fill step)
   - **Silence-timeout** (caller has gone quiet past an expected response window)
   - **Safety-escalation** (caller expresses distress, a medical/crisis keyword, or an explicit request for a human)
3. Weight each recommendation against three factors, in this order of priority: (a) whether this exact moment falls inside a listed non-interruptible content block — if so, override to DTMF-only or non-interruptible regardless of category, except safety-escalation, which always escalates even mid-disclaimer; (b) the stated risk tolerance; (c) caller population notes (e.g., noisy environments raise false-noise-as-correction risk, so bias noise handling toward `ignore-as-noise` with a confidence floor rather than stopping).
4. Apply the non-negotiable guardrail for safety-escalation (see Guardrails) regardless of stated risk tolerance.
5. Write a one-line rationale for each of the six rows explaining *why* that action fits this specific use case, not a generic justification that would read the same for any team.
6. Produce a logging/QA checklist: the concrete fields this team should log per interruption event so they can retrain or audit later (timestamp offset into the agent's utterance, which content block was playing, detected/ruled category, action taken, caller's next utterance, whether the call ended in escalation/completion/hangup).
7. List 2-4 open risks specific to this use case (e.g., "no distress-keyword list has been defined for this domain yet" or "no non-English callers considered — policy as written assumes English").

## Output format
A single markdown report with these sections, in this order:
1. **Use case summary** — the restated use case and any flagged missing inputs/assumptions.
2. **Policy table** — 6 rows (one per category) with columns: Category | Example trigger | Recommended action | Rationale.
3. **Non-interruptible overrides** — bullet list of content blocks that override the table above, and what action applies during them.
4. **Logging checklist** — bullet list of fields to capture per event.
5. **Open risks** — 2-4 bullets.

## Guardrails
- Never recommend `ignore-as-noise` or any deferred/no-action outcome for safety-escalation — it always maps to `escalate-to-human`, biased toward over-triggering (a false escalation costs a few seconds; a missed one costs a caller in distress being ignored). This overrides stated risk tolerance, not just suggests it.
- Never output a single uniform action applied to all six categories — if the reasoning converges on the same action for every row, stop and re-examine the use-case inputs, because that collapses back into the exact binary-toggle problem this skill exists to avoid.
- Never present this output as a trained model, working code, or a validated policy — it is a design recommendation to be tested against real call recordings before being trusted in production, and the report must say so.
- Never invent caller statistics, engagement numbers, or population data the user didn't provide — if population notes are "unknown," say so in the summary rather than filling in a plausible-sounding default.
- Default any content the user flags as legal, compliance, consent, or safety-instruction-related to non-interruptible or DTMF-only unless the user explicitly overrides that default, and say so explicitly when applied.
- If the user's risk tolerance input conflicts with the safety-escalation guardrail (e.g., "bias toward never stopping, even for distress signals"), flag the conflict in the output rather than silently complying.
