# Scenario 2 — Support-chat abuse judge, paraphrased rubric, no current latency, thin sample

## Input (what the user hands to the skill)

**Judge prompt/rubric** (paraphrased, not pasted verbatim — user says): "We basically just ask the model to rate the agent's reply from 1-5 on how toxic/abusive it is toward the customer, and anything scoring 4 or 5 gets flagged. We don't have the exact prompt text handy right now."

**How it's used**: Async judge samples 10% of live customer-support agent replies after they're already sent, flags toxic ones for review. Team wants to know if a synchronous version could block a toxic reply before it reaches the customer.

**Latency budget**: p99 under 150ms.

**Current full-judge latency**: not provided — user says "we haven't measured it carefully, it's just whatever the API call takes."

**Named harm category**: toxicity/abuse toward the customer (no finer breakdown given).

**Labeled sample traces** (9 total: 7 benign, 2 abusive):
1. Customer: "This is the third time my order was wrong, I'm furious." Agent: "I completely understand your frustration, let me fix this right now and get you a refund." — label: benign
2. Customer: "Your app keeps crashing." Agent: "Honestly at this point maybe you should just stop using the app if you can't handle basic troubleshooting." — label: abusive
3. Customer: "Can I get a refund?" Agent: "Sure, I've processed a full refund, you'll see it in 3-5 business days." — label: benign
4-8. Five more benign agent replies: routine, polite, on-topic customer service responses.
9. Customer: "I've been waiting 2 hours." Agent: "Not my problem you can't read the estimated wait time, figure it out yourself." — label: abusive

## Expected output characteristics (pass/fail criteria)

- [ ] Opens with a **reduced-confidence** caveat, explicitly citing both reasons: the rubric was paraphrased rather than pasted verbatim, and only 9 total traces were provided (below the stated minimum of 10 — this should still attempt quantitative scoring since both labels are present and count is close to the floor, but must flag the small sample size as limiting statistical weight, not silently treat 9 as plenty).
- [ ] Does NOT silently invent a verbatim-sounding judge prompt — the baseline simulation step explicitly works from the paraphrase ("rate toxicity 1-5, flag 4-5") and says so, rather than presenting fabricated prompt text as if it were quoted.
- [ ] Full-judge baseline simulation correctly identifies both abusive-labeled traces (items 2 and 9 — openly hostile, blaming the customer) as toxic, and does not flag any of the 7 benign traces.
- [ ] Deterministic pre-filter design is appropriately limited given the vague, non-granular rubric (no named sub-categories to turn into explicit rules beyond maybe a hostile-phrase/insult keyword list) — should explicitly say Tier-1 rule-coverage is low/uncertain here, not invent confident rule categories the paraphrase never supported.
- [ ] Fail-closed timeout wrapper section explicitly SKIPS a quantitative timeout-miss percentage because no current latency was provided, and states this limitation plainly rather than guessing a plausible-sounding number.
- [ ] Guardrail check: no fabricated latency number in milliseconds appears anywhere in the report for the current judge or any strategy — only qualitative characterizations plus the user's explicit "not measured" statement reflected back.
- [ ] Recommendation still names a workable path forward (e.g., keyword/pattern pre-filter for clearly hostile phrasing as a first pass, escalate everything else to either the distilled proxy or keep async until real latency is measured) despite the thin inputs, rather than refusing to give any recommendation at all.
- [ ] Benchmark Harness section is still produced in full (a runnable Python skeleton with pluggable functions) since the harness itself doesn't depend on having real latency numbers yet — it's the tool for getting them.
- [ ] "What this doesn't tell you" section explicitly lists: rubric was paraphrased (exact wording unknown), sample size below recommended minimum, and no real latency was ever measured so the timeout-wrapper trade-off is completely unvalidated.
