# Soft Landing: Guardrail Degradation Policy Designer

Paste this whole document into any AI chat tool (ChatGPT, Claude, Gemini, etc.), then answer the prompts at the bottom with your own data. No other context needed.

## What this does

If your team runs LLM guardrail checks (classifiers, rule engines, LLM-judge calls) in front of a latency-sensitive production path — customer support bots, voice agents, real-time chat — and a latency spike or a tight p99 budget forces a choice between "eat the full guardrail cost" and "turn guardrails off entirely," this produces a **tiered degradation policy**: a written plan for which checks drop first, what cheaper fallback substitutes for each one, and which gaps can't be safely covered at all.

This is a **design document**, not a running system. It tells you *what* to build or configure; it doesn't enforce anything itself. If you need live enforcement against real traffic, that's a separate engineering project (a proxy/middleware layer), not something a chat prompt can do.

## When to use this

- Your guardrail layer is blowing your latency budget and today the only lever is "turn it all off."
- You're about to ship a new guardrail stack and want a pressure-tested fallback plan before a real incident forces an ad-hoc one.
- You want an audit of which of your checks have *no* cheap fallback, so you know your real exposure before a latency spike hits.

## What you need to provide

This is entirely manual input — nothing here reads from a live system or API. For **every** guardrail check you run, provide:
1. **Name** of the check.
2. **Type**: deterministic rule/regex, ML classifier, or LLM-judge call.
3. **Measured latency** — p95 or p99 in milliseconds if you have it, p50 if that's all you have. Rough estimates are fine ("the LLM judge call is around 400ms") — just don't guess numbers you have no basis for; say "unknown" instead and the assistant should ask you for it rather than inventing one.
4. **What it catches** — e.g. PII leakage, jailbreak/prompt injection, toxicity, brand/tone drift, output format validation.
5. **Current blocking status** — does it run synchronously (must finish before the response returns) or is it already async/sampled?

Also provide:
- Your **overall latency budget** for the guardrail layer (a target p99 in ms).
- Whether your checks run **serially or in parallel** today.

## The procedure to follow (copy this into your prompt)

```
You are designing a tiered guardrail degradation policy. I will give you a list
of guardrail checks (name, type, latency, what it catches, blocking status),
my overall latency budget, and whether checks run serially or in parallel.

Follow these steps:

1. Build a table of my checks as given. If any latency number is missing, ask
   me for it rather than guessing.

2. Compute total latency (sum if serial, max if parallel) and compare to my
   budget. State the overage or headroom in both ms and %.

3. Classify each check's severity using my own labels if I gave them;
   otherwise infer using this default ranking, and say explicitly which
   labels were inferred vs. given:
   - Critical: PII/data leakage, jailbreak/prompt injection, illegal content.
   - High: toxicity/hate, self-harm content, hallucinated claims in
     high-stakes domains (medical/legal/financial).
   - Medium: brand tone, off-topic drift, format/schema validation.
   - Low: style, verbosity, non-critical formatting.

4. For each check, identify whether a cheaper fallback exists (a deterministic
   substitute, e.g. a regex/NER PII filter standing in for an LLM-judge PII
   check). If no credible fallback exists for a Critical or High severity
   check, flag it as a coverage gap -- do not invent a fallback to make the
   table look complete.

5. Draft a 3-tier degradation policy, ordered so cheap+high-severity checks
   survive longest:
   - Tier 0 (always-on): Critical-severity checks, plus anything under ~10ms
     regardless of severity.
   - Tier 1 (drop at >80% of budget consumed): Medium/Low severity checks
     with an available cheap fallback or safe async-deferral.
   - Tier 2 (drop at >95% of budget consumed, or an active SLO breach):
     everything else, including High-severity checks ONLY if step 4 found a
     credible fallback for them -- otherwise keep them in Tier 0 and say so,
     even if that means the budget target can't be hit without more
     infrastructure.
   Every dropped check needs an assigned action: substitute-with-cheaper-check,
   defer-to-async/sampled-review, or drop-with-no-replacement (flagged).

6. Express trigger thresholds as % of budget consumed, not raw ms.

7. If even Tier 0 alone exceeds my stated budget, say so plainly -- don't
   force a tiering that pretends the SLO is reachable.

Output as:
1. Input summary table (mark any inferred fields).
2. Load assessment (overage/headroom in ms and %).
3. Degradation policy table: Tier | Checks | Trigger threshold | Action |
   Fallback (or "none -- coverage gap").
4. Coverage gaps list, each with one sentence on why it can't be safely
   dropped.
5. A YAML snippet encoding the tiers/thresholds/fallbacks, ready to hand to
   whoever implements the enforcement layer.
6. Open questions / assumptions -- every inferred severity label and every
   proposed fallback substitution I didn't explicitly confirm.

Never invent a latency number, a fallback mechanism, or a severity label
without flagging it as inferred. Never silently drop a Critical check.
This is a design document for humans to review and implement -- not a
live enforcement system.

Here is my data:
[PASTE YOUR CHECK LIST, BUDGET, AND SERIAL/PARALLEL INFO HERE]
```

## What you'll get back

A structured policy document: a table of your checks, how far over (or under) budget you are, a 3-tier drop order with explicit trigger percentages and fallback actions for every check, a called-out list of checks that have no safe fallback (your real exposure), a YAML snippet you can hand to an engineer, and a list of every assumption the assistant made so you can correct it before trusting the policy.

## What this does NOT do

- It does not run against your live traffic or enforce anything — that requires building a proxy/middleware layer.
- It does not benchmark or re-measure your checks' latency — it only works with numbers you supply.
- It does not guarantee your SLO is reachable — if your Critical-severity checks alone exceed budget, it will tell you that honestly instead of forcing a policy that looks complete but isn't safe.
