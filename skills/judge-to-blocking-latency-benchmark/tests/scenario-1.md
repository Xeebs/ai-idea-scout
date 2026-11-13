# Scenario 1 — Marketplace scam-listing judge with full inputs

## Input (what the user hands to the skill)

**Judge prompt/rubric** (verbatim):
```
You are reviewing a marketplace listing (title + description + price) before it is shown to buyers.
Flag the listing as SCAM if it matches any of these patterns:
- Requests payment outside the platform (wire transfer, gift cards, crypto, "contact me on WhatsApp/Telegram to pay")
- Price is more than 70% below the category's typical market price with no stated reason (damage, clearance, etc.)
- Listing text contains urgency/pressure language ("must sell today", "first come first serve, no returns")
- Seller account is brand new (less than 7 days old) AND item is a high-value category (electronics, jewelry, vehicles)
Otherwise mark SAFE.
Output only SCAM or SAFE.

Listing: {title} / {description} / {price} / seller_account_age_days: {age}
```

**How it's used**: Runs asynchronously on every new listing after it's already live, as a sampled continuous-evaluation check (per the pattern described in the idea's Gap section — detects, doesn't block). Platform wants to block the clearest SCAM cases synchronously before the listing ever goes live, but keep the full async judge for everything else.

**Latency budget**: p99 under 250ms for the synchronous path.

**Current full-judge latency**: average 1.6s, p99 2.3s (same vendor's large model, called per listing).

**Named harm category**: scam listings (as defined in the rubric above — no separate ask needed).

**Labeled sample traces** (28 total: 18 benign, 10 scam):
1. "iPhone 15 Pro, barely used" / "$200, must sell TODAY, pay via Venmo friend/family or gift card only, no meetups" / seller age 2 days — label: scam
2. "Vintage armchair" / "$80, pickup only, cash on delivery" / seller age 400 days — label: benign
3. "Rolex Submariner authentic" / "$150 firm, contact me on Telegram @watch_deals to arrange payment" / seller age 1 day — label: scam
4. "Used textbook, Intro to Biology" / "$25, like new, platform checkout only" / seller age 900 days — label: benign
5. "PS5 console bundle" / "$90, selling fast, first come first serve, no returns, no refunds, must act now" / seller age 5 days — label: scam
6-15. Ten more benign listings: normal-priced household items, books, furniture, clothing, all platform checkout, mixed seller ages 30-1200 days.
16-20. Five more scam listings: two more gift-card/off-platform payment requests, one "90% off brand new MacBook, wire transfer only," two new-seller (3-6 days) high-value electronics with urgency language and no stated discount reason.
21-28. Eight more benign listings: a few new sellers (4-6 days old) selling low-value items like phone cases and used clothing — these deliberately test whether the new-seller-plus-high-value rule overfires on new sellers selling low-value, non-flagged categories.

## Expected output characteristics (pass/fail criteria)

- [ ] States full confidence (rubric was pasted verbatim, 28 traces with both classes present, current latency given) — no reduced-confidence caveat needed here.
- [ ] Full-judge baseline simulation correctly flags all 10 scam-labeled traces as SCAM (the rubric's rules are explicit enough that a careful read should catch all of them) and does not flag the new-seller-but-low-value benign traces (items 21-28) as SCAM, since the rubric's new-seller rule is scoped to high-value categories only.
- [ ] Deterministic pre-filter strategy correctly identifies off-platform-payment-language and urgency-language as mechanically rule-checkable (explicit keyword/phrase patterns named in the rubric), and the price/category/seller-age combination as needing escalation to the judge (requires category-typical-price knowledge the pre-filter can't resolve with pure pattern matching) — reports an escalation rate, not 0% or 100%.
- [ ] Distilled-proxy heuristic strategy produces its own catch-rate/false-positive numbers, explicitly labeled as "reasoning applied to a condensed rubric," not as an actual trained model.
- [ ] Fail-closed timeout wrapper section produces a quantitative estimate (since current latency 1.6s/p99 2.3s was given) that nearly all synchronous calls would exceed the 250ms budget if run as full judge calls unmodified — correctly concluding the full judge cannot run synchronously as-is at this budget, which is the entire reason distillation strategies are needed.
- [ ] Strategy Comparison table has no invented latency numbers in milliseconds for the pre-filter/distilled-proxy rows — only "near-zero" / qualitative characterizations, since no real model timing was ever run.
- [ ] Recommendation section names a specific strategy or combination (plausibly: deterministic pre-filter catching the obvious off-platform-payment/urgency cases directly, escalating ambiguous price/seller-age cases to either the distilled proxy or async judge) and includes the explicit caveat that these are sample-based simulation numbers, not measured production numbers.
- [ ] Benchmark Harness section contains an actual runnable Python code block with pluggable `judge_fn`, `prefilter_fn`, `distilled_fn`, a timeout wrapper, and a scoring loop (catch-rate, false-positive rate, p50/p99 latency) — not just prose describing what a harness would do.
- [ ] "What this doesn't tell you" section explicitly notes that no real model was called and the harness must be run against the team's actual judge/pre-filter/small-model implementations before any production decision.
