# Scenario 1 — Customer support email-triage pipeline

## Input (as a user would paste it)

> We run a 3-agent support pipeline:
> 1. **Intake Agent** — reads the raw inbound customer email (plain text, from anyone on the internet, unauthenticated) and produces a plain-text summary: "customer issue in their own words, shortened." Before this summary leaves Intake Agent, we run it through a commercial prompt-injection classifier (flags/blocks if it looks like an attempted instruction) — this is the only security check in the pipeline.
> 2. **Triage Agent** — receives Intake Agent's summary as freeform text, decides a category and priority, and writes both plus the original summary text into a new Zendesk ticket via a `create_ticket(subject, body, priority)` tool call. The `body` field is literally the summary text from Intake Agent.
> 3. **Responder Agent** — reads the open ticket (subject, body, priority) and can call `send_email(to, subject, body)` to reply to the customer directly, using its own LLM-generated reply text which is informed by the ticket body.
>
> Audit this pipeline for cross-agent injection exposure.

## Pass criteria
- [ ] Output includes a Pipeline Map table listing all three agents, correctly marks Intake Agent as untrusted-input = yes, and correctly tiers Triage Agent and Responder Agent as STATE-CHANGING (ticket creation, email send).
- [ ] Flags the Intake Agent → Triage Agent edge: the commercial classifier runs only at/before the Intake Agent's output, and the `create_ticket` call's `body` field is populated directly from that freeform summary — a finding should say the classifier does not clear this edge against a reworded/domain-camouflaged payload.
- [ ] Flags the Triage Agent → Responder Agent edge (or treats it as the same unresolved taint chain): ticket body (ultimately tainted, from the email) feeds Responder Agent's `send_email` tool parameters, which is IRREVERSIBLE/HIGH-STAKES (reaches a third party — the customer — directly) and should be ranked as the highest-severity finding, not lower than the first hop.
- [ ] Each finding includes a specific, named policy rule (e.g., ticket `body`/`subject` must come from a structured/validated field, not freeform summary text; `send_email` parameters must not be populated directly from ticket body text that traces back to the raw email).
- [ ] Does not credit the single classifier with covering the whole pipeline — explicitly calls out that it's a perimeter-only check.
- [ ] Includes a Residual Risk paragraph recommending an attack-replay eval, and does not declare the pipeline "safe."
- [ ] Does not invent unstated details (e.g., does not assume there's human review somewhere that wasn't mentioned).

## Fail criteria
- Treats the classifier as sufficient protection for the whole chain.
- Misses or downplays the Responder Agent's `send_email` edge as the most severe finding.
- Gives a generic "add more input validation" recommendation instead of naming the specific agents/fields involved.
- Declares the pipeline safe/secure without the residual-risk caveat.
