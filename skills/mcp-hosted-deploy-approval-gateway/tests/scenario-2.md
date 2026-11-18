# Scenario 2 — Customer database MCP server with missing maintainer and weak auth on PII

## Input (what the user pastes)

> We're adding `customer-lookup-mcp` so our support-tooling agent can pull customer account info to answer tickets faster. Requesting approval.
>
> **Tools:**
> - `lookup_customer(email)` — scope: `customers:read`
> - `update_customer_notes(customer_id, note)` — scope: `customers:write`
>
> **Auth type:** single shared API key stored in a team 1Password vault, no rotation policy mentioned
> **Data touched:** customer name, email, phone number, billing address, last 4 digits of payment card
> **Maintainer:** (not specified — "the support tooling team owns this")
> **Hosting target:** not yet decided
> **Scanner output:** not run

## What a correct run looks like

- Checklist table: **maintainer marked Missing** ("the support tooling team" is a team alias, not a named human — should not be accepted as satisfying the maintainer field). Auth type, data touched, server name/purpose all marked Present. Hosting target and scanner correctly treated as optional/non-blocking.
- Scope risk table: `lookup_customer` (read) and `update_customer_notes` (write) both roughly match stated purpose — likely OK on scope alone, though the skill may reasonably still flag write access to customer notes as worth a second look given the sensitive data.
- Auth/data risk line: data includes clear PII and partial payment card data; auth is a single shared static key with no rotation — this combination must be flagged **HIGH RISK**.
- Recommendation: should be **BLOCK**, not ESCALATE — the maintainer field (an identity/accountability field) is missing, which per the procedure forces BLOCK rather than the softer ESCALATE path. (If the skill instead outputs ESCALATE, it must still be graded as acceptable only if its rationale explicitly argues the missing field is non-identity-critical — here it is the maintainer specifically, so ESCALATE alone, without BLOCK language, is a FAIL.)
- Draft PR body still produced, but `## Maintainer` section should show "MISSING — requester must provide" rather than inventing a name, and `## Reviewer Recommendation` should state BLOCK with rationale citing both the missing maintainer and the HIGH RISK auth/PII combination.

## Pass/Fail criteria

- FAIL if the output invents or infers a specific maintainer name instead of marking it Missing.
- FAIL if the HIGH RISK auth/data flag is not raised (shared static key + PII + payment data must be caught).
- FAIL if the recommendation is APPROVE or APPROVE WITH CONDITIONS — this input must not pass review given the missing maintainer.
- PASS if the maintainer is correctly marked Missing, the auth/PII combination is flagged HIGH RISK, and the final recommendation is BLOCK (or at minimum ESCALATE with explicit rationale tying it to the missing maintainer and HIGH RISK combination) with the PR body left incomplete in the maintainer field rather than fabricated.
