# Scenario 2: Indie audiobook/animation studio with a decent consent process but thin disclosure (mixed PARTIAL/COVERED expected)

## Input (as a user would paste it)

**What the voice clone is used for**: We're a small animation studio. We clone the voice of one of our voice actors to generate extra dialogue lines in post-production when the actor isn't available for a pickup session, for an animated series we sell to streaming platforms. This is clearly a fictional/creative work — it's animated character dialogue, not a real person speaking as themselves.

**My role**: We're a deployer — we use a third-party voice-cloning tool (not something we built) to generate the extra lines ourselves, in-house.

**Current consent-collection process for the voice donor**: Every voice actor signs a contract clause (drafted by our entertainment lawyer) that explicitly grants us the right to generate additional synthetic dialogue in their cloned voice for this specific production, with a stated expiry at the end of our rights window for that show. We keep signed copies in our contract management system, searchable by actor name and production.

**Current disclosure practice toward listeners/recipients**: We don't disclose anywhere that some lines were AI-generated — our credits just list the voice actor's name as the character's voice, same as any other episode. We haven't thought about whether we need to say anything given this is clearly fictional animated content.

**Jurisdiction(s) of operation**: We distribute globally, including to EU streaming platforms.

## Procedure walkthrough (self-check)

1. Role classification: Deployer (explicitly stated; they license a third-party tool rather than building one).
2. Exception check: this is animated character dialogue — evidently fictional/creative content — so the artistic/satirical/fictional exception plausibly applies, but the skill must still flag this as needing confirmation ("needs confirmation" or "applies, but confirm narrow scope"), not wave it through unconditionally, since it's a legal judgment call the skill isn't positioned to finalize.
3. Consent Evidence: COVERED — a signed, production-specific contract clause with an expiry, stored and retrievable by actor/production, is exactly the "timestamped, voice-linked, retrievable" bar described in the skill. This is the scenario's main point: a well-built skill must actually recognize a good-faith, well-documented consent process as COVERED, not score everything GAP by default.
4. Disclosure Compliance: PARTIAL or GAP — no disclosure of AI-generated dialogue exists anywhere, and while the fictional-work exception may reduce the disclosure burden, the studio hasn't actually confirmed that reasoning applies or determined whether any disclosure (even a minimal one, proportionate to not disrupting the work) is still required — this must be scored PARTIAL at best, with an explicit instruction to confirm the exception's applicability rather than assuming it closes the question outright.
5. Technical-Detection Reliance: COVERED or N/A with a one-line note — the input describes no detection pass being used as a compliance crutch at all, so there's nothing being misused as proof of consent; this axis should not be scored GAP just because no detection technology was mentioned.
6. Remediation checklist should mainly address the disclosure uncertainty (confirm whether the exception truly covers this and whether any proportionate disclosure is still owed) rather than consent (which is already well-handled) — a good output does NOT invent consent-related remediation items when the input shows a solid process.
7. Legal basis caveat and disclaimer must still appear even though this is a lower-risk case.

## Pass criteria

- [ ] Role classified Deployer.
- [ ] Exception check says the fictional/animated framing plausibly applies but flags it as needing confirmation, not an unconditional pass.
- [ ] Consent Evidence scored COVERED, with justification citing the signed, production-specific, retrievable contract clause — demonstrating the skill can recognize a good process, not just find gaps everywhere.
- [ ] Disclosure Compliance scored PARTIAL (or GAP), with reasoning that the fictional-work exception hasn't been confirmed to fully resolve the disclosure question, and that no disclosure of any kind currently exists.
- [ ] Technical-Detection Reliance scored COVERED or explicitly marked not-applicable, with a note that no detection pass is being misused as a consent proxy — not incorrectly scored GAP for lack of any detection mention.
- [ ] Remediation checklist is proportionate: focuses on confirming/resolving the disclosure question, does not fabricate consent-process fixes for an already-solid process.
- [ ] Legal Basis Caveat and Disclaimer sections both present despite the lower overall risk.

## Fail conditions

- Scoring Consent Evidence as GAP or PARTIAL despite the described signed, voice-linked, retrievable contract clause (this would show the skill defaults to pessimism regardless of input quality).
- Treating the fictional/animated exception as an automatic, unconditional pass with no confirmation caveat.
- Inventing consent-related remediation items that aren't justified by any described gap.
- Scoring Technical-Detection Reliance as GAP when no detection technology was described as being used or misused at all.
