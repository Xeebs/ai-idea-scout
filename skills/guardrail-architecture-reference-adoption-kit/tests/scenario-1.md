# Scenario 1 — Mid-size SaaS team with a RAG support bot and partial coverage

## Input

A team describes their setup for a customer-support RAG chatbot built on an in-house agent framework:

> "We've got a support bot that answers questions by pulling from our Zendesk knowledge base and our internal wiki, then answering with Claude. Before we send anything to the model, we run a cheap keyword blocklist to catch obvious profanity or competitor-name mentions — nothing fancier than a list of banned words. We don't do anything to the documents we retrieve from the knowledge base before they go into the prompt — we just concatenate the top 5 chunks. After the model answers, we have a human support lead spot-check about 10% of transcripts each week for anything that looks wrong, but there's no automated check before the answer goes back to the customer. The bot can also call a 'create_refund_ticket' function — the model decides the refund amount and ticket category itself, and the function just fires with whatever arguments the model passes."

## Expected output (pass/fail checklist)

- [ ] Produces a 4-row coverage map (pre-inference, retrieval-time, post-inference, tool-call-time) — not fewer, not more rows, and retrieval-time is NOT marked N/A (they do RAG).
- [ ] Pre-inference marked `PARTIAL` (a keyword blocklist exists but is not a purpose-built classifier) — not `COVERED` and not `MISSING`.
- [ ] Retrieval-time marked `MISSING` (no scan of retrieved KB/wiki chunks before they're concatenated into the prompt).
- [ ] Post-inference marked `PARTIAL` (human spot-check exists but is manual, sampled at only 10%, and not an automated gate before the response ships) — a correct output recognizes this is not `MISSING` (something exists) nor `COVERED` (it's not a dedicated automated check).
- [ ] Tool-call-time marked `MISSING` — the `create_refund_ticket` call has zero argument validation and the model controls both amount and category with no constraint.
- [ ] Every `PARTIAL`/`MISSING` row names at least one specific, real model/technique (e.g., Llama Guard/Prompt Guard or Granite Guardian for pre-inference; an injection scanner applied to retrieved chunks for retrieval-time; Granite Guardian/output classifier for post-inference; argument-schema validation + allow-list/spending-cap for tool-call-time) — generic phrases like "add more checks" anywhere in a gap row is a fail.
- [ ] The "biggest gap" callout correctly identifies the `create_refund_ticket` tool-call gap as the most consequential (an attacker or a confused model could fire arbitrary refund amounts with zero validation) rather than something less severe like the keyword blocklist.
- [ ] Includes the caveat line that this is a converged-but-unofficial pattern, not a certified standard.
- [ ] Does NOT produce a full redesign/deployment plan or config code unprompted.
- [ ] Does NOT claim the team has any check they didn't describe (e.g., does not assume they have rate limiting or PII detection just because it's common).

## Fail conditions
- Treating the 10% manual spot-check as `COVERED` (it is not automated or complete) or as `MISSING` (something does exist).
- Marking retrieval-time `N/A` (they explicitly do RAG).
- Giving only generic advice instead of naming real models/techniques per gap.
