# Scenario 1 — Partial key mapping, non-overlapping activity windows, calibration data available

## Setup

"Ferrotype," a mid-size multi-tenant SaaS, needs a per-tenant cost breakdown for March 2026 ahead of an internal margin review. Two tenants (Acme, Brightline) got dedicated API keys and a tenant-naming proxy partway through their rollout; two older tenants (Cobalt, Delta) were onboarded before dedicated keys existed and still share one legacy key. The team knows Cobalt's staff are only active 09:00–11:00 UTC and Delta's only 14:00–16:00 UTC (from the app's own usage logs), and these windows never overlap. In June 2026 the team fixed instrumentation for the shared-key pair specifically and now tags tenant_id — that window is provided for calibration.

## Input data to hand the skill

**Known tenant/key facts:**
- `sk-acme-001` → Acme only (unique key). Acme calls route through `/v1/tenant-proxy/acme/chat`.
- `sk-bright-002` → Brightline only (unique key). Brightline calls route through `/v1/tenant-proxy/brightline/chat`.
- `sk-shared-003` → shared by Cobalt and Delta, both via legacy endpoint `/v1/chat/completions`.
- Cobalt active window: 09:00–11:00 UTC. Delta active window: 14:00–16:00 UTC. No other tenant uses these windows.

**Billing/usage export, March 2026:**

| # | Timestamp (UTC) | API key | Cost |
|---|---|---|---|
| 1 | 03-03 09:15 | sk-shared-003 | $0.72 |
| 2 | 03-03 14:20 | sk-shared-003 | $0.48 |
| 3 | 03-04 10:05 | sk-acme-001 | $1.50 |
| 4 | 03-04 15:40 | sk-bright-002 | $0.90 |
| 5 | 03-05 09:40 | sk-shared-003 | $0.57 |
| 6 | 03-05 22:10 | sk-shared-003 | $0.36 |
| 7 | 03-06 10:30 | sk-acme-001 | $1.35 |
| 8 | 03-06 14:55 | sk-shared-003 | $0.42 |
| 9 | 03-07 15:10 | sk-bright-002 | $0.60 |
| 10 | 03-07 09:05 | sk-shared-003 | $0.66 |
| 11 | 03-08 03:00 | sk-shared-003 | $0.24 |

**Observability metadata export, March 2026** (rows 1–5, 7–10 have a matching observability record at the same key+timestamp with endpoint info as described above; **row 11 has no matching observability record at all** — it only appears in the billing export).

**Calibration export, June 2026** (shared key, tenant_id now tagged):

| Timestamp (UTC) | Cost | Tenant |
|---|---|---|
| 06-02 09:20 | $0.50 | Cobalt |
| 06-02 14:35 | $0.44 | Delta |
| 06-03 10:10 | $0.61 | Cobalt |
| 06-03 15:05 | $0.39 | Delta |
| 06-04 09:50 | $0.55 | Cobalt |
| 06-04 23:40 | $0.28 | Delta |

(Note the last calibration row is Delta activity at 23:40 UTC — outside Delta's normal 14:00–16:00 window.)

## Pass criteria

- [ ] Acme and Brightline rows (1.50, 1.35, 0.90, 0.60 → $2.85 and $1.50 totals) are tiered **High** on unique key + tenant-named endpoint.
- [ ] Cobalt/Delta shared-key rows that fall inside their known windows (rows 1, 2, 5, 8, 10 → $0.72+$0.48+$0.57+$0.42+$0.66) are tiered **Medium**, split correctly: Cobalt = $0.72+$0.57+$0.66 = $1.95; Delta = $0.48+$0.42 = $0.90.
- [ ] Row 6 ($0.36, 22:10, outside both windows) is tiered **Unattributed**, not forced into Cobalt or Delta.
- [ ] Row 11 ($0.24, no observability match) is reported as a **coverage gap**, distinct from Unattributed.
- [ ] Reconciliation: High ($4.35) + Medium ($2.85) + Unattributed ($0.36) + Coverage gap ($0.24) = $7.80, matching the billing export total.
- [ ] The calibration section reports a measured accuracy figure derived from the June data — and does **not** claim 100%. It should note that the 23:40 Delta charge falls outside the known window and that the blind method would have placed it in Unattributed rather than misattributing it to Cobalt (a safe miss, not a wrong attribution).
- [ ] Each tenant row has a one-line methodology note citing the actual signal (unique key vs. timing-window correlation on a shared key).
- [ ] No Unattributed or coverage-gap dollars are folded into any tenant's total.

## Fail conditions

- Treating Cobalt/Delta shared-key traffic as High confidence (no unique key exists — this would overstate certainty).
- Silently dropping row 11 or row 6 instead of reporting them as explicit gap/unattributed buckets.
- Claiming the calibration validates 100% accuracy without engaging with the 23:40 edge case.
- Producing a single blended total per tenant with no tier breakdown.
