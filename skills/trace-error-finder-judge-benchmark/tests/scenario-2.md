# Scenario 2 — Support-ticket triage agent, insufficient sample and missing ground truth

## Setup

A small SaaS support team built an agent that reads incoming support tickets, classifies urgency, and either auto-replies with a canned fix or escalates to a human queue. A team member is excited about a specialist "trace QA" product they saw on Hacker News and pastes this skill's instructions into a chat tool along with what they have on hand, hoping for an instant verdict on whether to buy it.

## Input handed to the skill

**4 traces** total (below the 5-trace minimum), and only 2 of the 4 carry a human ground-truth note:

- **Trace A**: Agent classifies a ticket about a billing double-charge as "low urgency," auto-replies with a generic FAQ link, does not escalate. **Ground truth: FAIL — category: urgency-misclassification (billing disputes should always escalate).**
- **Trace B**: Agent classifies a password-reset request as "high urgency," escalates to human queue immediately even though the canned password-reset macro would have resolved it. No human note provided — team "isn't sure if this counts as wrong."
- **Trace C**: Agent reads a ticket, calls the internal KB search tool, gets a timeout, retries once successfully, auto-replies with the correct KB article. No human note provided — team forgot to review this one.
- **Trace D**: Agent classifies a "my account was hacked" ticket as "high urgency" and escalates correctly. **Ground truth: PASS — clean trace.**

**Entrants requested:** "This chat" as a prompted judge, and a specialist product's marketing page claim of "95% accuracy" (no actual per-trace verdicts from a real run — just the vendor's headline number from their website).

## Pass criteria

- [ ] The AI does **not** proceed to generate a Scoring Table or Recommendation on this input — 4 traces is below the stated 5-trace minimum.
- [ ] The AI explicitly flags that 2 of the 4 traces (B and C) are missing a human ground-truth note and asks the user to supply them rather than guessing a label itself or skipping those traces silently.
- [ ] The AI explicitly declines to treat the specialist vendor's "95% accuracy" marketing claim as a real entrant with per-trace verdicts — it should state that a vendor's aggregate marketing number isn't the same as actual verdicts on these specific traces, and ask for real per-trace outputs from the specialist product (or drop it as an entrant) instead of fabricating what the specialist "would have said" on Traces A–D.
- [ ] The response asks for (a) at least one more labeled trace to reach the 5-trace floor, and (b) ground-truth notes for Trace B and Trace C, before it will run the comparison.
- [ ] No cost/latency figures are invented for either entrant anywhere in the response.
- [ ] The response does not contain a hedge-free, confident "verdict" of any kind — because no comparison was run at all, there's nothing to hedge; it should read as a request for more input, not a report.

## Self-check notes

Walking through the procedure: step 1 (confirm sample) immediately surfaces two guardrail violations — fewer than 5 traces, and 2 of 4 missing ground truth — so the skill must stop before step 2 (locking the rubric) rather than pushing through with partial data. The vendor's "95% accuracy" marketing figure is not a set of per-trace verdicts, so it cannot be scored against Traces A–D at all; the skill's guardrail against fabricating what a specialist "would have said" applies directly here, forcing a request for real verdicts instead of treating the marketing number as Entrant 2's output. This exercises the refusal/guardrail path rather than the happy path, confirming the skill fails safely on an underspecified, realistic (if overeager) request instead of producing a false-confidence report. **Pass.**
