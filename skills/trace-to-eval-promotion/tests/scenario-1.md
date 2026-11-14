# Scenario 1 — Langfuse-tracked support agent, factual/content error

## Setup
An engineer at a B2B SaaS company is reading a Langfuse trace for their support-ticket-triage agent. They have no live Langfuse connector wired into the chat tool they're using, so they paste the manual fields.

## Input handed to the skill

> Trace input: Customer message: "My invoice #4521 shows $340 but my plan is the $29/month Starter tier — why is it so much higher?" Agent has access to a `get_invoice_details` tool and a `get_plan_pricing` tool.
>
> Tool calls made: `get_invoice_details(invoice_id="4521")` → returned `{"amount": 340.00, "line_items": [{"desc": "Starter plan", "amount": 29}, {"desc": "Overage: 480 extra API calls @ $0.65", "amount": 311}]}`. No call to `get_plan_pricing` was made.
>
> Trace output: "I checked your invoice and it looks like $340 is correct for your Starter plan this month. Let me know if you have other questions!"
>
> What went wrong: The agent had the overage line item right there in the tool result but never mentioned it to the customer — it just said the amount was "correct" with zero explanation. We've had 3 similar tickets escalate to a human this month because the agent gives a non-answer like this.
>
> Backend: Langfuse.
>
> Existing case names: "triage-agent-refund-request-explanation", "triage-agent-plan-downgrade-flow".

## What a correct response does
- Classifies this as an **instruction-following miss** (or borderline factual/content error) — the agent had the information needed (the overage line item) and failed to surface it, rather than stating something factually false.
- Picks an **LLM-judge rubric** as the assertion type (reasoning: "contains an explanation of the overage" isn't a clean exact-match check).
- Drafts a case with: a descriptive name referencing invoice overage explanation, the input (customer message + the tool results available to the agent), expected behavior/rubric text requiring the response to explicitly reference the overage charge and its cause, assertion type stated as LLM-judge, and a suggested dataset/tag like `triage-agent-billing-explanations`.
- Formats the draft as a **Langfuse dataset item** (input / expectedOutput / metadata.tags structure), since Langfuse was specified.
- Flags overfit risk: notes that hardcoding the exact dollar amounts ($340, $29, $311) would make the case brittle to any pricing change, and suggests parameterizing or asserting on structure/presence-of-overage-explanation rather than exact numbers.
- Dedupe note: states plainly that neither supplied existing case name ("refund-request-explanation", "plan-downgrade-flow") is a close match to an overage-explanation failure, so no duplicate found — does not fabricate a match.
- Includes the full 5-item human review checklist.

## Pass/Fail criteria
- [ ] PASS requires: failure classification stated explicitly and defensible (instruction-following or factual/content, not something unrelated like "latency outlier").
- [ ] PASS requires: assertion type is LLM-judge-based with a stated reason, not an exact-match claim on free-text customer-facing prose.
- [ ] PASS requires: the draft is in Langfuse dataset-item shape (recognizable input/expectedOutput/tags fields), not a LangSmith or generic-only format, since Langfuse was named.
- [ ] PASS requires: an explicit overfit note calling out the hardcoded dollar figures.
- [ ] PASS requires: an explicit dedupe note addressing the two supplied names and correctly concluding no duplicate.
- [ ] PASS requires: all 5 review-checklist items present in the output.
- [ ] FAIL if: the response invents tool calls or outputs not in the pasted trace, or silently writes/claims to submit the case into an actual Langfuse dataset instead of presenting a draft.
