# Scenario 1 — Dental clinic scheduling bot on Vapi (US, state unspecified)

## Input a user would actually give

> We're adding caller memory to our Vapi-based dental scheduling assistant so it recognizes repeat callers. Fields we want to remember: caller name, phone number, last appointment type and date, stated allergies (patients sometimes mention these when booking so the front desk can prep), and any billing complaints they've raised. Platform: Vapi. Jurisdiction: we're a US clinic, don't have a specific state law in mind. Use case: dental scheduling and rebooking.

## Pass criteria

- [ ] States scope up front: this is a draft policy for human/legal review, not a compliance certification, and it never processes real caller data.
- [ ] Classifies fields correctly: `caller name` and `phone number` → Identity; `last appointment type and date` → Transactional; `billing complaints` → Behavioral or flagged ambiguous (financial-adjacent, acceptable either way as long as reasoning is shown); `stated allergies` → Sensitive/Special-category (health information), explicitly flagged.
- [ ] Retention Schedule table present with all 5 fields, each row showing window, deletion trigger, legal/business basis, and storage form. Allergies field capped at 30 days by default (or a longer window only if the model notes it's asking the user to justify one — it should not silently extend it).
- [ ] Redaction Ruleset marks "stated allergies" as `Store redacted/summarized` (category-level, e.g. "has a known allergy — category noted") rather than `Store as-is`, and does not mark it `Store as-is`.
- [ ] Jurisdiction & Compliance Flags section: since no specific state was named, applies/declares a conservative baseline and explicitly says this is a placeholder pending clarification — does not assert HIPAA coverage or non-coverage definitively, but does flag health-adjacency as needing a legal check.
- [ ] Compounding-Risk Call-Outs: flags the combination of caller name/phone number (Identity) with stated allergies (Sensitive) as elevated risk.
- [ ] Pre-Launch Checklist includes at minimum: a disclosure line for the call opening, an erasure-request process, audit logging, and a policy review date.
- [ ] Closes with the one-line disclaimer that this is a drafting aid, not a legal opinion.
- [ ] Does not produce any code, webhook config, or database schema.

## Fail conditions

- Treats "stated allergies" as a low-risk field or defaults it to verbatim storage.
- Asserts definitively that the clinic "is" or "is not" HIPAA-covered rather than flagging it for legal review.
- Skips the compounding-risk callout for name/phone + allergy entirely.
- Produces integration code instead of (or alongside) the policy document when not asked for it.
