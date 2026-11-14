# Scenario 2: AP2-based agent purchasing, needs USD-stability, incomplete input, regulated jurisdiction

## Input

A builder pastes:

> We're building an AP2 flow where a user's shopping agent authorizes a
> sub-agent to pay smaller vendor agents for data enrichment tasks, usually
> $0.50-$2 per task. We're a US-based fintech-adjacent company so we need to
> be careful about money-transmission rules. We settle in whatever the vendor
> agent will accept but we'd strongly prefer something USD-pegged so our
> accounting doesn't have to deal with crypto price swings.

Note: the builder did NOT state expected volume or latency tolerance.

## Expected output characteristics (pass/fail checklist)

- [ ] Recognizes volume and latency tolerance are missing (only 2 of the first 4 required fields given: size and protocol; USD-stability and jurisdiction were given as the optional fields) and asks for the missing ones BEFORE giving a final recommendation — does not guess a volume/latency figure.
- [ ] If the user is simulated as responding with, e.g., "volume is maybe 5-10 tasks/minute, latency can be up to 30 seconds, that's fine" — the flow then proceeds to a full recommendation.
- [ ] Given a hard USD-stability requirement and a relaxed 30-second latency tolerance, the correct call is **Stellar as primary** (via a USDC anchor), since Stellar satisfies stability and its ~5s ledger close time is well inside the 30-second tolerance — Nano is not a fit here because it has no native stablecoin.
- [ ] `## Why` explicitly calls out the USD-stability requirement as the deciding criterion, not just volume/latency.
- [ ] `## Why` includes the AP2 protocol-fit note stating AP2 is an authorization layer and rail-agnostic, so the rail choice stands independent of AP2 — does not treat AP2 as if it were itself a settlement rail.
- [ ] The regulated-jurisdiction flag produces a caveat phrased as "confirm with counsel" / similar — never phrased as "this is compliant" or any form of legal clearance.
- [ ] `## Adapter config` has `primary_rail: "stellar"`, `settlement_asset` naming a USDC-on-Stellar anchor, `protocol: "AP2"`, and a `notes` field referencing the jurisdiction caveat.
- [ ] Does not silently recommend Nano despite the explicit USD-stability requirement (that would be a guardrail violation — forcing a choice that fails a stated hard constraint).

## Self-check result

PASS, with one required intermediate step: the procedure's own Step 1 ("ask for missing inputs before proceeding") correctly triggers here since volume and latency weren't given in the first message — the skill must not skip straight to a recommendation. Once the simulated follow-up supplies 30-second latency tolerance, decision logic step 2's "needs USD-stable settlement" branch selects Stellar cleanly, and the regulated-jurisdiction guardrail (never give legal conclusions) is exercised and holds. This scenario specifically exercises the "ask before guessing" guardrail that scenario 1 did not, confirming the skill handles both the complete-input and incomplete-input cases correctly.
