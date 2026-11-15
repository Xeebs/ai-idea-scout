# Scenario 2: Internal policy Q&A rewriter (should NOT recommend fine-tuning)

## Input

**Task description**: "Given an employee's question about our internal expense policy, answer using the current expense policy document and rewrite the answer in a friendly, concise tone (2-3 sentences, no legal jargon)."

**Examples (14 rows, representative sample shown)**:
```
input: "Can I expense a client dinner over $150?" -> output: "Client dinners up to $200 per person are covered with a receipt and the client's name noted - you're all set, just make sure to log it within 30 days."
input: "Do I need a receipt for a $20 taxi ride?" -> output: "Receipts are required for anything over $25, so you're fine without one here - just note the date and purpose in your expense report."
input: "What's our current mileage reimbursement rate?" -> output: "It's $0.67 per mile as of this quarter - just log miles driven, not total trip time."
input: "Can I expense a hotel upgrade?" -> output: "Hotel upgrades aren't covered unless pre-approved by your manager - happy to check with them if you want to pursue it."
... (10 more rows, all Q&A about specific policy numbers/rules: per diem rates, international travel limits, software purchase approval thresholds, etc. Every example cites a specific current number or rule from the policy doc.)
```

**Already tried few-shot prompting?**: "No, haven't tried that yet - I just assumed fine-tuning was the way to make the model 'know' our policy."

## Pass criteria

- [ ] Gate 1 (prompt ceiling) should trigger first in practice since few-shot wasn't tried, OR the advisor should at minimum flag this before reaching a final verdict — but even if prompting were tried, Gate 2 is the critical gate here.
- [ ] Gate 2 (knowledge vs. behavior) correctly identifies this as a **knowledge gap**, not a behavior gap — every example hinges on specific, current factual numbers from a policy document (dollar thresholds, mileage rate, approval limits), not on format/tone consistency alone.
- [ ] Final recommendation is **STICK WITH PROMPTING + RAG** (or at minimum explicitly flags "try few-shot prompting first" at Gate 1 before ever reaching a FINE-TUNE verdict) — must NOT output a final FINE-TUNE recommendation with a synthetic-size/base-model sizing for this scenario.
- [ ] Explanation clearly states why fine-tuning would bake in current policy numbers that will go stale when the policy document changes, which is the core reason this is a RAG problem not a fine-tuning problem.
- [ ] Concrete next action given (try few-shot prompting with the policy doc in context, and/or set up retrieval over the policy document) rather than a vague "consider other options."
- [ ] Does not compute or present a synthetic training set size or base model tier for this scenario (those only belong to a FINE-TUNE verdict).

## Fail if

- Recommends FINE-TUNE and proceeds to size a synthetic set / base model for a task that is fundamentally about looking up current, changeable facts.
- Fails to distinguish this from Scenario 1 (treats both as equivalent "behavior" tasks).
- Gives generic advice without naming RAG/retrieval as the concrete alternative.
