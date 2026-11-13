# ConsentGate: A Watermark + Liveness + Linked-Consent Verification Layer for Live Voice Calls

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Voice & multimodal agents
- **Source**: research/2026-11-12-voice-multimodal-agents-iii.md · P4
- **Maturity verdict**: PARTIAL (Voice Truthgate — an open-core, MIT-licensed MCP server for voiceprint enrollment and clip-checking — exists, but its own maker reports a targeted clone accepted 63% of the time at the operating threshold and recommends it only as one signal, not a standalone verdict, and it doesn't tie the check to a recorded consent record; commercial watermarking (Resemble AI) explicitly concedes a missing watermark proves nothing; no system combining watermark + spectral-artifact + liveness + a linked consent record was found)
- **Format**: BOTH
- **Data Sources**: CONNECTED — the runtime verification layer reads the live call's audio stream directly (via the voice-agent platform's media API, e.g. LiveKit or Twilio Media Streams) against a self-hosted consent registry that a voice owner enrolls into once (a short verified sample plus a signed consent record), not pasted per call. Voice Truthgate's enrollment/check primitives and Resemble's watermark-detection API already exist and are mature enough to compose; the linked-consent-record ledger is the piece that needs building.

## The Gap
Resemble AI's own material concedes "the absence of a watermark doesn't prove a voice is human," and that detection "answers with a confidence score... it does not read intent or confirm consent." Voice Truthgate is the one real open-source attempt at going further, but its maker reports a 63% false-accept rate on a targeted clone at the operating threshold, and it never ties a check to an actual recorded consent record — just similarity/liveness. The search found no system answering "has anyone built" a consent-verification layer for agent calls. Meanwhile the gap is causing live harm, not a theoretical risk: Lovo's Chapter 7 bankruptcy coincided with a still-pending voice-actor lawsuit over unconsented cloning, and the EU AI Act's Article 50 disclosure deadline (cited as August 2026 in the digest, unverified against the primary text) creates fresh regulatory pressure with no compliant off-the-shelf answer yet.

## The Project
A verification pipeline for live calls that combines watermark detection, spectral-artifact detection, and a liveness challenge with an actual consent ledger — a signed record linking a voiceprint hash to consent text, timestamp, and optional expiry — so a call can be checked for "is this clone authorized" rather than only "is this synthetic." The ledger is the centerpiece: every existing piece (Truthgate, Resemble) stops at a similarity/authenticity score, and none links that score to a recorded authorization.

Components: a voiceprint enrollment/consent-record ledger, a composed detection pass (watermark + spectral + liveness, built on Voice Truthgate and a commercial watermark API), and a three-state verdict output (verified-consented / synthetic-no-consent-record / inconclusive) exposed as a callable check during a live call.

## Tangible Impact
**Population**: voice professionals and private individuals at risk of unauthorized voice cloning — the digest's cited Lovo lawsuit is concrete evidence of current harm to this group — plus any business or call-center operator subject to the EU AI Act's Article 50 disclosure obligation who currently has no compliant off-the-shelf way to prove a given cloned voice was authorized.
**Mechanism**: a platform or recipient can query whether a specific voice clip corresponds to a voiceprint with a linked, recorded consent record, instead of relying on a bare synthetic-confidence score that proves nothing about authorization — closing the exact gap Resemble's own material admits exists.
**Measure**: false-accept rate on known-unauthorized clones (63% at Truthgate's own threshold is the baseline to beat); time for a platform to produce an audit-ready consent record for a disputed clip (currently no standard mechanism exists at all); percentage of test calls where the system correctly flags a clone lacking a linked consent record.

## Why Now
The EU AI Act's Article 50 disclosure deadline creates fresh compliance urgency in 2026, and Lovo's bankruptcy alongside a pending lawsuit shows the harm is active, not hypothetical. The underlying building blocks (Voice Truthgate's enrollment/liveness primitives, mature commercial watermark-detection APIs) exist today — this is a composition and ledger-building problem, not a capability-wait problem.

## Skill Angle
A companion skill, "voice-clone consent audit," is a one-shot compliance-review task: given a pasted description of an organization's current voice-cloning/disclosure practices (policy text, call-flow description, or sample disclosure script), it flags gaps against the EU AI Act Article 50 disclosure requirement and the "watermark-is-not-consent" failure mode Resemble's own material documents, and drafts a remediation checklist. This is genuinely separable from the project: the skill is a one-shot review a compliance or legal team runs before deciding whether to build or buy the runtime verification layer; the project is the always-on verification infrastructure that runs during live calls.

## MVP Sketch
Combine Voice Truthgate (voiceprint enrollment + similarity/liveness) with a minimal signed consent-record ledger (voiceprint hash + consent text + timestamp + optional expiry, stored append-only) and a watermark-detection pass (Resemble or an equivalent API) into one pipeline returning the three-state verdict above. Validate on a held-out test set of consented vs. simulated-unauthorized clone clips, building on and explicitly re-measuring Voice Truthgate's own 63% false-accept benchmark, to show the combined pipeline reduces false-accepts versus Truthgate alone.

## Risks & Open Questions
- Voice Truthgate's own 63% false-accept rate suggests the underlying liveness/similarity technology may have a hard reliability ceiling regardless of how it's combined with other signals — this could be a technical limit, not an integration gap.
- A consent-record ledger is only as trustworthy as the enrollment process; coercive or fraudulent "consent" obtained at enrollment time isn't solved by this layer.
- The EU AI Act Article 50 deadline is cited as unverified in the source digest — the regulatory-urgency claim needs independent confirmation before being weighted heavily in positioning.
- Marketing a "verified" badge beyond what the underlying detection accuracy actually supports risks creating false assurance rather than genuine risk reduction — must be scoped explicitly as risk-reduction, not proof.
