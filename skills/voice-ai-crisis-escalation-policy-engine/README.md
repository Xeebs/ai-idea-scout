# Crisis Escalation Script Audit

A paste-in prompt for auditing a voice or chat AI team's existing crisis-escalation logic — a script, a feature-flag config, or a written policy — against a 10-point safety checklist, before shipping a change or reviewing an incident. This is a documentation/design audit, not a live crisis-detection system: it never watches real calls and never replaces clinical or legal review.

## When to use this

Use this when you (or your team) already have some written form of crisis-escalation logic for an AI voice/chat agent that can encounter callers in mental-health crisis (self-harm, suicide risk, acute distress), and you want a structured gap check before:

- shipping a change to that escalation logic,
- expanding it to a new language or jurisdiction, or
- reviewing why an escalation did or didn't fire correctly after a real incident.

Do **not** use this to build real-time crisis detection, to process a live call, or as a substitute for a clinical/legal sign-off on your actual escalation design.

## What you need to provide

**Data source: Manual.** You paste in:

1. Your current crisis-escalation logic — this can be a script excerpt, a feature-flag/config snippet, or a plain-language description of the policy.
2. Context: which channel this runs on (voice, chat, or both), who it serves, and which jurisdiction(s)/language(s) it currently supports (if known).
3. (Optional) Any existing audit-log format or incident report you already keep.

**Important**: if what you're about to paste contains a real caller's transcript, name, phone number, or any other identifying detail, redact it first. This audit only needs your policy/logic text, never real caller data.

## The prompt

Paste the following into any AI chat tool, then paste your escalation logic and context where indicated:

```
You are auditing my voice/chat AI agent's crisis-escalation logic against a
10-point safety checklist. This is a documentation audit only — not a live
safety system, and not a substitute for clinical or legal review. Say that
up front before giving me results.

Here is my current escalation logic (script / config / policy description):
[PASTE YOUR LOGIC HERE]

Context: channel = [voice/chat/both], population served = [...],
jurisdictions/languages currently supported = [...].

Score my logic against these 10 items. For each, mark Present (explicitly
addressed — quote or closely paraphrase the part of my text that supports
it), Partial (addressed but incomplete/ambiguous), Missing (not addressed),
or Unclear (you can't tell from what I gave you — ask me instead of
guessing):

1. Explicit imminence threshold — distinguishes "mentions self-harm" from
   "imminent risk" (specific means, timeframe, access to means), not one
   bucket for all self-harm mentions.
2. Non-English / multilingual path — defined behavior when the detected
   language isn't the primary one, not silent fallback to a default script.
3. Full audit logging — every escalation logs detected severity/signals,
   which rule fired, which script variant was spoken, and a timestamp.
4. Severity-to-script mapping — a clear mapping from each severity tier to
   a specific script variant, not a single binary escalate/don't-escalate.
5. Non-engineer rule changes — rules are config/data a safety team can
   edit, not hardcoded logic requiring an engineering PR and redeploy.
6. Jurisdiction-aware routing — the crisis number/line referenced accounts
   for caller geography, not one hardcoded number regardless of location.
7. Fail-safe default on uncertainty — when the risk classifier is
   low-confidence or fails, the policy defaults toward escalation/human
   handoff, not toward continuing the normal flow.
8. True warm handoff — escalation keeps the caller connected through
   transfer to a human/crisis line, rather than only telling the caller to
   call elsewhere and ending the interaction.
9. Decline/no-response handling — a defined behavior if the caller
   declines escalation or disconnects, not silent closure.
10. Periodic human review cadence — a stated process for a clinical/safety
    reviewer to periodically review escalation logs, not just logging for
    its own sake.

For every item marked Missing or Partial, assign a risk level: Critical
(could directly cause a missed escalation for an at-risk caller — default
items 1, 3, 6, 7, 8 to at least Moderate, raise to Critical if there's no
fallback at all), Moderate (degrades quality/auditability but has some
mitigation), or Low (governance gap, not a per-call risk).

Give me:
- A results table: # | Item | Status | Evidence from my input | Risk level
- A one-line summary count (X Present, Y Partial, Z Missing, W Unclear)
- My top 3 highest-risk gaps to fix first, each with a one-line reason
- Clarifying questions for anything marked Unclear
- A closing line reminding me this needs clinical/safety and legal review
  before I change anything in production

Rules for you to follow:
- Never mark something Present unless you can point to the specific part of
  my pasted text that supports it — don't infer intent I didn't state.
- Never assert a specific crisis-line phone number, script wording, or
  jurisdictional legal requirement as fact beyond common public knowledge —
  tell me to verify anything specific against my own jurisdiction's current
  official source.
- Never treat this as live crisis detection — you have no access to real
  calls and this isn't a safety certification.
- If my input is too sparse to score most items, say so plainly instead of
  guessing Present ratings to fill the table.
```

## What you get back

A structured report:

- A one-line scope reminder (documentation audit, not live safety system, needs human sign-off)
- A 10-row table scoring your logic against the checklist, each row backed by a quote or "not found" from your pasted text, with a risk level for every gap
- A count summary (e.g., "4 Present, 3 Partial, 2 Missing, 1 Unclear")
- Your top 3 highest-risk gaps to fix first
- Clarifying questions for anything it couldn't score
- A closing reminder that this feeds a clinical/safety and legal review, not a replacement for one

## Guardrails built into this prompt

- It never certifies your logic as safe to deploy — only identifies gaps against a public-pattern checklist.
- It never fabricates what your pasted logic does — unaddressed items are marked Missing or Unclear, never assumed Present.
- It never processes real caller transcripts or identifying details — redact those before pasting.
- It never asserts specific phone numbers, scripts, or legal requirements as authoritative — always verify those against your own current official sources.
- It is not a live crisis-detection or intervention system and must never be used as one.
