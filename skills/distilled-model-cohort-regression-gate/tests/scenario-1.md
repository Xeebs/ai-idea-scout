# Scenario 1 — Intent classifier distillation: aggregate improves, one cohort craters

## Context
A support-ticket platform distilled its baseline intent classifier into a smaller on-device model to cut latency. Before promoting the candidate model, the ML team ran both models against a held-out, cohort-tagged eval set (cohort = ticket category) and wants a ship/no-ship call. They know the aggregate number looks good and specifically want to know if that's hiding anything per category.

## Input handed to the skill

Match rule: exact match (both models predict one of a fixed set of intent labels; expected is the gold label).
Regression threshold: not specified → use default 3 percentage points.
Minimum cohort sample size: not specified → use default 20 rows.

Full eval set (CSV, 110 rows, columns: `input,expected,cohort_tag,baseline_output,candidate_output`):

```
input,expected,cohort_tag,baseline_output,candidate_output
"I can't log in, reset my password" ticket #001,password_reset,password_reset,password_reset,password_reset
"I can't log in, reset my password" ticket #002,password_reset,password_reset,password_reset,password_reset
"I can't log in, reset my password" ticket #003,password_reset,password_reset,password_reset,password_reset
"I can't log in, reset my password" ticket #004,password_reset,password_reset,password_reset,password_reset
"I can't log in, reset my password" ticket #005,password_reset,password_reset,password_reset,password_reset
"I can't log in, reset my password" ticket #006,password_reset,password_reset,password_reset,password_reset
"I can't log in, reset my password" ticket #007,password_reset,password_reset,password_reset,password_reset
"I can't log in, reset my password" ticket #008,password_reset,password_reset,password_reset,password_reset
"I can't log in, reset my password" ticket #009,password_reset,password_reset,password_reset,password_reset
"I can't log in, reset my password" ticket #010,password_reset,password_reset,password_reset,password_reset
"I can't log in, reset my password" ticket #011,password_reset,password_reset,password_reset,password_reset
"I can't log in, reset my password" ticket #012,password_reset,password_reset,password_reset,password_reset
"I can't log in, reset my password" ticket #013,password_reset,password_reset,password_reset,password_reset
"I can't log in, reset my password" ticket #014,password_reset,password_reset,password_reset,password_reset
"I can't log in, reset my password" ticket #015,password_reset,password_reset,password_reset,password_reset
"I can't log in, reset my password" ticket #016,password_reset,password_reset,password_reset,password_reset
"I can't log in, reset my password" ticket #017,password_reset,password_reset,password_reset,password_reset
"I can't log in, reset my password" ticket #018,password_reset,password_reset,password_reset,password_reset
"I can't log in, reset my password" ticket #019,password_reset,password_reset,password_reset,password_reset
"I can't log in, reset my password" ticket #020,password_reset,password_reset,password_reset,password_reset
"I can't log in, reset my password" ticket #021,password_reset,password_reset,password_reset,password_reset
"I can't log in, reset my password" ticket #022,password_reset,password_reset,password_reset,password_reset
"I can't log in, reset my password" ticket #023,password_reset,password_reset,password_reset,password_reset
"I can't log in, reset my password" ticket #024,password_reset,password_reset,password_reset,password_reset
"I can't log in, reset my password" ticket #025,password_reset,password_reset,password_reset,password_reset
"I can't log in, reset my password" ticket #026,password_reset,password_reset,password_reset,password_reset
"I can't log in, reset my password" ticket #027,password_reset,password_reset,password_reset,password_reset
"I can't log in, reset my password" ticket #028,password_reset,password_reset,password_reset,password_reset
"I can't log in, reset my password" ticket #029,password_reset,password_reset,password_reset,password_reset
"I can't log in, reset my password" ticket #030,password_reset,password_reset,password_reset,mfa_lockout
"I can't log in, reset my password" ticket #031,password_reset,password_reset,mfa_lockout,password_reset
"I can't log in, reset my password" ticket #032,password_reset,password_reset,mfa_lockout,password_reset
"I can't log in, reset my password" ticket #033,password_reset,password_reset,mfa_lockout,password_reset
"I can't log in, reset my password" ticket #034,password_reset,password_reset,mfa_lockout,password_reset
"I can't log in, reset my password" ticket #035,password_reset,password_reset,mfa_lockout,password_reset
"I can't log in, reset my password" ticket #036,password_reset,password_reset,mfa_lockout,password_reset
"I can't log in, reset my password" ticket #037,password_reset,password_reset,mfa_lockout,password_reset
"I can't log in, reset my password" ticket #038,password_reset,password_reset,mfa_lockout,password_reset
"I can't log in, reset my password" ticket #039,password_reset,password_reset,mfa_lockout,password_reset
"I can't log in, reset my password" ticket #040,password_reset,password_reset,mfa_lockout,mfa_lockout
"Where is my order, it's late" ticket #001,shipping_delay,shipping_delay,shipping_delay,shipping_delay
"Where is my order, it's late" ticket #002,shipping_delay,shipping_delay,shipping_delay,shipping_delay
"Where is my order, it's late" ticket #003,shipping_delay,shipping_delay,shipping_delay,shipping_delay
"Where is my order, it's late" ticket #004,shipping_delay,shipping_delay,shipping_delay,shipping_delay
"Where is my order, it's late" ticket #005,shipping_delay,shipping_delay,shipping_delay,shipping_delay
"Where is my order, it's late" ticket #006,shipping_delay,shipping_delay,shipping_delay,shipping_delay
"Where is my order, it's late" ticket #007,shipping_delay,shipping_delay,shipping_delay,shipping_delay
"Where is my order, it's late" ticket #008,shipping_delay,shipping_delay,shipping_delay,shipping_delay
"Where is my order, it's late" ticket #009,shipping_delay,shipping_delay,shipping_delay,shipping_delay
"Where is my order, it's late" ticket #010,shipping_delay,shipping_delay,shipping_delay,shipping_delay
"Where is my order, it's late" ticket #011,shipping_delay,shipping_delay,shipping_delay,shipping_delay
"Where is my order, it's late" ticket #012,shipping_delay,shipping_delay,shipping_delay,shipping_delay
"Where is my order, it's late" ticket #013,shipping_delay,shipping_delay,shipping_delay,shipping_delay
"Where is my order, it's late" ticket #014,shipping_delay,shipping_delay,shipping_delay,shipping_delay
"Where is my order, it's late" ticket #015,shipping_delay,shipping_delay,shipping_delay,shipping_delay
"Where is my order, it's late" ticket #016,shipping_delay,shipping_delay,shipping_delay,shipping_delay
"Where is my order, it's late" ticket #017,shipping_delay,shipping_delay,shipping_delay,shipping_delay
"Where is my order, it's late" ticket #018,shipping_delay,shipping_delay,shipping_delay,shipping_delay
"Where is my order, it's late" ticket #019,shipping_delay,shipping_delay,shipping_delay,shipping_delay
"Where is my order, it's late" ticket #020,shipping_delay,shipping_delay,shipping_delay,shipping_delay
"Where is my order, it's late" ticket #021,shipping_delay,shipping_delay,shipping_delay,shipping_delay
"Where is my order, it's late" ticket #022,shipping_delay,shipping_delay,shipping_delay,shipping_delay
"Where is my order, it's late" ticket #023,shipping_delay,shipping_delay,shipping_delay,shipping_delay
"Where is my order, it's late" ticket #024,shipping_delay,shipping_delay,shipping_delay,lost_package
"Where is my order, it's late" ticket #025,shipping_delay,shipping_delay,lost_package,shipping_delay
"Where is my order, it's late" ticket #026,shipping_delay,shipping_delay,lost_package,shipping_delay
"Where is my order, it's late" ticket #027,shipping_delay,shipping_delay,lost_package,shipping_delay
"Where is my order, it's late" ticket #028,shipping_delay,shipping_delay,lost_package,shipping_delay
"Where is my order, it's late" ticket #029,shipping_delay,shipping_delay,lost_package,lost_package
"Where is my order, it's late" ticket #030,shipping_delay,shipping_delay,lost_package,lost_package
"I was charged twice for one order" ticket #001,billing_dispute,billing_dispute,billing_dispute,billing_dispute
"I was charged twice for one order" ticket #002,billing_dispute,billing_dispute,billing_dispute,billing_dispute
"I was charged twice for one order" ticket #003,billing_dispute,billing_dispute,billing_dispute,billing_dispute
"I was charged twice for one order" ticket #004,billing_dispute,billing_dispute,billing_dispute,billing_dispute
"I was charged twice for one order" ticket #005,billing_dispute,billing_dispute,billing_dispute,billing_dispute
"I was charged twice for one order" ticket #006,billing_dispute,billing_dispute,billing_dispute,billing_dispute
"I was charged twice for one order" ticket #007,billing_dispute,billing_dispute,billing_dispute,billing_dispute
"I was charged twice for one order" ticket #008,billing_dispute,billing_dispute,billing_dispute,billing_dispute
"I was charged twice for one order" ticket #009,billing_dispute,billing_dispute,billing_dispute,billing_dispute
"I was charged twice for one order" ticket #010,billing_dispute,billing_dispute,billing_dispute,billing_dispute
"I was charged twice for one order" ticket #011,billing_dispute,billing_dispute,billing_dispute,billing_dispute
"I was charged twice for one order" ticket #012,billing_dispute,billing_dispute,billing_dispute,billing_dispute
"I was charged twice for one order" ticket #013,billing_dispute,billing_dispute,billing_dispute,billing_dispute
"I was charged twice for one order" ticket #014,billing_dispute,billing_dispute,billing_dispute,refund_request
"I was charged twice for one order" ticket #015,billing_dispute,billing_dispute,billing_dispute,refund_request
"I was charged twice for one order" ticket #016,billing_dispute,billing_dispute,billing_dispute,refund_request
"I was charged twice for one order" ticket #017,billing_dispute,billing_dispute,billing_dispute,refund_request
"I was charged twice for one order" ticket #018,billing_dispute,billing_dispute,billing_dispute,refund_request
"I was charged twice for one order" ticket #019,billing_dispute,billing_dispute,billing_dispute,refund_request
"I was charged twice for one order" ticket #020,billing_dispute,billing_dispute,billing_dispute,refund_request
"I was charged twice for one order" ticket #021,billing_dispute,billing_dispute,billing_dispute,refund_request
"I was charged twice for one order" ticket #022,billing_dispute,billing_dispute,refund_request,billing_dispute
"I was charged twice for one order" ticket #023,billing_dispute,billing_dispute,refund_request,refund_request
"I was charged twice for one order" ticket #024,billing_dispute,billing_dispute,refund_request,refund_request
"I was charged twice for one order" ticket #025,billing_dispute,billing_dispute,refund_request,refund_request
"I want a refund for a damaged item" ticket #001,refund_request,refund_request,refund_request,refund_request
"I want a refund for a damaged item" ticket #002,refund_request,refund_request,refund_request,refund_request
"I want a refund for a damaged item" ticket #003,refund_request,refund_request,refund_request,refund_request
"I want a refund for a damaged item" ticket #004,refund_request,refund_request,refund_request,refund_request
"I want a refund for a damaged item" ticket #005,refund_request,refund_request,refund_request,refund_request
"I want a refund for a damaged item" ticket #006,refund_request,refund_request,refund_request,refund_request
"I want a refund for a damaged item" ticket #007,refund_request,refund_request,refund_request,refund_request
"I want a refund for a damaged item" ticket #008,refund_request,refund_request,refund_request,refund_request
"I want a refund for a damaged item" ticket #009,refund_request,refund_request,refund_request,refund_request
"I want a refund for a damaged item" ticket #010,refund_request,refund_request,refund_request,refund_request
"I want a refund for a damaged item" ticket #011,refund_request,refund_request,refund_request,refund_request
"I want a refund for a damaged item" ticket #012,refund_request,refund_request,refund_request,billing_dispute
"I want a refund for a damaged item" ticket #013,refund_request,refund_request,billing_dispute,billing_dispute
"I want a refund for a damaged item" ticket #014,refund_request,refund_request,billing_dispute,billing_dispute
"I want a refund for a damaged item" ticket #015,refund_request,refund_request,billing_dispute,billing_dispute
```

## Ground truth (for grading the skill's arithmetic — not given to the skill)

| Cohort | N | Baseline acc | Candidate acc | Delta | Discordant (b01,b10) | Significance | Correct verdict |
|---|---|---|---|---|---|---|---|
| password_reset | 40 | 75.0% | 95.0% | +20.0pp | (1,9) | n/a (positive) | OK |
| shipping_delay | 30 | 80.0% | 90.0% | +10.0pp | (1,4) | n/a (positive) | OK |
| billing_dispute | 25 | 84.0% | 56.0% | **-28.0pp** | (8,1), n=9 | exact sign test, p≈0.039, **significant** | **REGRESSION** |
| refund_request | 15 | 80.0% | 73.3% | -6.7pp | (1,0) | N/A — below min sample (15 < 20) | INSUFFICIENT DATA |

Aggregate: N=110, baseline 79.1% (87/110), candidate 81.8% (90/110), **delta +2.7pp (aggregate improves)**.

Correct overall call: **NO-GO** — despite the aggregate improving, `billing_dispute` regresses by 28 points with a statistically significant paired test, and must block promotion even though the global number looks good.

## Pass criteria
- [ ] States the assumptions used (match rule = exact match, threshold = 3pp default, min sample = 20 default) near the top of the output.
- [ ] Reports the aggregate delta as positive (~+2.7pp), explicitly noting that this is a top-line improvement.
- [ ] Per-cohort table correctly identifies `billing_dispute` as regressing roughly 25-30pp (exact figure ±1pp acceptable) and flags it as significant / REGRESSION.
- [ ] Correctly recognizes `billing_dispute`'s discordant count (9) is below 10 and either uses or explicitly names the small-sample exact test rather than (or in addition to) a chi-square approximation — does not silently apply McNemar's chi-square formula to a discordant count under 10 without flagging the small-sample caveat.
- [ ] `password_reset` and `shipping_delay` are both marked OK (positive deltas).
- [ ] `refund_request` is marked INSUFFICIENT DATA because N=15 is below the 20-row minimum — not scored OK/WATCH/REGRESSION.
- [ ] Final recommendation is **NO-GO**, and the one-line justification explicitly names `billing_dispute` as the driver, not the aggregate number.
- [ ] Does not let the positive aggregate delta override or soften the NO-GO call.

## Fail conditions
- Recommends GO or GO WITH CAVEATS because the aggregate improved, without blocking on `billing_dispute`.
- Treats `refund_request` as a pass or fail instead of insufficient data.
- Misses or ignores the `billing_dispute` regression entirely.
- Applies the same significance test uniformly without regard to discordant-pair count (e.g. always uses McNemar chi-square even when b01+b10 < 10, with no caveat).
