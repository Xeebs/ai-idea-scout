# Scenario 1: Support-triage → billing escalation

## Input (as a user would paste it)

> We're building a 3-agent support system for an e-commerce platform.
>
> - **Triage agent**: reads the incoming support ticket (subject, full message body, customer account ID) and classifies it as billing, shipping, or general.
> - **Billing agent**: when triage classifies a ticket as billing, it receives the *entire original ticket object* — subject, full message body (which often contains the customer typing out their card number or last-4 digits when disputing a charge, plus their shipping address in the signature block), and account ID — and resolves the dispute by looking up the charge in Stripe via a `get_charge(charge_id)` tool call, then drafts a refund or decline.
> - **Shipping agent**: receives only the account ID and order ID when triage classifies a ticket as shipping — no message body.
> - All three agents log their full input and output to a shared Datadog log stream for debugging, including whatever was in the ticket body.
> - There's no shared memory store — just the ticket object getting passed directly agent-to-agent.
>
> Sensitive categories in play: PII (name, address), payment data (card digits), account identifiers.
>
> Review this for likely privacy leak paths before we build it.

## Expected output — pass/fail checklist

- [ ] Builds a 3-node handoff graph: triage → billing, triage → shipping, and classifies the ticket body passed to billing as **C2 (inter-agent message)**.
- [ ] Flags the triage → billing handoff as the primary risk: full message body (containing card digits + address) crosses with no redaction declared → `CONFIRMED` (user explicitly said card digits are often present and nothing scopes them out).
- [ ] Classifies the Datadog logging of full ticket bodies as **C6 (logs)** and flags it `CONFIRMED` — raw card digits and address data land in a shared log stream with no redaction mentioned.
- [ ] Classifies the `get_charge(charge_id)` tool call as **C3 (tool input)**; notes whether a charge ID alone is sensitive-category data (lower risk than the raw body) — should not over-flag this one as severely as the C2/C6 instances.
- [ ] Contrasts triage → shipping (account ID + order ID only, no body) as a lower-risk / unflagged or lightly-flagged instance, since no card data or free text crosses there — correctly does NOT treat it the same as the billing handoff.
- [ ] Proposes a concrete fix for the billing handoff: e.g., strip/mask card-digit patterns and address lines from the forwarded body before it reaches the billing agent, or have billing agent fetch only the charge ID and a redacted summary rather than the raw body.
- [ ] Proposes a concrete fix for the logging instance: redact/mask before writing to Datadog, or scrub known sensitive patterns pre-log — not just "add redaction" with no specifics.
- [ ] Explicitly states which of C1/C4/C5/C7 were never mentioned in the input (no final-output description, no tool *output* handling for the Stripe call, no shared memory, no file/export artifacts) — lists these as unmentioned/blind-spot channels.
- [ ] Does NOT claim to have measured an actual leak rate — states this is a static design read, recommends running the real AgentLeak-based CI harness once built.
- [ ] Rollup correctly ranks the billing C2 handoff (or the C6 logging, whichever is deemed worse) as the top fix-first item, both being CONFIRMED and higher-severity than the C3 tool-input instance.
