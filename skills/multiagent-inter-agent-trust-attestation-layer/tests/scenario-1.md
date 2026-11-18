# Scenario 1 — Agent-to-agent commerce pipeline (cross-org, high stakes)

## Input

A user building an agent-to-agent procurement pipeline for a mid-size logistics company describes it:

> We have a "Buyer" agent (ours) and a "Supplier" agent (operated by a third-party vendor, talking to us over A2A). The flow is:
> 1. Buyer sends a purchase request to Supplier for a batch of parts.
> 2. Supplier replies with a claim: "Inventory confirmed: 500 units in stock, ready to ship within 48 hours." Our Buyer agent, on receiving this, immediately triggers an escrow payment release of $38,000 to the Supplier's payment rail (x402).
> 3. Separately, our own internal "QA" agent (ours, same org) runs automated tests on code the Buyer agent generates to reconcile invoices, and reports "all reconciliation tests passed" to a "Deploy" agent (ours), which then pushes the reconciliation script to production without further review.
> 4. Occasionally the Supplier agent also sends a free-text claim like "this is our best customer tier, we'll prioritize you," which doesn't trigger any automated action, just gets logged for the account manager to see later.
>
> We got burned once already: the Supplier agent claimed inventory was confirmed, we released payment, and the inventory turned out to be short by 200 units — we had no way to tell beforehand and no record to dispute it with afterward. We want a trust policy before we build any actual signing/ledger system.

## Expected output characteristics

- A policy table with at least 3 distinct claim types: (1) Supplier's inventory-confirmed claim, (2) QA's "tests passed" claim, (3) Supplier's "best customer tier" claim.
- Claim 1 (inventory confirmed → $38k payment release) classified as **Irreversible/high-stakes**. Verifiability should be marked checkable (in principle, against the supplier's own inventory system or a corroborating check) or checkable-with-effort — and flagged for mandatory attestation referencing concrete evidence (e.g., a hash/reference to an inventory snapshot), plus the cross-org boundary rule applied (Supplier is third-party) raising its tier/requirement further.
- Claim 2 (QA tests passed → auto-deploy to production) classified as **Irreversible/high-stakes** (or at least reversible-but-costly) and **checkable** (test results are a ground-truth artifact) → attestation recommended referencing the actual test-run result/hash.
- Claim 3 ("best customer tier," logged only) classified as **Informational**, **unverifiable judgment**, attestation marked optional, explicitly flagged as not scoreable the same way as the other two.
- A trust-score threshold stated concretely per claim type (not vague "monitor trust" language) — e.g., naming a threshold or rule for when the Supplier's claims require human sign-off before further escrow releases.
- Priority narrative calls out the inventory-confirmed claim as the top priority and explicitly references the past incident (payment released on an unverified claim with no dispute record) as the gap being closed.
- Ends with the required disclaimer line that this is a draft policy, not working signing/ledger/scoring infrastructure.
- Does not invent any additional agents or claims beyond what the user described.

## Pass / fail

**Pass** if all three claim types appear, the inventory claim and QA claim are both correctly tiered high-stakes with attestation requirements tied to concrete evidence, the cross-org escalation rule is visibly applied only to the Supplier (not the internal QA agent), and the disclaimer line is present.

**Fail** if the skill treats all three claims identically (no stakes/verifiability differentiation), omits the cross-org boundary adjustment, invents claims/agents not in the description, or presents the output as if it were a working trust-scoring system rather than a draft policy.
