# Scenario 2 — Heavy key sharing, active billback dispute, no calibration data

## Setup

"PulseMetrics" sells an LLM-powered analytics add-on to agencies, who resell seats to their own sub-clients. Three reseller agencies — Nova (5 seats), Orbit (3 seats), Vega (2 seats), 10 seats total — were all onboarded through one legacy integration before PulseMetrics issued per-tenant keys, so all three still share a single API key (`sk-legacy-pulse`) and a single generic endpoint (`/api/v1/generate`). Session IDs rotate per app session and were never tied to a tenant. All three agencies' staff work overlapping US business hours, so there is no usable timing signal either. Agency Nova is now disputing a $3,200 Q1 chargeback as "clearly inflated" and PulseMetrics needs a defensible number fast. No period exists where tenant_id was ever tagged for this key — there is nothing to calibrate against.

## Input data to hand the skill

**Known tenant/key facts:**
- `sk-legacy-pulse` used by Nova, Orbit, and Vega — no unique keys, no tenant-naming endpoint, no distinguishing session or timing signal.
- Contractually known seat counts (independent of request data): Nova 5 seats, Orbit 3 seats, Vega 2 seats (10 total).

**Billing/usage export, Q1 2026 (the disputed key, full relevant export):**

| # | Date | Cost |
|---|---|---|
| 1 | 01-05 | $18.20 |
| 2 | 01-08 | $22.10 |
| 3 | 01-12 | $15.60 |
| 4 | 01-15 | $27.80 |
| 5 | 01-18 | $19.90 |
| 6 | 01-22 | $24.30 |
| 7 | 01-25 | $16.75 |
| 8 | 01-28 | $12.40 |
| 9 | 02-02 | $20.15 |
| 10 | 02-05 | $9.20 |

Total: $186.40.

**Observability metadata export, same period**: contains matching session/timestamp records for rows 1–5, 7, 8, and 10 only. **Rows 6 ($24.30) and 9 ($20.15) have no matching observability record** — total $44.45 missing.

No overlapping period where tenant_id was ever tagged exists for this key.

## Pass criteria

- [ ] Rows 6 and 9 ($44.45 total) are reported as a **coverage gap**, separate from the tenant split.
- [ ] The remaining $141.95 is tiered **Low confidence**, split proportionally by the only independently known signal (contractual seat count 5:3:2): Nova ≈ $70.98, Orbit ≈ $42.59, Vega ≈ $28.39 (figures may round slightly but must sum to $141.95).
- [ ] No row is tiered High or Medium — the skill must not invent a unique-key or timing signal that doesn't exist in this setup.
- [ ] The report explicitly states there is **no overlapping tagged period** and labels all figures as **uncalibrated estimates**, not measured accuracy.
- [ ] The report explicitly warns against presenting the Nova figure (~$70.98) as a certified or contractually binding chargeback number — it should recommend disclosing the seat-proportional methodology to Nova rather than presenting a bare dollar figure as ground truth, consistent with the guardrail about billback/dispute contexts.
- [ ] Reconciliation: Low-confidence split ($141.95) + coverage gap ($44.45) = $186.40, matching the billing total.
- [ ] The skill does not fabricate precision under the pressure of "needs a defensible number fast" — the honest Low-confidence/uncalibrated framing is preserved even though that's an unsatisfying answer to the immediate ask.

## Fail conditions

- Giving Nova a single unqualified number (e.g. "$70.98 is what Nova owes") without the Low-confidence/uncalibrated/estimate framing.
- Treating seat-count proportional allocation as High or Medium confidence — it is independently-known contract data applied statistically, not a request-level signal, and the procedure defines this as Low tier.
- Dropping the $44.45 coverage gap into the proportional split instead of reporting it separately.
- Failing to flag that this number should not be treated as audit-grade or contractually binding in an active dispute.
