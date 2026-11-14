# Scenario 1 — Sales-intelligence fact-checker considering web search escalation

## Input

> I'm designing an escalation policy for an AI agent that currently is quote-grounded only — it only answers from a prospect's own public filings, press releases, and LinkedIn data we've ingested, and refuses anything it can't ground in a direct quote. We're considering escalating to Tavily web search when our first-party corpus doesn't cover a prospect well enough (newer companies, international prospects). The risk profile: this feeds a sales rep's talking points before a call; if it's wrong, the rep looks unprepared or says something false to a prospect, but nothing regulatory or legally binding rides on it — it's reputational/sales-quality risk, not compliance risk. Our model's context window is 200K tokens. System prompt plus the first-party quote-grounded search results already use about 40K tokens before any escalation. We run roughly 300 queries/day and can tolerate up to ~3 extra seconds of latency per escalation.
>
> Using the Budget Gate procedure, draft my Escalation Policy Spec, flagging any schema field I can't currently populate as an open gap.

## Pass/fail criteria

- [ ] Classifies risk tier as **MEDIUM** (customer-facing, correctable, no legal/regulatory exposure — not HIGH, not LOW) with a one-line reason tied to the stated "reputational/sales-quality" framing.
- [ ] Escalation trigger uses the MEDIUM-tier rule: fires when first-party search returns fewer than 1 supporting quote (default), explicitly **no allow-list gate required** (that's the HIGH-tier-only requirement) — does not wrongly import the HIGH-tier two-condition rule.
- [ ] States the trigger threshold as an explicit, overridable number (not "when coverage seems thin").
- [ ] Context-budget cap is computed from the given numbers: 200K window, ~40K already spent → headroom ≈160K; cap = min(15% of 200K = 30K, 25% of 160K = 40K) → **30K tokens**. The answer should show this arithmetic, not just assert a number.
- [ ] States an overrun-handling behavior: truncate lowest-relevance passages first, then abort and surface "insufficient budget" if still over cap.
- [ ] Provenance schema includes all five fields (source, retrieved_at, claim_id, trust_tier, content_hash) and flags `trust_tier` as an **open gap** if the scenario gives no evidence a trust-tier taxonomy already exists (it doesn't — the input never mentions one).
- [ ] States the audit-log requirement as applying to every escalation decision (fired or not) plus budget spent, keyed by query ID.
- [ ] Does not recommend making retrieval always-on, and does not invent a risk profile, connector name, or context-window figure beyond what was given.
- [ ] Output follows the spec format (sections 1–4 plus Open Gaps) rather than loose prose.
