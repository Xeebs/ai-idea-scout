# Scenario 2 — CRM support bundle, missing "expected tool" and a system prompt in play

## Input (what the user pastes)

> **User request:** "Can you pull up the account history for customer Jane Ortiz, she's asking why her last two invoices look different."
>
> **Tool that got called:** `create_support_ticket`
> Description: "Opens a new support ticket for a customer issue. Captures customer name, issue summary, and priority. Use whenever a customer raises a question or problem."
>
> **Other tools available:**
> - `lookup_customer_account` — "Retrieves account details, invoice history, and billing records for a named customer."
> - `send_customer_email` — "Sends a templated email to a customer's registered address."
>
> **Correct tool:** not stated by the user — must be inferred.
>
> **System prompt (provided):** "You are a support assistant. Always open a ticket first when the user mentions a customer by name so nothing falls through the cracks, then follow up with any lookups needed."

## Pass criteria

- [ ] Incident Summary correctly infers `lookup_customer_account` as the likely correct tool (the request is clearly asking to retrieve billing/invoice history, not to open a ticket) AND explicitly marks this inference as unconfirmed since the user didn't state it.
- [ ] Root Cause: Description Overlap section still runs the description diff (e.g., "mentions a customer by name" vs. "retrieves ... billing records for a named customer") even though the real driver here is the system prompt — must not skip this step.
- [ ] System Prompt Interference section is present (not omitted, since one was provided) and correctly identifies the keyword rule — "Always open a ticket first when the user mentions a customer by name" — as a prompt-level override that would cause this exact misroute regardless of how good the tool descriptions are.
- [ ] Output distinguishes the two failure modes: notes that the system prompt rule, not primarily the tool description overlap, is the dominant cause here, and recommends editing the system prompt (e.g., removing the blanket "always open a ticket" rule or scoping it to only apply when no specific data request is present) rather than only rewriting `create_support_ticket`'s description.
- [ ] Suggested Description Rewrite section still offers a tightened description for `create_support_ticket` (e.g., excluding "...Do NOT use this when the user is asking to retrieve or review existing account/invoice data — use lookup_customer_account for that.") as a secondary, defense-in-depth fix.
- [ ] Regression scenarios include at least one case that specifically tests the system-prompt rule in isolation (e.g., "Jane Ortiz says the app crashed when she tried to log in" -> create_support_ticket, confirming the rule is still correct for genuine new issues) alongside the data-lookup near-miss.
- [ ] Confidence & Limits explicitly flags that the inferred "correct tool" is unconfirmed and recommends the user verify it.

## Fail conditions

- Fails to mention the system prompt at all, or treats the tool-description rewrite as a sufficient fix on its own when a blanket keyword rule in the system prompt would still force the same misroute.
- States the inferred correct tool as a certain fact rather than an explicit inference.
- Skips the description-diff step entirely because a system prompt was involved.
