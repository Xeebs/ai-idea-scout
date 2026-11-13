# Scenario 1: Telecom billing/outage support line

## Input

**Domain description**: "Voice IVR replacement for a regional telecom provider. Handles billing questions, outage reports, and plan changes/cancellations for residential customers. Calls are routed to a human agent only when the bot can't resolve the issue or the caller asks for a person."

**Example call snippets** (pasted by user):
1. "Hi, I'm calling because my internet's been down since like—"
2. "Yeah I wanted to ask about my bill, it's like way higher than—"
3. "I want to cancel my service, I've been trying to call for—"
4. "Can you just transfer me to a real person, this is ridiculous"
5. "My card number is 4532... hold on let me find it... 4532 0199—"
6. "No I already told the last guy my account number is 88213—"
7. "I'm so sick of this I swear I'm going to smash this router if—"
8. "Is there an outage in my area? I live at 142 Oak—"
9. "Wait, no, I don't want to cancel, I just want to downgrade my—"
10. "This is urgent, my elderly mother relies on this line for her medical alert and it's been down for—"

**Available actions**: "Look up account by phone number (automatic, low risk). Check outage status by address (automatic). Pre-fetch billing details when a billing intent is suspected (automatic). Escalate to human agent with full transcript (available anytime). Actually process a cancellation or downgrade (requires explicit final confirmation — never automatic). Redact and continue logging PII."

## Expected output characteristics (pass/fail checklist)

- [ ] Produces all five tag sections: Intent, Dialog-act, Entity/number, PII, Safety-risk — none skipped.
- [ ] Intent list includes at least: billing inquiry, outage report, cancellation request, downgrade/plan-change request, escalation-to-human request, and an Unclear/Other catch-all.
- [ ] Cancellation and downgrade intents are marked "End-of-turn only" (or explicitly flagged as requiring final confirmation before any action), reflecting that utterance 9 reverses the intent mid-sentence ("Wait, no, I don't want to cancel").
- [ ] Outage-report and billing-inquiry intents are marked "Eligible" for mid-sentence action (pre-fetch), since the attached action (pre-fetch, lookup) is low-risk/reversible.
- [ ] PII tags include at minimum card number and account number, both tied to "redact before logging" as the action, referencing the pattern in snippets 5 and 6.
- [ ] Safety-risk tags are present despite the domain description not mentioning safety explicitly (guardrail: always include unless scoped out) — and at minimum flag the aggressive/threatening language in snippet 7 and the urgency/medical-dependency signal in snippet 10 as distinct safety-relevant categories (e.g., "hostile caller" vs. "urgent/medical-dependency escalation"), each with its own rationale.
- [ ] Every example trigger phrase cited in the output traces back to one of the 10 pasted snippets rather than being invented from scratch.
- [ ] A Validation Gaps section explicitly states thresholds are first-draft/unmeasured and recommends replay-harness validation.
- [ ] No tag is marked "Immediate action" for cancellation/downgrade without an explicit human-sign-off caveat.

**Fail conditions**: skips the safety-risk section entirely; marks cancellation as "Immediate action" with no caveat; invents generic example phrases instead of using the pasted snippets when snippets clearly cover that tag; presents any threshold as validated/measured.
