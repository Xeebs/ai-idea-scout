# Scenario 1 — Nightly product-enrichment job with real degeneration in the samples

## Input (as a user would paste it)

**Job description**: We run Ollama with `mistral:7b-instruct` every night at 2am to enrich about 400 new product rows added to our catalog that day — it reads the raw supplier description and title, and writes a cleaned marketing description plus 3-5 SEO keywords. Nobody reviews the output; it writes straight to the `products.description` and `products.seo_keywords` columns, which go live on the storefront the next morning.

**Output contract**: We expect a JSON object: `{"description": "<100-400 chars>", "keywords": ["k1","k2","k3"]}`. No automated check for this today — we just trust the model to follow the prompt's format instructions.

**Sample outputs** (pasted verbatim, 6 of them):
1. `{"description": "Premium stainless steel water bottle, 32oz, keeps drinks cold for 24 hours and hot for 12. Leak-proof lid, BPA-free.", "keywords": ["water bottle", "stainless steel", "insulated"]}`
2. `{"description": "Soft cotton crew neck t-shirt in classic fit, available in six colors. Machine washable, pre-shrunk fabric.", "keywords": ["t-shirt", "cotton", "crew neck"]}`
3. `{"description": "Durable durable durable durable durable durable durable durable durable durable durable durable backpack with multiple compartments.", "keywords": ["backpack", "durable", "durable"]}`
4. `{"description": "Wireless earbuds with active noise cancellation and 8-hour battery life. Includes charging case and three ear tip sizes.", "keywords": ["earbuds", "wireless", "noise cancelling"]}`
5. `{"description": "Ergonomic office chair with lumbar support`  *(output cuts off here, no closing brace or keywords field)*
6. `{"description": "Ceramic coffee mug, 12oz, dishwasher and microwave safe, matte finish available in four colors.", "keywords": ["mug", "ceramic", "coffee"]}`

**Downstream consumer**: Writes directly to live storefront product pages — a bad description or malformed JSON either shows garbage text to customers or (if the JSON parse fails) leaves the old supplier-raw description in place silently, which nobody would notice since it still "looks like text."

**Known incidents**: None formally logged, but a coworker mentioned a product page once showed a weirdly repetitive description a few weeks ago — no ticket was filed.

**Existing downstream validation**: None — the enrichment script just writes whatever string comes back, wrapped in a try/except that falls back to the raw supplier text on a JSON parse error (but doesn't alert when that fallback triggers).

## Pass criteria

- [ ] Detectability matrix produced as an actual table with all four dimensions (length/shape, schema conformance, repetition/degeneration, semantic correctness), each marked with a status and reasoning tied to what was actually described.
- [ ] Schema conformance marked BLIND SPOT or PARTIALLY-DETECTABLE (there's a silent fallback on parse failure, but no alert) — not CONFIRMED-DETECTABLE, since nothing alerts when the fallback triggers.
- [ ] Findings from sample outputs explicitly flags sample #3 (the "durable durable durable..." repetition loop) and sample #5 (the truncated/cut-off JSON) as real, already-happening anomalies — not just theoretical risks. This is the single most important check: the skill must catch what's sitting in the data it was handed, not just produce generic advice.
- [ ] Recommended plan includes a concrete repetition/degeneration check (e.g. n-gram repetition ratio) and a concrete schema validation check, each with a stated threshold-setting approach and a rough build-cost estimate.
- [ ] Baseline maturation timeline gives a wall-clock estimate consistent with a nightly (daily) cadence against a stated run-count floor (e.g. "~3-4 weeks for a 20-30 run floor").
- [ ] Build-vs-don't-build verdict is an explicit yes (worth building now) given live-customer-facing downstream impact and already-observed-but-unflagged degeneration — not a hedge.
- [ ] Ceiling section explicitly states that none of these checks would catch a well-formed, schema-valid description that is simply factually wrong (e.g. wrong material, wrong capacity) — stated as its own paragraph, not buried.
- [ ] Does not recommend writing the actual monitoring code as part of its own output — stays at plan level.

## Fail conditions

- Treats sample #3 or #5 as fine, or doesn't analyze the pasted samples at all.
- Marks semantic correctness as detectable by any of the recommended statistical/structural checks.
- Produces a generic "add observability" answer without naming the four specific checks tied to this job's actual dimensions.
- Omits the build-vs-don't-build verdict or hedges indefinitely.
