# Scenario 1: Multi-channel customer support memory (expect multiple FAILs)

## Input (what the user pastes)

"We run three channel bots — chat, email, and a phone IVR agent — that all serve the same customers. Every interaction gets appended as a row to an `events` table, keyed by `customer_id`, with an auto-increment `id` but we don't use it for anything downstream. Separately, there's a `customer_summary` table with one JSON blob per customer that each agent reads before responding, so it knows the customer's history.

The summary gets rebuilt two ways: a nightly batch job regenerates it for every customer from all their events, and also any agent can trigger an on-demand rebuild mid-conversation if it thinks the summary looks thin. The rebuild job does this: first it runs an UPDATE to mark all the customer's events as `summarized = true`, then a few seconds later (after calling our summarization LLM) it runs a second UPDATE to overwrite the `customer_summary.blob` column with the new JSON. Agents read `customer_summary.blob` straight out of a 10-minute Redis cache in front of that table — whichever version is in cache when they ask is what they use, no comparison to anything else. All three channel bots can be talking to the same customer on different channels at the same time (e.g. the customer emails support while also on a live chat), so two rebuilds can legitimately fire close together for the same customer_id."

## Procedure to run

Apply the SKILL.md six-scenario audit to the description above.

## Expected output characteristics (pass/fail criteria for the skill output)

- [ ] Scenario 1 (stale-read-after-write): scored **FAIL** — the 10-minute Redis cache has no comparison to log/event state at all, so a reader can serve a 10-minute-old summary with no way to know new events landed.
- [ ] Scenario 2 (non-atomic consolidation): scored **FAIL** — the "mark summarized=true" update and the "overwrite blob" update are two separate statements seconds apart (LLM call in between), so a reader could see events marked summarized but the old blob still in place, or vice versa.
- [ ] Scenario 3 (lost update from concurrent writers): scored **FAIL** — two on-demand rebuilds (or a nightly + an on-demand) for the same customer_id racing is explicitly described as possible ("two rebuilds can legitimately fire close together"), and nothing in the description merges them — whichever finishes last silently overwrites the blob.
- [ ] Scenario 4 (no staleness signal exposed): scored **FAIL** — `customer_summary.blob` is read with no as-of marker at all; agents have no way to know how fresh it is.
- [ ] Scenario 5 (duplicate/conflicting rebuilds): scored **FAIL** or at minimum flagged as a real risk — the on-demand trigger has no mention of a lock/dedup, and it's explicitly stated concurrent triggers for the same customer are possible.
- [ ] Scenario 6 (torn read on projection): the skill should recognize the blob overwrite itself is likely a single-column UPDATE (plausibly atomic at the row level) and score this PASS or UNKNOWN rather than FAIL — a good output does NOT fail every single scenario reflexively; it should distinguish this one from the others.
- [ ] Overall verdict: **NOT SAFE FOR CONCURRENT USE** (FAILs on both scenario 1 and 3 trigger this per the stated rule).
- [ ] Fixes list names concrete, minimal changes tied to this architecture — e.g. "add an offset/last-event-id marker to customer_summary and compare against events table on read," "wrap the summarized-flag update and blob overwrite in one transaction," "add a per-customer lock or last-offset-based idempotent upsert for the rebuild trigger" — not a generic "rebuild your memory system with event sourcing."
- [ ] Does not fabricate facts not in the description (e.g. does not assume Postgres row updates are atomic without the user naming the engine as the reasoning — the `events`/`customer_summary` tables aren't named as any specific DB).

**FAIL the skill run if**: it scores everything PASS, scores everything FAIL without distinguishing scenario 6, gives no concrete fix per FAIL, or fails to reach NOT SAFE FOR CONCURRENT USE as the overall call.
