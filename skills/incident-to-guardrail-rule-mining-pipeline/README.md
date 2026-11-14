# Incident-to-Guardrail Rule Mining Pipeline

A prompt template for turning a batch of real support tickets or incident reports about an AI/bot system into draft guardrail rule proposals — a one-shot trial you can run by pasting ticket text into any AI chat tool (Claude, ChatGPT, etc.). No installation, no API connector required.

## When to use this

Use this when you have a pile of "the AI did something wrong" tickets — things like "the support bot leaked another customer's order details," "the moderation filter blocked a completely normal question about knife sharpening," "the assistant gave specific medication dosage advice" — and you suspect some of them are actually the *same underlying gap* showing up as separate, unrelated-looking complaints. Instead of waiting for an engineer to notice the pattern by memory, you paste the batch in and get back grouped clusters plus a concrete candidate rule for each one.

This is a one-shot manual trial, not a live monitoring system. It does not connect to your ticketing platform (Zendesk, Intercom, Jira, PagerDuty) and does not run continuously — you paste a batch, you get a report, done. If what you actually want is an always-on pipeline watching your live ticket queue, this prompt is a good way to validate the approach first, but the continuous version is a separate build.

This also isn't for red-team test results or eval-judge failure logs — tools like promptfoo's Adaptive Guardrails already turn synthetic test failures into guardrail rules. This is specifically for real production incidents and support tickets from actual users, which is the part nothing else currently automates.

## What to hand over

1. **The raw batch of tickets/incidents** — paste at least 8-10. Fewer than that and there isn't enough volume to cluster meaningfully; the output will say so rather than force a result. Each entry needs at minimum a short description of what happened; a ticket ID or date is helpful but a placeholder label ("Ticket A," "Ticket B") works fine if the real ID is sensitive. Strip customer PII before pasting, or flag it for the assistant to note as needing stripping.
2. **One sentence on what the AI system is** — e.g., "a customer support chatbot for a SaaS billing product" — so the clustering and rules are grounded in your actual product, not generic LLM behavior.
3. **(Optional) any guardrail rules you already have in place** — so proposed rules can be checked against what's already covered instead of duplicating it.

## The prompt

Paste this, with your ticket batch and context filled in:

```
You are mining a batch of production support tickets/incident reports about an AI system into candidate guardrail rule proposals. Here is what the AI system does: [ONE SENTENCE DESCRIPTION].

Here are our existing guardrail rules, if any: [LIST, OR "none currently"].

Here is the ticket/incident batch:
[PASTE AT LEAST 8-10 TICKETS, EACH WITH A SHORT DESCRIPTION AND AN ID/LABEL]

Please:
1. Normalize each ticket into one line: ID, one-sentence summary, and whether it's a MISS (harmful output got through) or a FALSE POSITIVE (a benign request got wrongly blocked).
2. Cluster tickets by shared underlying failure mechanism, not surface wording — state the shared mechanism for each cluster in one clause. Do not force a lone ticket into a cluster it doesn't really share a mechanism with; list it separately as a singleton instead.
3. For each cluster of 2+ tickets, draft one concrete, implementable guardrail rule (not vague advice), citing the specific ticket IDs as evidence.
4. Check each drafted rule against our existing rules (if supplied) — flag if it's redundant or if it should tighten an existing rule instead of being new.
5. Estimate catch-gain (how many MISS tickets in the batch this rule would catch) and false-positive risk (what legitimate use cases this rule's wording could also block) in plain language — don't invent numbers or percentages beyond what's derivable from the batch.
6. Rank clusters by ticket count, largest first, and note this is a proxy based only on this batch, not full incident history.
7. If fewer than 8 tickets were supplied, say so explicitly and treat any clusters as provisional, not evidence-backed.

Output as a Markdown report with these sections, in order:
- Batch Summary (ticket count, excluded non-AI tickets, singleton count)
- Cluster Table (cluster name, ticket IDs, shared mechanism, MISS/FALSE POSITIVE, count — sorted by count descending)
- Rule Proposals (one per cluster: the rule statement, cited tickets, existing-rule check, catch-gain/false-positive estimate)
- Singletons (tickets that didn't cluster, with a note they need more volume)
- Open Questions for Reviewer (anything assumed due to ambiguous input)

Never present a drafted rule as already approved or enabled — these are drafts for a human reviewer. Never invent ticket content or statistics not present in what I pasted.
```

## What you get back

A single report with five sections: a summary of the batch, a table of clusters ranked by size, one detailed rule proposal per cluster (with the exact tickets that justify it and an honest catch-gain/false-positive tradeoff), a list of tickets that didn't have enough company to cluster, and a short list of open questions a human reviewer should answer before approving anything.

## Guardrails — what this will not do

- It will not invent ticket content, counts, or false-positive percentages beyond what you pasted. Thin batches get an honest "not enough volume" note instead of a confident-sounding but fabricated estimate.
- It will not tell you a rule is live or enabled — everything produced is a draft for a human to review and decide on.
- It will not force unrelated tickets into a cluster just to produce a tidier-looking report.
- It will not accept red-team/eval-test failures as input — paste real field tickets and incidents, not synthetic test results.
- It will not pretend to be a live, continuously-running pipeline — this is a one-time trial run on whatever batch you paste.
