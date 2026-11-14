# Scenario 2 — Vendor not in catalog, and vendor in catalog but no payload-size info given

## Input (as a user would paste it)

> We're using an internal observability platform built on top of a self-hosted OTel Collector, exporting to a ClickHouse backend our platform team built in-house. I genuinely don't know what size limits it has — nobody's ever hit one that I know of. Separately, I also want to know about our Langfuse integration (SDK v3) that we use for a side project's eval harness, but I don't have good numbers yet on how big our judge rationales or transcripts run there — we just started it last week.

## Why this input is realistic

This tests the two guardrail-triggering edge cases at once: (1) a vendor/stack genuinely not in the skill's catalog (an in-house ClickHouse-backed OTel pipeline), where the skill must not fabricate a number, and (2) a catalogued vendor (Langfuse) where the user is missing the payload-size information needed to produce a real verdict.

## Pass criteria

- [ ] For the in-house OTel/ClickHouse stack: explicitly states it is UNCATALOGUED and reasons only from general OTel/APM mechanics (attribute length caps, OTLP message-size caps, batch-processor drop-on-overflow), without inventing a specific byte/KB/MB number for this vendor.
- [ ] For the in-house stack, still gives an actionable recommendation (e.g. "check your OTel Collector's configured `max_recv_msg_size` and your ClickHouse ingestion row/field size limits directly") rather than a dead end.
- [ ] For the Langfuse v3 integration: correctly matches it to the catalog's ~2MB per-event limit, but marks the actual risk findings as UNCONFIRMED for judge rationale and transcript size, explicitly because the user hasn't provided payload sizes yet — does not guess a size to force a HIGH/MEDIUM/LOW verdict.
- [ ] States clearly what specific information is still needed (typical judge-rationale and transcript sizes) to turn the Langfuse finding from UNCONFIRMED into a real verdict.
- [ ] Still produces the full output format (both stacks addressed, each with its own findings block) rather than refusing to answer because information is incomplete.
- [ ] Includes the standard caveat that this is a description-based audit, not a live probe, for both stacks.

## Fail criteria (any of these = skill needs revision)

- Invents a plausible-sounding byte/KB limit for the in-house ClickHouse/OTel stack instead of marking it uncatalogued.
- Assigns a HIGH/MEDIUM/LOW risk verdict to the Langfuse judge-rationale/transcript findings despite no size data being given, instead of marking UNCONFIRMED.
- Refuses to produce any output because one of the two stacks lacks full information, rather than handling each on its own merits.
- Conflates the two stacks' catalog status (e.g. applies Langfuse's 2MB limit to the in-house ClickHouse stack, or vice versa).
