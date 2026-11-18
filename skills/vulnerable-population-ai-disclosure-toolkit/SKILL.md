---
name: vulnerable-population-ai-disclosure-toolkit
description: Drafts the AI-involvement disclosure copy, consent-capture flow, and withdrawal mechanism for a specific decision a product makes about a vulnerable population (disability services, asylum/immigration, elder care, and similar high-stakes individualized decisions). Use when a product or legal/compliance team is about to ship (or retrofit) an AI-assisted matching, eligibility-screening, risk-flagging, or triage decision affecting a vulnerable population and has no existing disclosure language to reuse.
---

# Plain Disclosure: Vulnerable-Population AI Disclosure & Consent Drafting Aid

## When to use this
A product manager, legal/compliance reviewer, or engineer on a team building (or already shipping) an AI-assisted decision about a vulnerable population — a disability-support matching tool, an asylum/immigration case-triage or translation system, an elder-care risk-flagging tool, or a similar individualized-decision product — needs disclosure copy, a consent-capture sequence, and a withdrawal mechanism, and has nothing to reuse yet. Reach for this skill at that exact moment: the decision logic exists or is being built, but the "tell the affected person an AI was involved, and let them act on that" layer hasn't been drafted.

Do NOT use this for: writing or reviewing the underlying AI decision logic itself, generating a general-purpose website AI-content disclaimer (e.g. "this blog post was AI-assisted") unrelated to an individualized decision about a person, conducting the actual jurisdiction-specific legal review a licensed professional must do, or building the installable UI component library — this skill only drafts the text and flow; it does not ship code or confer legal sign-off.

## Inputs
**Data source**: Manual — the requester pastes a description of the AI-mediated decision (what the AI does, e.g. "ranks candidate support workers by compatibility with a participant's stated preferences and support needs"), the population it affects (e.g. "NDIS disability-support participants in Australia"), the jurisdiction(s) involved, and what categories of data the AI used to make the decision. No external system, API, or connector is read — this is a one-shot drafting aid configured entirely from what the user hands it at invocation time.

Required, per decision:
1. **Decision type and description** — what the AI actually does in plain terms (matching, eligibility screening, risk flagging, triage/translation, or "other" with a one-sentence description).
2. **Population** — who is affected (e.g. "asylum applicants with pending USCIS cases," "NDIS participants," "assisted-living residents").
3. **Jurisdiction(s)** — country/state/region the product operates in, since disclosure obligations vary (e.g. Washington's My Health My Data Act, EU AI Act transparency obligations, NDIS Quality and Safeguards Commission rules).
4. **Data used** — what categories of information the AI drew on to make the decision (e.g. "stated support preferences, prior incident reports, geographic availability").

Optional, if the requester has it: any specific statute or regulation they already know applies, the organization's existing severity/risk tiering, prior ad hoc disclosure language already in use that needs replacing.

## Procedure
1. **Classify the decision type.** Match the description to one of: matching, eligibility screening, risk flagging, triage/translation, or "other individualized decision." If "other," say so explicitly rather than forcing a poor fit into one of the four named categories.
2. **Name the jurisdiction obligation, or flag it as unverified.** If the requester named a specific statute, restate what it requires in one sentence. If no statute was named, state plainly: "No specific disclosure statute confirmed for this jurisdiction — verify with jurisdiction-specific legal counsel before shipping; drafting proceeds using general informed-consent best practice as a placeholder." Never invent or assert a statute citation that wasn't given or that the skill isn't certain of.
3. **Draft the plain-language disclosure panel.** Write what the AI did, using the word "AI" or "automated system" explicitly — never a euphemism like "advanced analysis" or "smart matching" that obscures that AI was involved. State: what decision it affected, what data it used, and that a human remains available to review it. Target a reading level appropriate to a general adult audience with no technical background (short sentences, no jargon, define any term that can't be avoided).
4. **Draft the consent-capture sequence as discrete steps**, not a single click-through: (a) the disclosure panel is shown and must be read/scrolled before (b) an explicit opt-in action (not a pre-checked box), followed by (c) a confirmation step repeating what was agreed to in one sentence.
5. **Draft the withdrawal mechanism.** Write the exact copy for how the person withdraws consent (e.g. "You can ask \[org\] to stop using AI in your case review at any time — contact \[channel\] and no AI-based decision will be used for your case going forward") and describe what happens procedurally after withdrawal (what the fallback process is, in plain terms). The withdrawal path must be no harder to find or complete than the opt-in was.
6. **Run a dark-pattern self-check** against the draft and report the result as a checklist: withdrawal path is not buried deeper than the opt-in; no guilt/loss-framing language ("you'll lose your matching priority if you opt out"); no pre-checked consent boxes; disclosure text appears before, not after, the consent action. Flag and fix any item that fails before presenting the final draft.
7. **Close with a legal-review banner.** Every output states plainly that this is an unreviewed draft and must go through jurisdiction-specific legal review before use in production — never imply the draft is compliance-ready as delivered.

## Output format
```
⚠️ DRAFT — unreviewed; requires jurisdiction-specific legal review before production use.

## Decision Summary
**Type**: <matching | eligibility screening | risk flagging | triage/translation | other>
**Population**: <as given>
**Jurisdiction(s)**: <as given>
**Legal basis**: <restated statute, or the "no statute confirmed" flag from step 2>

## Disclosure Panel Copy
<the plain-language "what the AI did" text>

## Consent-Capture Sequence
1. <disclosure shown / read-before-continue step>
2. <explicit opt-in action, not pre-checked>
3. <confirmation step copy>

## Withdrawal Mechanism
**Copy**: <exact withdrawal-path text>
**Process after withdrawal**: <what happens next, in plain terms>

## Dark-Pattern Self-Check
- [ ] Withdrawal path is as easy to find/complete as the opt-in
- [ ] No guilt/loss-framing language
- [ ] No pre-checked consent boxes
- [ ] Disclosure shown before, not after, the consent action
(each item marked pass with one-line justification, or flagged with the fix applied)

## Legal Review Flag
<explicit statement that this draft requires jurisdiction-specific legal sign-off before use>
```

## Guardrails
- Never state or imply legal review has occurred — the output is always a draft pending jurisdiction-specific legal sign-off, every time, with no exceptions.
- Never invent a specific statute, regulation, or citation that wasn't supplied and that the skill isn't certain of; say explicitly that it's unconfirmed and should be verified.
- Never use a euphemism for "AI" or "automated system" in the disclosure copy — the whole point is that the affected person understands an AI was involved.
- Never draft a consent mechanism that is a single "I Agree" click-through with no preceding explanation step, and never pre-check a consent box in the drafted flow.
- Never draft a withdrawal mechanism that is harder to find, slower, or more burdensome than the original opt-in — if the self-check fails this, fix the draft before presenting it, don't present it with the flaw noted and unfixed.
- Never draft generic website/blog AI-content disclaimers under this skill — it is scoped specifically to individualized decisions about a named vulnerable population, not general AI-use disclosure.
- Never fabricate population size estimates, engagement statistics, or adoption numbers in the output — this skill drafts copy and flow, not evidence.
