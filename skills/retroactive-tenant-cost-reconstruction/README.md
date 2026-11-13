# Cost Forensics: Retroactive Per-Tenant LLM Cost Reconstruction

Paste this whole document into any AI chat tool (Claude, ChatGPT, etc.) along with your data when you need to reconstruct a per-tenant cost breakdown for a past period where you never tagged tenant_id on your LLM requests.

## What this is for

You run a multi-tenant SaaS product with LLM-powered features. Months ago, your billing/usage logs did not record which customer (tenant) each request belonged to — only generic metadata like API keys, session IDs, timestamps, and endpoints. Now you need a cost-per-customer number for that past period: a customer is disputing a chargeback, the board wants to know what your biggest customers actually cost you, or you're doing a margin review. The common advice online is "you can't do this — tenant tagging has to happen at request time." That's true for perfect numbers, but it's not true that you're stuck with nothing. This prompt reconstructs a **confidence-scored, best-effort** breakdown instead of giving up or faking precision.

This is a one-time forensic pass on a closed historical window — not a tool for ongoing attribution. If you've since started tagging tenant_id on every request, you don't need this for future periods; only for the gap before you did.

## What you need to provide

You must bring the actual data — this prompt does not have access to your systems. Export and paste (or attach as files) the following, covering the exact period in question:

1. **Billing/usage export** from your LLM provider (OpenAI Usage API, Anthropic Admin/usage API, or your gateway's billing export) — ideally one row per request or per time bucket, with: timestamp, model, token counts, dollar cost, and whatever identifier the provider gives you (API key, key hash, or project/org ID).
2. **Observability metadata export** from whatever you use to log requests (Langfuse, Datadog LLM Observability, your own app logs) for the *same period* — request-level rows with: API key, session ID, timestamp, endpoint/route, and user-agent or source IP if you have them.
3. **Your tenant list**, with whatever partial mapping you already know: which API keys were issued to which tenants (even if you only know some of them), each tenant's rough signup/active date range, and any endpoint patterns that structurally identify a tenant (e.g. a URL containing the tenant's slug or ID).
4. *(Strongly recommended, optional)* **An overlapping period where you DID tag tenant_id** — even a short recent window. This lets the reconstruction be validated against ground truth instead of just asserted.

If you're missing (1) or (2), stop — there is no version of this that works without the raw request-level exports. Don't try to proceed on vibes.

## The procedure to run

Once you've pasted/attached the data above, work through these steps and show your work at each one:

1. **Align the two exports.** Match billing rows to observability rows by API key (or key hash) and timestamp proximity. Call out any requests that appear in one export but not the other, and total the dollar amount of that coverage gap — don't just drop it silently.

2. **Classify each API key.** Using the tenant list, mark each key as either a *unique key* (used by exactly one tenant, per your records) or a *shared key* (used across multiple tenants — common for pooled/internal infrastructure).

3. **Score each request/cluster into a confidence tier:**
   - **High** — a unique key confirmed to one tenant, or an endpoint that structurally names the tenant (e.g. `/tenants/acme/...`).
   - **Medium** — a session or timing cluster that lines up tightly with one tenant's known active window, with no other tenant active in that window, but without a unique key to confirm it.
   - **Low** — a shared key and/or overlapping activity windows across tenants, where the best you can do is a proportional statistical split (e.g. by relative usage share, if you know it independently).
   - **Unattributed** — nothing ties the request to any specific tenant. Keep this as its own line item; never force it onto a tenant's total.

4. **Calibrate if you provided an overlapping tagged period.** Hide the real tenant_id field from that period, re-run steps 1–3 on it as if it were untagged, then compare what the reconstruction guessed against the real answer. Report the measured accuracy per tier (e.g. "High-tier guesses matched the real tenant 97% of the time by dollar value; Medium-tier matched 61%"). If you didn't provide a calibration period, say plainly that the tiers below are uncalibrated estimates, not measured accuracy.

5. **Add it all up per tenant**, keeping High / Medium / Low / Unattributed as separate numbers — never blend them into one misleadingly clean figure. Also report the total coverage-gap dollars from step 1.

6. **Write one line per tenant explaining the methodology** — what signal(s) actually drove that tenant's number (e.g. "100% from a unique API key, no guessing involved" vs. "60% unique key, 40% inferred from timing correlation against a key three tenants shared").

## Output format to produce

```
## Per-Tenant Cost Reconstruction — <period>

Calibration: <either "Validated against tagged period <dates>: High-tier accuracy X%,
  Medium-tier accuracy Y%" OR "No overlapping tagged period provided — all figures below
  are uncalibrated estimates.">

| Tenant | High confidence | Medium confidence | Low confidence (inferred) | Tenant total | Methodology |
|---|---|---|---|---|---|
| <tenant name> | $X | $X | $X | $X | <one line on what signal drove this> |
| ... | | | | | |
| Unattributed | — | — | — | $X | No key/session/endpoint signal ties this spend to any tenant |

Coverage gap: $X of billed spend had no matching record in the other export.
Total period spend: $X (should equal High + Medium + Low + Unattributed + Coverage gap;
  if it doesn't match your billing total, say by how much and why).
```

Follow the table with a few plain-language sentences: which tenants are solidly known versus best-effort, and what the honest headline number is for whatever you're using this for (e.g. "for the chargeback dispute, $14,200 of Acme's $19,800 is high-confidence and defensible; the remaining $5,600 is a statistical estimate and should be presented to them as such, not as an exact figure").

## Rules this must follow (do not skip these)

- Never state a Low-confidence or Unattributed number as if it were exact. Always carry the confidence label with it, especially in anything that gets forwarded externally.
- Never fold Unattributed or Low-confidence dollars into a tenant's total just to make the report look tidier. An honest gap beats a fake precise number — fake precision is the exact thing that made people think this was unrecoverable in the first place.
- Never invent an API-key-to-tenant mapping you weren't actually given. If nobody recorded that a key belongs to a tenant, treat it as unmapped — not "probably" that tenant.
- Always say clearly whether the confidence tiers are calibrated (measured against a real tagged period) or just uncalibrated estimates. Don't let a reader assume you measured accuracy you didn't.
- If this report is headed toward a customer dispute or a board/legal context, say explicitly that it's a best-effort forensic reconstruction, not a certified or contractually binding figure.
- If your two exports genuinely can't be joined (no shared identifier format, clocks too far out of sync), say so and stop — don't produce a number that looks real but rests on a broken match.
