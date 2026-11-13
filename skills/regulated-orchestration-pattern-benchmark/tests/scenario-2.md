# Scenario 2: Financial-document extraction team (direct benchmark domain)

## Input a real user would provide

> We're a mid-size commercial lender automating extraction from signed loan agreements and the accompanying financial statements borrowers submit. Volume is around 1,200 documents/month, mostly standard 15-30 page commercial loan agreements plus 2-3 years of financial statements per borrower.
>
> Target fields (22 total): borrower legal name, loan amount, interest rate (fixed/variable + index), maturity date, covenant list (financial covenants like debt-service coverage ratio minimums), collateral description, guarantor names, prior-year revenue, prior-year net income, current ratio, debt-to-equity ratio, and 11 more standard loan-file fields.
>
> High-stakes fields: covenant list (missing or misreading a covenant threshold could mean we fail to flag a borrower who's out of compliance), debt-service coverage ratio, debt-to-equity ratio — these directly feed our credit risk model. A false positive here (flagging a compliant borrower as non-compliant) costs us an analyst's time to double check; a false negative (missing an actual covenant breach) is a real credit risk exposure we might not catch until the next audit.
>
> Low-stakes fields: borrower legal name, loan amount, maturity date, guarantor names — we cross-reference these against our loan origination system anyway, so an extraction slip gets caught.
>
> Labeled sample (4 documents):
> 1. $2.4M term loan — DSCR covenant minimum 1.25x, actual reported 1.41x (compliant), debt-to-equity 0.62
> 2. $850K revolving line — DSCR covenant minimum 1.15x, actual reported 1.09x (breach), debt-to-equity 0.88
> 3. $5.1M term loan — DSCR covenant minimum 1.30x, actual reported 1.33x (compliant, borderline), debt-to-equity 0.71
> 4. $1.2M equipment loan — no DSCR covenant, debt-to-equity covenant minimum 1.0x max, actual reported 0.95x (breach)
>
> Constraints: cost ceiling around $0.12/document (these are long, dense documents so we expect higher per-doc cost than simpler forms), no hard latency requirement since this runs as an overnight batch job, and we most want to avoid missing covenant breaches.

## What a passing output does

- [ ] Correctly identifies this as financial-document extraction — the domain the Kulkarni benchmark directly covers — and sets **confidence explicitly to HIGH** for the covenant/ratio fields, since this matches the benchmark's actual study domain.
- [ ] Distinguishes the reasoning-dependent, high-stakes fields (covenant compliance determination, DSCR, debt-to-equity) from the simple key-value low-stakes fields (borrower name, loan amount, maturity date, guarantor names).
- [ ] States the error-cost asymmetry explicitly: missing a covenant breach (false negative) is a real credit-risk exposure, while a false positive just costs analyst double-check time — and uses this to justify leaning toward reflexive or hybrid for the covenant/ratio fields specifically.
- [ ] Gives a concrete recommendation using the benchmark table — likely reflexive or hybrid for the covenant/ratio fields (given "most want to avoid missing covenant breaches" plus a $0.12/doc ceiling that can plausibly accommodate hybrid's 1.15x or even reflexive's 2.3x on a batch overnight job with no latency pressure), paired with sequential or parallel for the low-stakes administrative fields.
- [ ] Explicitly notes that because this is overnight batch with no latency constraint, the relative-cost multiplier matters more than wall-clock speed, which should push the reasoning toward reflexive/hybrid rather than parallel fan-out for the high-stakes fields.
- [ ] Validation plan references checking covenant-breach detection specifically against documents 2 and 4 (the two breach cases in the labeled sample) and borderline compliance on document 3.
- [ ] Still includes caveats (e.g., noting the benchmark's 25 field types and specific model set may not include every model/field type this team uses) even at HIGH confidence — HIGH confidence on domain match is not the same as "no caveats needed."

## What a failing output looks like

- Treats this identically to a non-finance domain and assigns LOW-MODERATE confidence despite this being the benchmark's actual study domain.
- Recommends sequential or parallel for the covenant/ratio fields purely to minimize cost, ignoring the stated priority to avoid missing covenant breaches and the fact that there's no latency constraint to justify that tradeoff.
- Fails to distinguish high-stakes reasoning fields from low-stakes lookup fields and gives one pattern for all 22 fields.
- Omits reference to the specific breach cases (documents 2 and 4) in the validation plan.
