# Scenario 2 — OpenAI Agents SDK Support Triage Router

## Input a user would actually give

> We built a customer support bot on the OpenAI Agents SDK. A **Triage agent** reads the incoming customer message, decides which of two specialist agents should handle it — a **Billing agent** or a **Technical-Support agent** — and hands off using the SDK's default `handoff()`, which just passes the existing conversation history along.
>
> Problem: before handing off, the Triage agent sometimes already tries a couple of quick things itself — like checking if the customer's account is on a known outage list, or noting that the customer mentioned they "already tried restarting the device" — and that gets lost. The Technical-Support agent then asks the customer to restart their device again, which is annoying since they already said they did that.
>
> We only have these two downstream paths right now (Triage→Billing, Triage→Tech-Support), both using the OpenAI Agents SDK's default handoff mechanism.

## Pass criteria

- [ ] Output recognizes this as a branching/routing pipeline with two distinct handoff edges (Triage→Billing, Triage→Tech-Support) and either drafts both or explicitly notes they share the same shape and gives one schema covering both, with a stated routing field (e.g. a `decisions_made` entry recording "routed to Tech-Support because...").
- [ ] Envelope schema includes `errors_encountered` or `open_questions`/`artifacts` capturing "customer already tried restarting the device" so it isn't lost — this is the named failure and must appear concretely in the worked example, not just in the abstract schema.
- [ ] Worked example uses the user's domain terms (Triage, Billing, Tech-Support, outage list, restart) and does not invent a specific customer name, account ID, or outage ticket number that wasn't given — those fields are marked `<< not specified >>` if needed for the example to read naturally, or left generic without being passed off as real data.
- [ ] Output states concretely where the envelope fits into the OpenAI Agents SDK handoff — i.e. passed as part of the handoff input rather than only relying on raw conversation history — not a vague "integrate it somehow."
- [ ] Validation checklist includes a pre-send or post-receive item that would have caught this exact failure (e.g. "confirm any customer-reported troubleshooting steps already attempted are listed in artifacts/open_questions before the Tech-Support agent asks the customer to repeat them").
- [ ] Does not tell the user to adopt a third-party handoff-protocol library or a different framework — works within the stated OpenAI Agents SDK setup.
- [ ] Follows the same six-field-plus-meta schema shape as scenario 1 (consistency of the underlying skill logic across different pipelines), not a bespoke one-off structure invented just for this case.

## Fail conditions

- Misses that there are two handoff edges and treats Triage→Billing and Triage→Tech-Support as if only one handoff exists.
- Fails to explicitly carry forward "customer already tried restarting" into a concrete envelope field.
- Recommends building/installing a general handoff library instead of drafting the schema directly.
