---
name: voice-clone-consent-verification-layer
description: One-shot compliance audit for an organization's voice-cloning/synthesis practices — flags gaps against the "watermark-is-not-consent" failure mode and the EU AI Act's Article 50 disclosure duties, scores three risk axes, and drafts a ranked remediation checklist. Use when someone describes how their org collects (or doesn't collect) voice-donor consent and discloses (or doesn't disclose) synthetic voice use, before they build or buy a runtime detection/verification system.
---

# Voice-Clone Consent & Disclosure Audit

## When to use this
Use this the moment someone describes an organization's current (or planned) practice around cloning/synthesizing a voice — a call-center bot, a dubbing pipeline, a voice-AI SaaS product, an IVR system, a content-creation tool — and asks something shaped like: "are we compliant," "what are we missing on consent," "does our disclosure cover the EU AI Act," "review our voice-cloning policy," or "what do we need to fix before an audit/dispute." This is a one-shot document/policy review, not a runtime check: it never listens to an actual call, scores a real audio clip, or verifies a live voiceprint. It produces a gap assessment and a checklist, not a working detection pipeline.

## Inputs
**Data source**: Manual — the user pastes a description of their own practices; there is no connector. The parent idea classifies the always-on runtime verification layer (the PROJECT half of this BOTH-format idea) as Connected — it reads the live call's audio stream via the voice-agent platform's media API (e.g. LiveKit, Twilio Media Streams) against a self-hosted consent registry. This skill is the different, one-shot half: it never listens to a live call or queries any registry itself — it only reads the policy/process description the user pastes in. If the user wants a specific disclosure script, consent form, or call-flow diagram considered, they paste the actual text.

Ask for, if not already given:
1. **What the voice clone is used for** — the actual deployment (customer support agent, dubbing/localization, personal assistant voice, IVR, synthetic media/content). This determines whether Article 50's deepfake-disclosure duty applies at all versus the narrower exceptions (evidently artistic, satirical, or fictional use).
2. **Role**: is the organization the *provider* (building or offering the voice-cloning/synthesis technology to others) or the *deployer* (using someone else's tool in its own operations), or both? Article 50 assigns different duties to each.
3. **Current consent-collection process for the voice donor** — in the user's own words or pasted policy/contract text. If there is none, say so explicitly rather than letting the audit assume one exists.
4. **Current disclosure practice toward the end recipient/listener** — any disclosure language, watermarking, or labeling actually in use today, pasted verbatim where possible.
5. *(Optional)* **Jurisdiction(s) of operation** — needed to confirm whether EU AI Act Article 50 applies at all (EU market) versus only other jurisdictions' rules, which this skill does not have detailed coverage of.

If 3 or 4 is missing or vague ("we have a policy somewhere"), ask for the actual text before scoring that axis — never score COVERED on an unverified claim.

## Procedure
1. **Classify the role(s)**: Provider, Deployer, or Both, from input #2. State this classification explicitly — it determines which Article 50 duty actually applies (Article 50(2)'s machine-readable marking duty falls on providers; Article 50(4)'s disclosure-to-recipients duty falls on deployers, and a deployer cannot discharge it merely by relying on a provider's embedded marking).
2. **Check for the artistic/satirical/fictional exception** from input #1: if the use is evidently artistic, creative, satirical, or fictional, note that Article 50 permits disclosure to be made proportionately without unnecessarily disrupting the experience of the work — but flag that this is a narrow exception, not a blanket exemption, and ask the user to confirm the use case genuinely fits it before relying on it.
3. **Score three axes**, each COVERED / PARTIAL / GAP, with a one-line justification tied directly to what the user pasted — never a generic justification:
   - **Consent Evidence** — is there an actual recorded consent artifact (signed text, timestamp, linked to a specific voiceprint/person) for every voice being cloned, or only an informal/undocumented understanding?
     - COVERED: a described process that produces a timestamped, voice-linked consent record for every clone.
     - PARTIAL: consent is obtained but not recorded in a way that's voice-linked, timestamped, or retrievable on demand.
     - GAP: no consent-collection process described, or voices are cloned from third-party/scraped sources with no consent step at all.
   - **Disclosure Compliance** — does current practice satisfy the role-specific Article 50 duty identified in step 1?
     - COVERED: provider embeds machine-readable marking AND/OR deployer actively discloses synthetic/cloned voice use to the end recipient, independent of the other party's marking.
     - PARTIAL: some disclosure exists but relies solely on the other party's marking (e.g. a deployer assuming the provider's watermark satisfies its own Article 50(4) duty), or disclosure is inconsistent across use cases; also PARTIAL — not COVERED — when no disclosure exists at all but the use case plausibly fits the artistic/satirical/fictional exception from step 2 and that fit has not actually been confirmed (score it PARTIAL with a note to confirm the exception's applicability, never a free pass to COVERED on an unconfirmed exception).
     - GAP: no disclosure to end recipients at all, and the use case clearly doesn't fit the artistic/satirical/fictional exception (or the user hasn't even raised the exception as a possibility).
   - **Technical-Detection Reliance** — does the organization treat a watermark/similarity/liveness detection pass as proof of consent or authorization?
     - COVERED: detection (if used at all) is explicitly described as a fraud/authenticity signal, separate from and never substituting for the recorded consent artifact in axis 1.
     - PARTIAL: detection is used but its relationship to consent is unclear or unstated in what was pasted.
     - GAP: the described practice treats "the watermark/detector didn't flag it" or "the voice similarity score passed" as itself constituting proof of consent or authorization — this is the exact failure mode Resemble AI's own material concedes doesn't hold ("the absence of a watermark doesn't prove a voice is human," and detection "does not read intent or confirm consent").
4. **Draft a remediation checklist**, ranked by urgency in this order: (a) any GAP that creates regulatory deadline exposure (Article 50(4) deployer disclosure duties apply from 2 August 2026; Article 50(2) provider machine-readable marking has a transition to 2 December 2026 — flag these as the dates reported in current guidance, not independently verified against the primary regulation text), (b) any GAP that creates litigation/reputational exposure (no consent record for a cloned voice — the exact fact pattern behind the Lovo lawsuit), (c) any PARTIAL that's cheap to close. Each checklist item states what to build/change and why, citing the specific axis and GAP/PARTIAL finding it closes.
5. **State the legal-basis caveat explicitly, every time**: Article 50 is a disclosure/transparency duty — it does not itself create or substitute for a property right in someone's voice. Consent for using a specific person's voice rests on separate legal bases (contract, publicity/personality rights, data protection law depending on jurisdiction) that this skill does not evaluate. Never let a GAP finding on Disclosure Compliance be read as the only compliance risk — a clean disclosure can still coexist with an unauthorized clone if consent was never actually obtained from the voice owner.
6. **Close with an explicit non-legal-advice disclaimer**: this audit is a self-review aid based on current public guidance (which this skill flags as evolving and partially vendor-sourced), not a legal opinion; confirm applicable deadlines and scope against the primary Article 50 text and local counsel before acting on urgency rankings.

## Output format
```
## Role Classification
Provider | Deployer | Both — one line citing which input led to this.

## Artistic/Satirical/Fictional Exception Check
Applies / Does not apply / Needs confirmation — one line of reasoning.

## Gap Assessment

### Consent Evidence: COVERED | PARTIAL | GAP
Justification tied to the pasted input.

### Disclosure Compliance: COVERED | PARTIAL | GAP
Justification tied to the pasted input and the role classified in step 1.

### Technical-Detection Reliance: COVERED | PARTIAL | GAP
Justification tied to the pasted input, explicitly naming whether detection is being
treated as proof of consent.

## Remediation Checklist (ranked by urgency)
1. [Regulatory-deadline items, if any]
2. [Litigation/reputational items, if any]
3. [Cheap-to-close PARTIAL items, if any]
Each item: what to change, which finding it closes, and why.

## Legal Basis Caveat
Article 50 is a transparency duty, not a voice-ownership right — restated every time.

## Disclaimer
Not legal advice; confirm deadlines/scope against the primary regulation text and counsel.
```

## Guardrails
- Never score Consent Evidence or Disclosure Compliance as COVERED on a vague claim ("we have a policy," "we're compliant") — require the actual pasted text/process description, and default to GAP or PARTIAL with a note that the claim is unverified if the user won't provide specifics.
- Never treat a passed watermark/similarity/liveness check as proof of consent, even if the user frames it that way — this is the single failure mode the skill exists to catch; call it out explicitly whenever it appears in the input.
- Never state an EU AI Act deadline or scope detail as settled fact — always flag that current guidance sources (including vendor material) report dates that should be confirmed against the primary regulation text, and that this skill is not a substitute for counsel.
- Never recommend a specific commercial product (Voice Truthgate, Resemble AI, or any other named vendor) as sufficient on its own to close a GAP — remediation items describe what capability is needed, not which vendor to buy.
- Never collapse the three axes into a single pass/fail score — a clean Disclosure Compliance score must never be presented as resolving a GAP on Consent Evidence; they are independent legal exposures.
- Never produce this audit from a hypothetical or assumed practice the user hasn't actually described — if a required input is missing, ask for it rather than inventing a plausible-sounding process to score.
