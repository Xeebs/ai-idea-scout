---
name: retroactive-tenant-cost-reconstruction
description: Reconstructs a confidence-scored, per-tenant LLM cost breakdown for a historical period where tenant_id was never tagged on requests, using provider billing exports plus whatever request metadata the team's observability stack already captured. Use when a finance/platform lead needs a historical cost-per-customer number for a billback dispute, board report, or margin review covering a period before tenant tagging existed.
---

# Cost Forensics: Retroactive Per-Tenant LLM Cost Reconstruction

## When to use this
A finance or platform lead at a multi-tenant LLM SaaS company needs a tenant-level cost breakdown for a *past* billing period, but tenant_id was never logged on the original requests — only generic request metadata (API keys, session IDs, timestamps, endpoints) exists. The trigger is usually one of: a customer disputing a billback/chargeback number, a board or investor asking "what does customer X actually cost us," or a margin review that needs historical data the team assumed was unrecoverable. This is a one-time forensic pass on a closed historical window, not an ongoing attribution pipeline — if tenant_id is already tagged going forward, this skill isn't needed for future periods.

## Inputs
**Data source**: Connected — provider usage/billing APIs (OpenAI Usage API, Anthropic Admin/usage API — both mature, documented, available today) for raw per-request cost and timestamp data, exported by the user as CSV/JSON, plus the team's existing observability backend (e.g. Langfuse, Datadog LLM Observability, or custom logs) exported the same way for request metadata that *was* captured even though tenant_id specifically wasn't. This skill does not call those APIs itself — the user exports the data from their own provider/observability dashboards or API and hands Claude the files or pasted tables for the period in question.

Required:
1. **Billing/usage export** for the period: one row per request or per time-bucket with timestamp, model, token counts, cost, and whatever identifier the provider's billing records carry (API key or key hash, project/org ID).
2. **Observability metadata export** for the same period: request-level rows with API key, session ID, timestamp, endpoint/route, and (if available) user-agent or source IP.
3. **The team's tenant list**, with any partial identifying hints they already have: which API keys were provisioned to which tenants (even if incomplete), known tenant signup/active date ranges, known per-tenant integration endpoints (e.g. a webhook path containing a tenant slug).

Optional but strongly improves the result:
4. **An overlapping tagged period** — any window, even a short recent one, where tenant_id *was* actually captured. This is used to calibrate and validate the confidence scoring; without it, confidence tiers are reported as uncalibrated estimates.

If (1) or (2) is missing, stop and ask for it — there is no fallback that produces a defensible number without the raw request-level data.

## Procedure
1. **Parse and align the two exports** on shared keys: API key (or key hash), and timestamp proximity when no shared request ID exists. Flag any requests present in the billing export but missing from the observability export (and vice versa) as a coverage gap — report the gap's dollar size, don't silently ignore it.
2. **Classify each API key by exclusivity** using the tenant list: a key used only by one tenant across the team's records is a *unique key*; a key shared across multiple tenants (pooled/shared infrastructure key) is a *shared key*.
3. **Assign confidence tier per request/cluster**:
   - **High** — unique key with a confirmed single-tenant mapping, or an endpoint pattern that structurally encodes the tenant (e.g. `/t/{tenant_slug}/...`).
   - **Medium** — session ID or timing cluster that correlates tightly with one tenant's known active window, without a unique key, but with no competing tenant active in the same window.
   - **Low** — shared key and/or overlapping active windows across multiple tenants, where only proportional statistical allocation is possible (e.g. split by each tenant's share of total activity in that window, if that share is independently known).
   - **Unattributed** — no signal ties the request to any tenant at all. Keep this as its own bucket; never force it into a tenant's number.
4. **If an overlapping tagged period was provided**: mask its tenant_id field, re-run steps 1–3 on it blind, then compare the inferred tier-by-tier attribution against the real tagged ground truth. Report measured accuracy per tier (e.g. "High-tier inferences matched ground truth on 97% of dollars; Medium-tier matched on 61%"). This is the calibration number that makes the confidence tiers meaningful rather than asserted.
5. **If no overlapping tagged period exists**: state this explicitly in the report and label all tiers "uncalibrated estimate" rather than implying measured accuracy.
6. **Aggregate per tenant**: sum High + Medium + Low dollars separately, plus the Unattributed bucket, plus the coverage-gap dollars from step 1. Never collapse these into one blended number — the whole value of this report is keeping them visibly separate.
7. **Write the methodology note per tenant** — one sentence stating which signal(s) drove that tenant's attribution (e.g. "100% unique API key, no inference required" vs. "62% unique key, 38% timing-correlation inference against a shared key window").

## Output format
A Markdown report with:

```
## Per-Tenant Cost Reconstruction — <period>

Calibration: <"Validated against tagged period <dates>: High-tier accuracy X%, Medium-tier accuracy Y%"
  OR "No overlapping tagged period available — all tiers are uncalibrated estimates.">

| Tenant | High confidence | Medium confidence | Low confidence (inferred) | Tenant total | Methodology |
|---|---|---|---|---|---|
| <name> | $X | $X | $X | $X | <one-line signal summary> |
| ... | | | | | |
| **Unattributed** | — | — | — | $X | No key/session/endpoint signal ties this spend to any tenant |

Coverage gap: $X of billed spend had no matching observability record at all (requests logged by the provider but not captured by the observability export, or vice versa).
Total period spend: $X (High $X + Medium $X + Low $X + Unattributed $X + Coverage gap $X should sum to the billing export total — if not, state the discrepancy).
```

Follow with 2–4 sentences of plain-language interpretation: which tenants are solidly known, which are best-effort, and what the honest headline number is for whatever triggered the request (e.g. "for the billback dispute, $14,200 of Tenant Acme's $19,800 total is high-confidence; the remaining $5,600 is a statistical estimate and should be presented as such").

## Guardrails
- Never present a Low-confidence or Unattributed number as if it were exact — always carry the tier label through to any summary a human might forward to a customer or the board.
- Never fold Unattributed or Low-confidence spend into a tenant's total to make the report look cleaner — an honest gap is more valuable than a false precise number, which was the exact failure mode that made teams give up on this in the first place.
- Never infer an API-key-to-tenant mapping that isn't supported by data the user actually provided (the tenant list, the exports) — if no team wrote down that key X belongs to tenant Y, treat key X as unmapped, not as "probably" Y.
- Always state explicitly whether the confidence tiers are calibrated (against a real overlapping tagged period) or uncalibrated estimates — do not let a reader assume measured accuracy that wasn't actually measured.
- Never present this report as audit-grade or contractually binding without flagging it as a best-effort reconstruction — if the trigger is a billback dispute or legal/contractual matter, say plainly that this is forensic estimation, not a certified figure, and that any contractually binding number needs the counterpart's sign-off on methodology.
- If the two exports don't overlap enough to join (e.g. no shared key format, clocks out of sync by more than normal request latency), say so and stop rather than producing a number that looks real but rests on a broken join.
