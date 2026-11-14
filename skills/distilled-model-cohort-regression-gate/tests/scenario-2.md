# Scenario 2 — Quantized reply-generation model: free-text outputs, custom thresholds, borderline cohort

## Context
A SaaS support team quantized their on-device reply-drafting model (for an offline-first mobile app) and wants a go/no-go before rollout. Outputs are free-text draft replies, not labels, so correctness isn't a simple string match. The team also wants stricter settings than the defaults: a 5-point regression threshold and a 15-row minimum cohort size (their eval set is smaller than usual). Cohorts are device/platform type, since the quantized model runs differently depending on on-device compute.

## Input handed to the skill

Regression threshold: **5 percentage points** (explicitly stated, overriding default).
Minimum cohort sample size: **15 rows** (explicitly stated, overriding default).
Match rule: **not stated** — the user just says "score whether the reply is correct" without defining how, even though outputs are free text.

Eval set (76 total rows across 4 device cohorts: `ios`, `android`, `web`, `legacy_browser`). A representative sample of rows is shown below per cohort; stated totals for the full set are given for grading.

### Cohort: ios (N=20, stated totals: baseline correct 18/20 = 90.0%, candidate correct 17/20 = 85.0%, discordant b01=2 b10=1)
| input | expected (reference resolution) | baseline_output | candidate_output |
|---|---|---|---|
| "Account locked after 5 failed logins" | Unlock account, send password reset link via email | "Your account was locked after repeated failed logins — I've unlocked it and emailed you a password reset link." | "Your account got locked from too many failed attempts. I've sent a reset link to your email." |
| "Can't access my account, locked out" | Unlock account, send password reset link via email | "I see the lockout — I've unlocked your account and sent a reset link to your email." | "I don't see anything wrong with your account. Can you try logging in again?" |
| "Keep getting locked out of my account" | Unlock account, send password reset link via email | "Sorry about that — I can't find an active lockout on your account right now, please try again in a few minutes." | "I've unlocked your account and emailed a password reset link — you should be able to log in now." |
| "App says account suspended after login attempts" | Unlock account, send password reset link via email | "Your account isn't actually suspended, this looks like a display glitch — please restart the app." | "I'm seeing the same false suspension message — restarting the app should clear it, no account action needed." |
| "Locked out again, this is the third time" | Unlock account, send password reset link via email | "I've unlocked your account and sent a new password reset link to your email on file." | "I've unlocked your account and sent a new password reset link to your email on file." |
*(15 more rows omitted — consistent with the stated 18/20 baseline, 17/20 candidate totals above)*

### Cohort: android (N=25, stated totals: baseline correct 18/25 = 72.0%, candidate correct 20/25 = 80.0%)
| input | expected | baseline_output | candidate_output |
|---|---|---|---|
| "Payment failed but I was still charged" | Confirm duplicate charge will be refunded within 5-7 business days | "I see the duplicate charge — a refund for the extra amount will post to your card within 5-7 business days." | "I see the duplicate charge — a refund for the extra amount will post to your card within 5-7 business days." |
| "My card got charged twice" | Confirm duplicate charge will be refunded within 5-7 business days | "I don't see a duplicate charge on this account, can you send a screenshot?" | "I've confirmed the duplicate charge and submitted a refund — expect it within 5-7 business days." |
| "Charged twice for the same subscription" | Confirm duplicate charge will be refunded within 5-7 business days | "I've confirmed the duplicate charge and submitted a refund — expect it within 5-7 business days." | "I don't see a duplicate charge on this account, can you send a screenshot?" |
*(22 more rows omitted — consistent with the stated 18/25 baseline, 20/25 candidate totals above)*

### Cohort: web (N=19, stated totals: baseline correct 14/19 = 73.7%, candidate correct 15/19 = 78.9%)
| input | expected | baseline_output | candidate_output |
|---|---|---|---|
| "Order hasn't arrived, it's a week late" | Offer tracking update and expedited reshipment if still missing after 48h | "I've pulled up tracking — it's delayed in transit. If it hasn't moved in 48 hours I'll send a free expedited replacement." | "I've pulled up tracking — it's delayed in transit. If it hasn't moved in 48 hours I'll send a free expedited replacement." |
*(18 more rows omitted — consistent with the stated 14/19 baseline, 15/19 candidate totals above)*

### Cohort: legacy_browser (N=12, stated totals: baseline correct 9/12 = 75.0%, candidate correct 8/12 = 66.7%)
| input | expected | baseline_output | candidate_output |
|---|---|---|---|
| "Page won't load on my old browser" | Recommend browser update or provide compatibility-mode link | "This app needs a modern browser — here's a compatibility-mode link that should work on yours." | "This app needs a modern browser — here's a compatibility-mode link that should work on yours." |
*(11 more rows omitted — consistent with the stated 9/12 baseline, 8/12 candidate totals above)*

## Ground truth (for grading — not given to the skill)

Aggregate: N=76, baseline correct = 18+18+14+9 = 59 (77.6%), candidate correct = 17+20+15+8 = 60 (78.9%), **delta +1.3pp (slight aggregate improvement)**.

| Cohort | N | Baseline | Candidate | Delta | vs. 5pp threshold | Correct verdict |
|---|---|---|---|---|---|---|
| ios | 20 | 90.0% | 85.0% | -5.0pp | at threshold, but discordant pairs (2,1)=3 too small to be significant | **WATCH** |
| android | 25 | 72.0% | 80.0% | +8.0pp | — | OK |
| web | 19 | 73.7% | 78.9% | +5.2pp | — | OK |
| legacy_browser | 12 | 75.0% | 66.7% | -8.3pp | N=12 < stated min 15 | **INSUFFICIENT DATA** |

Correct overall call: no cohort reaches REGRESSION (nothing both crosses -5pp *and* is statistically significant with such a small discordant count), so recommendation should be **GO WITH CAVEATS**, naming `ios` as a cohort to watch, and separately flagging `legacy_browser` as not evaluated for lack of data (12 rows < the user's stated 15-row minimum).

## Pass criteria
- [ ] Before (or clearly alongside) producing the cohort table, the skill either explicitly asks what correctness/match rule to use for these free-text replies, or explicitly states an assumed rule (e.g. "scoring whether each reply conveys the same resolution as the reference") as a flagged assumption — it must not silently treat this as plain exact-string match without comment, since the outputs are clearly free text.
- [ ] Uses the user-specified threshold (5 percentage points) and minimum sample size (15 rows) instead of the skill's own defaults (3pp / 20 rows) — this must be visible in the stated assumptions.
- [ ] `legacy_browser` (N=12) is marked INSUFFICIENT DATA because 12 < 15, not scored pass/fail.
- [ ] `ios` is flagged as a WATCH/caution cohort (delta right at -5pp) rather than silently passed — and is not escalated all the way to a hard REGRESSION/NO-GO given how small its discordant-pair count is, or if it is treated as REGRESSION the skill must explicitly justify why it still considered 3 discordant pairs sufficient for significance.
- [ ] `android` and `web` are both marked OK (clearly positive deltas).
- [ ] Final recommendation is **GO** or **GO WITH CAVEATS** — never outright NO-GO, since no cohort both crosses the threshold and is statistically significant — and if GO WITH CAVEATS, `ios` is the cohort named.
- [ ] `legacy_browser`'s insufficient-data status is reported separately from the pass/fail table, not folded silently into "OK" or omitted.

## Fail conditions
- Silently assumes exact string match on free-text replies and never surfaces that assumption.
- Ignores the user's custom threshold/minimum-sample values and applies the skill's own defaults instead.
- Scores `legacy_browser` as a normal pass/fail cohort despite having fewer rows than the user's stated minimum.
- Recommends NO-GO (no cohort actually meets the REGRESSION bar in the ground truth).
- Drops `ios` from the report entirely instead of flagging it as a borderline/WATCH cohort.
