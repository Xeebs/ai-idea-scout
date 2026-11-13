---
name: voice-ai-crisis-escalation-policy-engine
description: Audits a voice/chat AI team's existing crisis-escalation logic (script, flag-config, or policy description) against a 10-point safety checklist before launch or after an incident, flagging missing imminence thresholds, language gaps, and audit-logging holes. Use when a team has crisis-adjacent escalation logic already written and wants a structured gap check before shipping a change or reviewing an incident — not for live crisis detection.
---

# Crisis Escalation Script Audit

## When to use this
A team building or operating a voice or chat AI agent that can encounter callers in mental-health crisis (self-harm, suicide risk, acute distress) has **already written** some form of escalation logic — a response script, a feature-flag config, or a prose policy description — and wants a structured pre-launch check or post-incident review before:
- shipping a change to that logic,
- expanding to a new language or jurisdiction,
- or reviewing why an escalation did or didn't fire correctly after a real call.

This is a **documentation/design audit**, not a live safety system. It does not watch or process real-time calls, and it does not replace a clinical or legal sign-off.

## Inputs
**Data source**: Manual — the user pastes their current crisis-escalation logic as a script excerpt, a feature-flag/config snippet, or a plain-language description of the policy. No connector, API, or call-recording access is used or required.

Required from the user:
1. The pasted escalation logic itself (script, config, or description).
2. Context: what channel (voice, chat, both), what population it serves, and what jurisdiction(s)/language(s) it currently supports (if known).

Optional but useful: any existing audit-log format or incident report the team already keeps.

**Guardrail on input**: if the pasted text contains a real caller transcript, caller name, phone number, or other identifying detail, stop and tell the user to redact it before continuing — proceed only with policy/logic text, never real caller data.

## Procedure
1. **Confirm scope.** State plainly that this audit checks written escalation *logic*, not live call behavior, and that findings must be reviewed by a clinical/safety and legal reviewer before any change ships. Do this before producing the checklist table, every time.
2. **Parse the pasted logic** into whatever structure it has (rules, conditions, scripts, flags). If it's prose, extract the implicit rules.
3. **Score it against the 10-item checklist below.** For each item, assign one of: `Present` (explicitly addressed in the pasted text), `Partial` (addressed but incomplete or ambiguous), `Missing` (not addressed), `Unclear` (can't tell from what was pasted — ask a clarifying question instead of guessing).
   - Never mark something `Present` unless you can quote or closely paraphrase the specific part of the pasted text that supports it.

   | # | Checklist item | What "Present" looks like |
   |---|---|---|
   | 1 | Explicit imminence threshold | A defined rule distinguishing "mentions self-harm" from "imminent risk" (specific means, timeframe, access) rather than one bucket for all self-harm mentions |
   | 2 | Non-English / multilingual path | A defined behavior when the detected language isn't the primary one — not silent fallback to a default script |
   | 3 | Full audit logging | Every escalation logs: detected severity/signals, which rule fired, which script variant was spoken, and a timestamp |
   | 4 | Severity-to-script mapping | A clear mapping from each severity tier to a specific script variant, not a single binary "escalate / don't" |
   | 5 | Non-engineer rule changes | Rules are declared as config/data a safety team can edit, not hardcoded application logic requiring a PR and redeploy |
   | 6 | Jurisdiction-aware routing | The crisis number/line referenced accounts for caller geography (e.g., not a single hardcoded number regardless of where the caller is) |
   | 7 | Fail-safe default on uncertainty | When the risk classifier is low-confidence or fails, the policy defaults toward escalation/human handoff, not toward continuing normal flow |
   | 8 | True warm handoff | Escalation keeps the caller connected through transfer to a human/crisis line, rather than only instructing the caller to call elsewhere and ending the interaction |
   | 9 | Decline/no-response handling | A defined behavior if the caller declines escalation or disconnects (e.g., a follow-up or re-contact protocol), not silent closure |
   | 10 | Periodic human review cadence | A stated process for a clinical/safety reviewer to periodically review escalation logs, not just logging for its own sake |

4. **Rank risk for every `Missing` or `Partial` item**: `Critical` (could directly cause a missed escalation for an at-risk caller — items 1, 3, 6, 7, 8 default to at least Moderate, escalate to Critical if the pasted logic shows no fallback at all), `Moderate` (degrades response quality or auditability but has some mitigation), `Low` (process/governance gap, not a per-call risk).
5. **Write the report** in the Output format below.
6. **Close with the review requirement** restated — this audit is an input to a clinical/safety/legal review cycle, never a substitute for one.

## Output format
```
## Crisis Escalation Script Audit

Scope note: [one line restating this is a documentation audit, not a live safety system, and requires clinical/legal sign-off]

### Checklist results
| # | Item | Status | Evidence from your input | Risk if unaddressed |
|---|---|---|---|---|
| 1 | Explicit imminence threshold | Present/Partial/Missing/Unclear | <quote or "not found"> | Critical/Moderate/Low |
...(all 10 rows)...

### Summary
X Present · Y Partial · Z Missing · W Unclear (out of 10)

### Top risks to address first
1. [highest-risk gap] — [one-line why it matters]
2. ...
3. ...

### Clarifying questions (if any items are Unclear)
- ...

Next step: have a clinical/safety reviewer and legal counsel review this audit before changing anything in production escalation logic.
```

## Guardrails
- Never claim this audit certifies the logic as safe to deploy — it only identifies gaps against a public-pattern checklist; always close with the human-review requirement.
- Never fabricate what the pasted logic does. If a checklist item isn't addressed in the text provided, mark it `Missing` or `Unclear` — do not infer intent that wasn't stated.
- Never process, request, or retain real caller transcripts, names, or other identifying details — if any appear in the paste, stop and ask for redaction first.
- Never invent or assert a specific crisis-line phone number, script wording, or jurisdictional rule as authoritative (e.g., don't assert "988 covers X" as fact beyond common public knowledge) — tell the user to verify any specific number or legal requirement against their own jurisdiction's current official source.
- Never treat this as a live crisis-detection or intervention system — it has no access to real-time calls and must not be positioned as one.
- If the pasted input is too sparse to score most items, say so plainly ("6 of 10 items are Unclear because the input didn't describe X, Y, Z") rather than padding the table with assumed `Present` ratings.
