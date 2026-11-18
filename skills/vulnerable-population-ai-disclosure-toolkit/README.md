# Plain Disclosure: Vulnerable-Population AI Disclosure & Consent Drafting Aid

A paste-in prompt for product managers, legal/compliance reviewers, or engineers building an AI-assisted decision about a vulnerable population — a disability-support matching tool, an asylum/immigration case-triage or translation system, an elder-care risk-flagging tool, or any similar individualized decision about a person in a high-stakes category. It drafts the disclosure copy, the consent-capture sequence, and the withdrawal mechanism for that specific decision — the layer that tells the affected person an AI was involved and lets them act on that, which most teams in this space are currently deriving from scratch, ad hoc, with no shared starting point.

This is not a legal-review service and not an installable UI component library. It drafts text and a flow for a human to review, edit, and route through real jurisdiction-specific legal sign-off before anything ships.

## When to use this
Use it the moment your team has (or is building) an AI-mediated decision affecting a vulnerable population — matching, eligibility screening, risk flagging, or triage/translation — and needs disclosure/consent/withdrawal language and has nothing to reuse yet. Don't use it to write the underlying AI decision logic, to generate a generic "this blog post was AI-assisted" disclaimer, to replace an actual legal review, or to get installable code — it only drafts the words and the step sequence.

## What to paste in

Copy this prompt into any AI chat tool (Claude, ChatGPT, etc.), then fill in the bracketed sections with your own case:

```
You are drafting AI-involvement disclosure copy, a consent-capture sequence, and a withdrawal mechanism for one specific AI-mediated decision about a vulnerable population. Follow this procedure exactly:

1. Classify the decision type as one of: matching, eligibility screening, risk flagging, triage/translation, or "other individualized decision" (say so explicitly if it's "other" rather than forcing a poor fit).

2. State the jurisdiction's disclosure obligation in one sentence if I named a specific statute. If I didn't name one, say plainly: "No specific disclosure statute confirmed for this jurisdiction — verify with jurisdiction-specific legal counsel before shipping; drafting proceeds using general informed-consent best practice as a placeholder." Never invent a statute citation I didn't give you and you aren't certain of.

3. Draft a plain-language disclosure panel: what the AI did, using the word "AI" or "automated system" explicitly (never a euphemism like "advanced analysis" or "smart matching"), what decision it affected, what data it used, and that a human remains available to review it. Write for a general adult reader with no technical background — short sentences, no unexplained jargon.

4. Draft the consent-capture sequence as three discrete steps, not one click-through: (a) the disclosure panel must be shown/read before (b) an explicit opt-in action with no pre-checked box, followed by (c) a confirmation step that restates what was agreed to in one sentence.

5. Draft the withdrawal mechanism: the exact copy for how the person withdraws consent, and what happens procedurally afterward (the fallback process, in plain terms). The withdrawal path must be no harder to find or complete than the opt-in was.

6. Run a dark-pattern self-check on your own draft and report it as a checklist: withdrawal path as easy as the opt-in; no guilt/loss-framing language; no pre-checked boxes; disclosure shown before the consent action. If anything fails, fix it before showing me the final draft — don't show me a flaw you noticed and left in.

7. Close every output with a banner stating this is an unreviewed draft requiring jurisdiction-specific legal sign-off before production use. Never imply it's compliance-ready as delivered.

Output format:

⚠️ DRAFT — unreviewed; requires jurisdiction-specific legal review before production use.

## Decision Summary
**Type**: <classification>
**Population**: <as given>
**Jurisdiction(s)**: <as given>
**Legal basis**: <restated statute, or the unconfirmed-statute flag>

## Disclosure Panel Copy
<text>

## Consent-Capture Sequence
1. <step>
2. <step>
3. <step>

## Withdrawal Mechanism
**Copy**: <text>
**Process after withdrawal**: <text>

## Dark-Pattern Self-Check
- [ ] Withdrawal as easy as opt-in
- [ ] No guilt/loss-framing language
- [ ] No pre-checked boxes
- [ ] Disclosure shown before consent action

## Legal Review Flag
<statement>

Here is my case:
- What the AI does: [fill in, plain terms]
- Population affected: [fill in — who, specifically]
- Jurisdiction(s): [fill in — country/state/region]
- Data the AI used: [fill in — categories of information]
- Known applicable statute, if any: [fill in, or write "none known"]
- Any existing ad hoc disclosure language to replace: [optional, paste it]
```

## What you get back
A single structured draft opening with the unreviewed-draft banner, containing: the decision classification, the jurisdiction's legal basis (or an explicit flag that none was confirmed), the disclosure panel copy, a three-step consent sequence, withdrawal copy plus the post-withdrawal process, a completed dark-pattern self-check, and a closing legal-review flag. If you don't know the applicable statute, you still get a usable draft — it's just explicitly marked as resting on general informed-consent practice instead of a confirmed legal citation.

## Guardrails (the AI should refuse or flag, not improvise past these)
- It should never claim or imply legal review has happened — every output is a draft pending real jurisdiction-specific sign-off.
- It should never invent a statute or citation you didn't give it and it isn't certain of.
- It should never use a euphemism for "AI" or "automated system" in the disclosure text.
- It should never draft a single "I Agree" click-through with no explanation step first, and never pre-check a consent box.
- It should never leave the withdrawal path harder to find or complete than the opt-in — if its own self-check flags that, it should fix the draft, not just note the flaw.
- It should never draft a generic website/blog AI-content disclaimer under this prompt — it's scoped to individualized decisions about a named vulnerable population.
- It should never invent population size, engagement, or adoption numbers — it drafts copy and flow only.
