---
name: emergency-dispatch-voice-liveness-detector
description: Builds a structured swatting-risk assessment and verification checklist for a 911/PSAP supervisor reviewing one suspicious or flagged call after the fact, using the transcript, call metadata, and dispatcher notes against a documented AI-voice-swatting red-flag pattern — not a live audio-analysis tool. Use when a dispatch supervisor or investigator needs to document whether a specific call looks like an AI-cloned-voice swatting attempt before deciding on next steps.
---

# Emergency Dispatch Voice-Swatting Risk Reviewer

## When to use this
A 911/PSAP supervisor, quality-assurance reviewer, or investigator has one specific call they suspect may have involved an AI-cloned or synthetic voice (a "swatting" pattern: a fabricated violent-crime report sent to an address to trigger an armed response) and needs a documented, defensible risk assessment plus a next-step checklist — produced *after* the call, as part of post-incident review or before escalating a pattern of suspicious calls to investigators. This is not a real-time call-screening tool and does not replace a dedicated audio-forensics/voice-liveness detection product; it is the human-review layer that structures a decision when no such product is deployed, or that adds transcript/context-level reasoning on top of one that is.

## Inputs
**Data source**: Manual — the reviewer pastes in: (1) the call transcript or the most complete verbatim reconstruction available (CAD call notes, recording transcript, or dispatcher's own typed account), (2) call metadata (ANI/caller ID shown, timestamp, call duration, address/location given by the caller), (3) the dispatcher's contemporaneous notes on how the voice/audio sounded (tone, pacing, background noise, anything that struck them as odd), and (4) optionally, the output of any third-party audio-liveness/deepfake-detection tool already run on the recording (score and tool name only — this skill does not perform audio signal analysis itself and never claims to).

## Procedure
1. **Confirm minimum inputs.** Require at minimum a transcript/notes and the call metadata. If only a bare audio file is offered with no transcript, ask the user to transcribe it (or paste CAD notes) first — this skill works from text evidence, not raw audio.
2. **Run the red-flag checklist.** Evaluate the transcript/metadata/notes against each of these documented AI-voice-swatting patterns, marking each `PRESENT`, `ABSENT`, or `UNCLEAR` with the exact quoted or paraphrased evidence line that supports the call:
   - Flat, monotone, or oddly even prosody inconsistent with the claimed level of panic/distress.
   - Unnatural pacing: no breathing sounds, no disfluencies ("um," restarts), or mechanically even sentence timing.
   - Scripted-sounding phrasing — overly complete, grammatically clean sentences for a claimed panic situation.
   - Caller volunteers unusually specific, actionable details early and unprompted (exact address, occupant count/description, weapon make, room layout) without the dispatcher having to extract them.
   - Caller resists, deflects, or gives inconsistent answers to standard verifying questions (name, callback number, exact relationship to the address).
   - Background noise inconsistent with the claimed location or situation (e.g., claims to be hiding in a house but audio is dead silent or has an odd consistent hum).
   - ANI/caller-ID does not match the claimed caller identity or location, or shows signs of spoofing (out-of-area number claiming local address, number previously tied to unrelated incidents).
   - No valid callback number, or callback goes straight to voicemail/disconnected/a different person who denies the call.
   - Call duration or hang-up pattern is anomalous relative to how a genuine panicked caller for this incident type typically behaves (e.g., abrupt hang-up right after delivering the key actionable detail).
3. **Fold in third-party detector output as one weighted signal, never the deciding one.** If the user supplied a score from a dedicated tool, include it labeled explicitly as "third-party tool output, not independently verified by this review" — never let it override the transcript-based checklist, and never treat an unnamed/unverifiable vendor claim as evidence of anything.
4. **Assign an overall risk tier** — `LOW`, `ELEVATED`, or `HIGH SUSPICION OF SYNTHETIC-VOICE SWATTING` — based on the count and weight of `PRESENT` flags (treat ANI mismatch and no-valid-callback as the two highest-weight flags; treat any single `UNCLEAR` prosody-only flag alone as insufficient for anything above `LOW`). Always state the tier is a decision-support signal, never a forensic determination of what the caller actually was.
5. **Write the verification checklist** matched to the tier: `LOW` → standard documentation only, no special action; `ELEVATED` → recommend supervisor-initiated callback-verification and cross-check of the address against recent call history before any change in response posture; `HIGH SUSPICION` → recommend immediate supervisor review, callback verification attempt, and coordination with responding units on approach caution — but explicitly note this skill cannot and does not authorize delaying, downgrading, or declining dispatch of any emergency response; that decision stays with policy and command staff.
6. **Produce the evidence log entry** — a short, dated, chain-of-custody-ready paragraph suitable for pasting into the official case file, stating what was reviewed, what flags were found, the assigned tier, and the recommended next step.

## Output format
A single markdown report with these sections, in order:
1. **Call Summary** — one paragraph: timestamp, ANI, claimed location, claimed incident type, duration.
2. **Red-Flag Checklist** — a table with columns Flag | Status (PRESENT/ABSENT/UNCLEAR) | Evidence.
3. **Third-Party Detector Signal** — the supplied score/tool name, or "None supplied."
4. **Overall Risk Tier** — the tier, with a one-sentence rationale citing the highest-weight flags.
5. **Recommended Verification Actions** — the tier-matched checklist from step 5.
6. **Evidence Log Entry** — the pasteable paragraph from step 6.

## Guardrails
- Never state a definitive conclusion that a voice "is" or "is not" synthetic — only a risk tier with stated reasoning. This skill does not perform audio signal analysis and must never imply that it did.
- Never recommend delaying, downgrading, or declining to dispatch a response to a call based on this review alone — the output is always framed as "flag for supervisor verification," never as a stand-down recommendation.
- Never fabricate spectral, prosodic, or other acoustic-feature findings that weren't actually in the transcript/notes/third-party output supplied — if the dispatcher's notes don't mention voice quality, mark every prosody-related flag `UNCLEAR`, not `ABSENT`.
- Never treat an unverified vendor marketing claim (e.g., a blog post claiming unnamed states use a product) as evidence in the checklist or risk tier.
- Never skip stating, in the evidence log entry, that this is non-evidentiary decision support and that any legal/prosecutorial use requires independent review of the raw audio by a qualified forensic audio examiner.
- Never use this for real-time call screening — it is explicitly a post-incident/after-the-fact review tool, not a live dispatch-console integration (that is the separate "project" half of this idea, not this skill).
