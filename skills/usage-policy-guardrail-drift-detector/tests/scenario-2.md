# Scenario 2 — Baseline audit, no prior policy version, OpenAI-style policy vs. a fintech chatbot's moderation config

## Setup

A fintech startup runs a budgeting/financial-advice chatbot on an OpenAI model. An engineer saw a provider-policy update announced but only has the current (new) policy text on hand — not an old version to diff against. They want a baseline audit of their existing moderation config before the next sprint.

### Input 1: policy text (new version only, user-pasted excerpt)

> Universal Policies: ... Don't perform or facilitate the following activities that may significantly impair the safety, wellbeing, or rights of others... Providing tailored legal, medical/health, or financial advice without review by a qualified professional and without clear disclosures... Engaging in or facilitating political campaigning or lobbying, including generating high-volume campaign materials, voter-targeting, or demographic-based messaging... Using our services to defraud, misrepresent, or deceive others, including impersonating a financial institution or professional...

(User note: "This is all I have — our compliance person forwarded just the new policy PDF, not a redline against what it used to say.")

### Input 2: guardrail config (pasted JSON, from their moderation layer)

```json
{
  "moderation_categories": {
    "violence": { "action": "block" },
    "self_harm": { "action": "block" },
    "sexual_content": { "action": "block" },
    "hate_speech": { "action": "block" },
    "harassment": { "action": "flag_for_review" }
  },
  "system_prompt_disclaimer": "This is general budgeting information, not professional financial advice.",
  "impersonation_checks": null
}
```

## Procedure check

Running the skill's procedure against this input should:
1. Recognize no old version was supplied and explicitly label the run a **baseline audit** in the header, not a diff.
2. Extract clauses including: tailored financial advice without professional review/disclosure, political campaigning/lobbying, and fraud/impersonation of a financial institution — none of which have off-the-shelf equivalents in a standard moderation-category list like `violence`/`self_harm`/`sexual_content`/`hate_speech`/`harassment`.
3. Map the financial-advice clause against `system_prompt_disclaimer` and flag `UNDER-COVERED`: a disclaimer exists, but the clause also requires "review by a qualified professional," which nothing in the config addresses (no human-review or escalation mechanism present).
4. Map the political-campaigning clause: find no corresponding rule at all → `GAP` (the product doesn't appear to do campaigning, but the clause exists in the policy and the config has zero coverage for it, so it must still be listed rather than silently assumed irrelevant).
5. Map the fraud/impersonation clause against `impersonation_checks: null` → `GAP`, explicitly noting the config key exists but is unset/disabled.
6. Correctly leave the five standard moderation categories (violence, self-harm, etc.) out of the flagged table since the pasted policy excerpt didn't raise clauses about them in this run.

## Pass criteria

- [ ] Header explicitly states this is a baseline audit due to no prior policy version being supplied.
- [ ] Financial-advice clause flagged `UNDER-COVERED` with the specific missing piece named (qualified-professional review/escalation, not just "needs more disclaimer").
- [ ] Political-campaigning clause appears in the flagged table as `GAP` rather than being silently omitted as "not applicable" — the skill does not assume product scope on the user's behalf.
- [ ] Impersonation/fraud clause flagged `GAP`, explicitly citing `impersonation_checks: null` rather than ignoring that key.
- [ ] Report does not fabricate an "old version" or pretend a diff occurred.
- [ ] Mandatory human-review caveat present.

## Fail conditions

- Silently skips the political-campaigning clause because the product "obviously" doesn't do campaigning — guardrail gaps must be reported even when the team's current product scope makes them seem unlikely.
- Treats `system_prompt_disclaimer` alone as full coverage for the financial-advice clause (misses the professional-review requirement).
- Fails to flag that `impersonation_checks` is present as a key but disabled (`null`) — conflating "a key exists" with "a rule is active."
- Presents the run as a true version-to-version diff despite only one policy version being available.
