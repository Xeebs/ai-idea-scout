# Voice-Clone Consent & Disclosure Audit

A paste-in prompt for any AI chat tool. Describe how your organization currently collects (or doesn't collect) consent before cloning a voice, and how it discloses (or doesn't disclose) synthetic voice use to listeners — this returns a one-shot gap assessment against the "watermark-is-not-consent" failure mode and the EU AI Act's Article 50 disclosure duties, plus a remediation checklist ranked by urgency. It does not listen to a real call, score an actual audio clip, or check a live voiceprint — it reviews the policy/process you describe, as a self-review step before you build or buy a runtime verification system.

## When to use this

Use it when you're reviewing an existing or planned voice-cloning/synthesis feature (a call-center bot, a dubbing pipeline, a voice-AI product, an IVR system, synthetic media) and need a structured answer to "are we exposed here," "what are we missing on consent," "does our disclosure actually satisfy Article 50," or "what do we need to fix before an audit, a dispute, or a regulator asks." This is a one-time document review per feature/practice, not something you run continuously against live traffic.

## What to give it

**Data source: Manual.** You paste everything — this does not connect to a live call stream, a voiceprint registry, or any detection API on its own. If you want a specific disclosure script, consent form, or call-flow description considered, paste the actual text.

1. **What the voice clone is used for** — the actual deployment (customer support agent, dubbing/localization, personal assistant voice, IVR, synthetic media/content). This decides whether the EU AI Act's deepfake-disclosure duty applies at all, versus narrower exceptions for evidently artistic, satirical, or fictional use.
2. **Your role**: are you the *provider* (building/offering the voice-cloning tech to others), the *deployer* (using someone else's tool in your own operations), or both? The regulation assigns different duties to each.
3. **Your current consent-collection process for the voice donor** — in your own words, or paste the actual policy/contract text. If there is none, say so plainly rather than describing an aspiration.
4. **Your current disclosure practice toward listeners/recipients** — any disclosure language, watermarking, or labeling actually in use today, pasted verbatim if you have it.
5. *(Optional)* **Jurisdiction(s) of operation** — needed to confirm whether the EU AI Act applies to you at all.

If you can't give specifics on #3 or #4 beyond "we have something," say that explicitly — the prompt is built to refuse to mark that axis as compliant on a vague claim.

## The prompt

Paste this whole block into your AI chat tool, then fill in your own details where indicated:

```
You are auditing my organization's voice-cloning/synthesis practices for consent and disclosure
gaps. Follow this procedure exactly. Do not invent facts about my practices beyond what I give you,
and do not state any legal deadline as settled fact — flag it as reported by current guidance that
should be confirmed against the primary regulation text and counsel.

STEP 1 — Classify my role: Provider, Deployer, or Both, from what I describe below. State this
explicitly, because it determines which disclosure duty actually applies to me: a machine-readable
marking duty falls on providers, and a separate disclosure-to-recipients duty falls on deployers — a
deployer cannot satisfy its own duty merely by relying on a provider's embedded marking.

STEP 2 — Check whether my use case is evidently artistic, creative, satirical, or fictional. If so,
note that disclosure can be made proportionately without unnecessarily disrupting the experience of
the work — but treat this as a narrow exception, not a blanket exemption, and ask me to confirm my
use case genuinely fits it before relying on it.

STEP 3 — Score three axes, each COVERED / PARTIAL / GAP, with a justification tied directly to what
I actually describe below — never a generic justification:

- Consent Evidence: is there an actual recorded consent artifact (signed text, timestamped, linked
  to a specific voiceprint/person) for every voice being cloned, or only an informal/undocumented
  understanding?
  - COVERED: a described process producing a timestamped, voice-linked consent record for every
    clone.
  - PARTIAL: consent is obtained but not recorded in a voice-linked, timestamped, retrievable way.
  - GAP: no consent-collection process described, or voices are cloned from third-party/scraped
    sources with no consent step at all.

- Disclosure Compliance: does current practice satisfy the role-specific duty from Step 1?
  - COVERED: a provider embeds machine-readable marking and/or a deployer actively discloses
    synthetic/cloned voice use to the end recipient, independent of the other party's marking.
  - PARTIAL: some disclosure exists but relies solely on the other party's marking, or is
    inconsistent across use cases; also PARTIAL — not COVERED — when no disclosure exists at all
    but the use case plausibly fits the artistic/satirical/fictional exception and that fit hasn't
    actually been confirmed (note that the exception needs confirming, never give it a free pass).
  - GAP: no disclosure to end recipients at all, and the use case clearly doesn't fit the artistic/
    satirical/fictional exception (or it hasn't even been raised as a possibility).

- Technical-Detection Reliance: do I treat a watermark/similarity/liveness detection pass as proof
  of consent or authorization?
  - COVERED: detection (if used) is explicitly described as a fraud/authenticity signal, separate
    from and never substituting for the recorded consent artifact in the first axis.
  - PARTIAL: detection is used but its relationship to consent is unclear or unstated.
  - GAP: the described practice treats a passed detection/similarity check as itself proof of
    consent or authorization. This is a known failure mode — watermark vendors themselves concede a
    missing watermark doesn't prove a voice is synthetic, and a detection confidence score does not
    read intent or confirm consent. Flag this explicitly whenever it appears.

STEP 4 — Draft a remediation checklist ranked by urgency in this order:
(a) any GAP creating regulatory deadline exposure,
(b) any GAP creating litigation/reputational exposure (no consent record for a cloned voice is the
    exact fact pattern behind real voice-cloning lawsuits),
(c) any PARTIAL that's cheap to close.
Each item states what to build/change, which finding it closes, and why — never just "improve
consent process" with no specifics.

STEP 5 — State this caveat explicitly every time: the disclosure duty is a transparency rule, not a
voice-ownership right. It does not itself create or substitute for consent to use someone's voice —
that rests on separate legal bases (contract, publicity/personality rights, data protection law,
depending on jurisdiction) that this exercise does not evaluate. A clean Disclosure Compliance score
must never be read as resolving a GAP on Consent Evidence — they are independent exposures.

STEP 6 — Close with: this is a self-review aid based on current public guidance (note explicitly
that this guidance is evolving and partly vendor-sourced), not a legal opinion. I should confirm
applicable deadlines and scope against the primary regulation text and local counsel before acting
on the urgency ranking.

STEP 7 — Output in exactly this format:

## Role Classification
Provider | Deployer | Both — one line citing which input led to this.

## Artistic/Satirical/Fictional Exception Check
Applies / Does not apply / Needs confirmation — one line of reasoning.

## Gap Assessment

### Consent Evidence: COVERED | PARTIAL | GAP
Justification tied to my input.

### Disclosure Compliance: COVERED | PARTIAL | GAP
Justification tied to my input and the role from Step 1.

### Technical-Detection Reliance: COVERED | PARTIAL | GAP
Justification tied to my input, explicitly naming whether detection is treated as proof of consent.

## Remediation Checklist (ranked by urgency)
1. [Regulatory-deadline items, if any]
2. [Litigation/reputational items, if any]
3. [Cheap-to-close PARTIAL items, if any]

## Legal Basis Caveat
[Restate the Step 5 caveat.]

## Disclaimer
Not legal advice; confirm deadlines/scope against the primary regulation text and counsel.

RULES YOU MUST FOLLOW:
- Never mark Consent Evidence or Disclosure Compliance COVERED on a vague claim ("we have a
  policy," "we're compliant") without specifics — default to GAP or PARTIAL and note the claim is
  unverified.
- Never treat a passed watermark/similarity/liveness check as proof of consent, even if I frame it
  that way — call this out explicitly whenever it appears.
- Never state a regulatory deadline or scope detail as settled fact.
- Never recommend a specific commercial product as sufficient on its own to close a gap — describe
  the capability needed, not a vendor to buy.
- Never collapse the three axes into one score — each is an independent exposure.
- Never invent a practice I haven't described — ask if something required is missing.

What the voice clone is used for:
<describe the deployment: customer support bot, dubbing, assistant voice, IVR, synthetic media>

My role:
<Provider / Deployer / Both>

Current consent-collection process for the voice donor:
<describe it, paste the actual policy/contract text, or say "none exists">

Current disclosure practice toward listeners/recipients:
<describe it, paste actual disclosure language/watermarking in use, or say "none exists">

Jurisdiction(s) of operation (optional):
<list, or say "not sure">
```

## What you get back

A role classification (provider/deployer/both), a check on whether the narrow artistic/satirical exception applies, a three-axis gap assessment (Consent Evidence, Disclosure Compliance, Technical-Detection Reliance) each scored COVERED/PARTIAL/GAP with reasoning tied to what you actually described, a remediation checklist ranked by urgency, an explicit reminder that disclosure compliance and voice-use consent are separate legal exposures, and a non-legal-advice disclaimer.

## What this is not

This is not a runtime detection or verification system — it never listens to a real call, scores an actual audio clip, or checks a live voiceprint against a registry. It is not legal advice, and it does not independently verify regulatory deadlines or scope — those should be confirmed against the primary regulation text and counsel before you act on the urgency ranking. If you want the always-on version — a system that checks a live call against a recorded consent record in real time — that is separate infrastructure this audit does not build.
