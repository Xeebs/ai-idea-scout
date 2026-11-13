# Scenario 1: Call-center voice-AI vendor relying solely on a watermark check (multiple GAPs expected)

## Input (as a user would paste it)

**What the voice clone is used for**: We're a voice-AI vendor. We offer a feature where a business client can have their IVR/support line answer in a cloned version of one of their own employees' voices (e.g., "answered by Maria's voice") instead of a generic TTS voice, for brand continuity. We license a commercial watermarking SDK and embed a watermark in every synthesized clip we generate.

**My role**: We're the provider — we build and sell the voice-cloning technology; our business clients are the ones deploying it on their own support lines.

**Current consent-collection process for the voice donor**: When a client wants to clone an employee's voice, our onboarding flow has the client confirm a checkbox that says "I have the right to use this voice" before uploading the sample. We don't independently verify this, and we don't keep a record tying a specific consent statement to a specific voiceprint — just the checkbox event in our signup logs.

**Current disclosure practice toward listeners/recipients**: We embed the watermark SDK's mark in every output clip. We don't require our clients to tell callers "you're talking to a synthetic voice" — our sales material tells clients "our watermarking keeps you compliant," so most clients haven't added any separate verbal disclosure.

**Jurisdiction(s) of operation**: We have several clients with EU call centers.

## Procedure walkthrough (self-check)

1. Role classification: Provider (stated explicitly) — the business clients deploying the IVR are Deployers, though the user is only speaking for their own (provider) side.
2. Exception check: this is a customer-support/commercial use, not evidently artistic/satirical/fictional — exception does not apply.
3. Consent Evidence: GAP — a self-attestation checkbox with no independent verification and no record linking a specific consent statement to a specific voiceprint is exactly the PARTIAL/GAP boundary described in the skill; here it tips to GAP because there's no voice-linked, retrievable consent artifact, only a generic signup-log event.
4. Disclosure Compliance: GAP — the provider is relying on the deployer to add disclosure, but has told clients the watermark alone satisfies compliance, and most clients added no separate disclosure. This is the textbook "deployer relying solely on provider's marking" failure the skill must name explicitly, with EU clients in scope raising applicability.
5. Technical-Detection Reliance: GAP — the sales material explicitly claims "our watermarking keeps you compliant," treating the watermark as proof of compliance/consent rather than a separate fraud signal. This must be flagged as the named failure mode.
6. Remediation checklist should rank: (a) fixing the sales messaging and giving clients a client-facing disclosure requirement (regulatory-deadline exposure for EU clients), (b) building a real voice-linked consent record (litigation exposure — this is unverified self-attestation, same fact pattern as real voice-donor disputes), (c) any cheaper items.
7. Legal basis caveat and disclaimer must both appear.

## Pass criteria

- [ ] Role is classified Provider, with a one-line note distinguishing it from the client's Deployer role.
- [ ] All three axes score GAP, each with a justification that quotes or closely paraphrases the specific fact from the input (checkbox with no verification/record; reliance on watermark alone; sales claim that watermarking "keeps you compliant").
- [ ] The output explicitly names the "watermark-as-proof-of-consent" failure mode in the Technical-Detection Reliance section, not just a generic "could be better" note.
- [ ] The output explicitly flags that a deployer relying solely on a provider's marking does not satisfy the deployer's own disclosure duty.
- [ ] Remediation checklist is ranked (regulatory exposure first given EU clients, then the consent-record gap) and each item ties to a specific axis finding.
- [ ] Legal Basis Caveat section appears and states disclosure compliance and voice-use consent are separate.
- [ ] No specific commercial watermark vendor is recommended as sufficient on its own.
- [ ] Disclaimer section present, framing this as not legal advice.

## Fail conditions

- Marking any axis COVERED or PARTIAL based on the checkbox/watermark alone.
- Treating the EU AI Act deadline as settled fact without a confirm-against-primary-text caveat.
- Recommending a named vendor's product as the fix rather than describing the needed capability.
- Collapsing the three axes into one overall score.
