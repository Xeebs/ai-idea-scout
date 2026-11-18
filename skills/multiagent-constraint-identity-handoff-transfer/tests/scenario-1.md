# Scenario 1 — Support triage escalating to a refunds agent

## Setup
A SaaS company runs a two-agent support pipeline. The user pastes both agents' full system prompts (realistic length, not a toy one-liner):

**Upstream — "Triage Agent" system prompt:**
```
You are the first point of contact for customer support chats. Your job is to understand the
customer's issue, answer simple questions yourself, and escalate to the Refunds Agent for anything
involving money back.

Tone: warm, brief, never robotic-sounding. Always acknowledge frustration before offering a solution.

Rules:
- Never promise a refund amount yourself — that's the Refunds Agent's job.
- Never discuss a customer's billing history details beyond what they already stated.
- If a customer threatens to cancel, do not offer a discount to retain them — escalate instead.
- Always include this exact line when escalating: "I'm connecting you with our billing team who can
  resolve this right away."
```

**Downstream — "Refunds Agent" system prompt:**
```
You handle refund requests escalated from Triage. You can approve refunds up to $50 without manager
approval. Refunds over $50 need a manager tag. You should be efficient and get the customer their
answer quickly.
```

**Known-bad incident the user also pastes:**
"Yesterday the Refunds Agent told a frustrated customer 'I'll give you a 20% discount on your next
order to make up for this' instead of processing a refund — we don't even have a discount feature on
this agent."

**Sample downstream response to spot-check:**
"Hi! I see you're frustrated — I can offer you a $60 refund right now, no manager needed, and also
throw in a 15% discount code for your trouble."

## Pass criteria
- Output extracts at least these upstream items correctly: tone (warm/brief/acknowledge frustration), forbidden action (never promise refund amount itself — though this is upstream-specific, see fit check), forbidden action (no discounts to retain), required phrasing (the exact escalation line).
- Downstream Fit Check correctly identifies that "never promise a refund amount yourself" is upstream-specific and does NOT carry to the Refunds Agent (whose whole job is promising refund amounts) — this is the key trap the scenario is designed to test.
- "No discounts to retain customers" is correctly flagged as CARRIES OVER (nothing in the downstream prompt authorizes discounts, and the known-bad incident is exactly this violation).
- Required phrasing item is flagged as upstream-specific (it's Triage's own escalation line, not something the Refunds Agent itself must say) unless the model reasonably argues otherwise with stated logic — either call is acceptable as long as reasoning is given.
- Ambiguous Rules list includes the $50 refund threshold being per-request vs. some other scope ambiguity, OR explicitly states no ambiguity found there (acceptable either way, as long as it isn't silently invented as settled when the downstream prompt actually doesn't specify per-item vs per-order for the discount-adjacent case).
- Conformance Spot-Check flags the sample response's "15% discount code" as a VIOLATION against the inherited "no discounts to retain" capsule item, quoting the exact phrase — this is the required catch, since it's the one capsule item (an inherited rule) the spot-check is actually scoped to check against.
- (Bonus, not required for pass/fail): the output may also separately note that "$60 refund, no manager needed" contradicts the downstream agent's own stated $50 threshold — this is a downstream-native rule, not a capsule item, so it's fine whether or not the output remarks on it, as long as it isn't presented as a capsule/inherited-rule violation.
- Output never claims the spot-check is a validated detector; says it's one manual pass.

## Fail criteria
- Treats "never promise a refund amount" as blindly carrying over to the Refunds Agent without noticing the contradiction with the downstream agent's actual job.
- Misses the discount violation in the spot-check.
- Invents a numeric limit, phrase, or rule not present in either pasted prompt.
- Produces a single merged list instead of the four required categories.
