# Scenario 2 — Startup considering disabling default tool-output capping on a customer-support agent, no task suite at all

## Input (what the user hands over)

> We built a customer-support agent on LangGraph that answers billing and account questions by calling internal tools (lookup_account, lookup_invoice, search_kb). Our framework setup caps raw tool output at 1,500 tokens by default before it goes back into the model's context — anything longer gets truncated with a "[...truncated]" marker. We think this might be causing bad answers when a customer's invoice history is long (invoice tool output gets cut off and the agent answers from partial data).
>
> We want to test turning the cap off entirely (pass full tool output through) versus keeping it, but we honestly don't have a formal task suite — we just have a Zendesk queue of past tickets we could pull examples from. We've never written pass/fail criteria for any of this. We also don't have any cost/latency numbers handy.

## What a correct skill run produces

An "A/B Test Design Brief" with:

1. **Hypothesis**: specific to removing the 1,500-token tool-output cap for `lookup_invoice`-type calls, predicting direction on answer correctness (for long invoice histories specifically) and on cost/latency (since full output is more tokens), with the truncation mechanism named.
2. **Baseline vs. Treatment**: baseline = current 1,500-token cap with truncation marker; treatment = cap removed / tool output passed through uncapped — matching the user's actual proposed change, not a generic "with vs without context engineering" framing.
3. **Task Sample**: since the user has no task suite, the skill must draft one (not refuse or stall) — around 10-15 candidate tasks derived from the described workload (billing/account questions, varying invoice-history length), each with a concrete, checkable pass/fail criterion (e.g. "answer must include all invoices in the account's history" / "answer must not state totals calculated from partial data"), explicitly flagged as a first draft the team should validate against real Zendesk tickets before trusting results. Must include tasks specifically with long invoice histories (the exact failure case named by the user) since that's the scenario this change targets.
4. **Metrics**: answer-correctness/success-rate delta, token/cost delta (expected to rise under treatment — should be named as a tradeoff, not just a cost), latency delta, and a constraint/accuracy check specific to this case (e.g. "did the agent cite or use invoice data beyond what the 1,500-token cap would have allowed" as a proxy signal for whether truncation was the actual cause).
5. **Statistical Plan**: repeat-run recommendation and test method appropriate for a drafted ~10-15 task suite, with an honest note that a freshly drafted (unvalidated) suite adds extra uncertainty beyond normal LLM noise.
6. **Execution Checklist**: steps usable against a LangGraph-based agent specifically (not assuming Claude Code CLI), toggling the tool-output cap config.
7. **Risks & Caveats**: must include that the task suite is synthetic/drafted rather than pulled from real Zendesk tickets, the cost tradeoff of uncapped tool output at scale, and that removing the cap entirely (vs. e.g. raising it or summarizing instead) wasn't the only option considered.

## Pass/Fail criteria

- PASS requires: the skill proceeds to draft a first-pass task suite rather than stopping because the user has none; drafted tasks specifically include long-invoice-history cases; the metrics explicitly call out that cost/latency are expected to move in the opposite direction from correctness (a real tradeoff, not framed as a pure win); the output stays neutral on whether removing the cap is a good idea; all 7 output sections are present in order.
- FAIL if: the skill refuses or stalls due to missing task suite/baseline data, fails to target the long-invoice-history failure case in the drafted tasks, declares a verdict ("removing the cap will definitely help") instead of designing a neutral test, or omits the cost-tradeoff framing entirely.
