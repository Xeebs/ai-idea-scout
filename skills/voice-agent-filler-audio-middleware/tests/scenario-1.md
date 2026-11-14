# Scenario 1 — Insurance claims intake voice bot

## Input

A team runs a phone voice agent for first-notice-of-loss (FNOL) insurance claims intake, built on LiveKit Agents. They paste:

> Tools:
> - `lookup_policy_status(policy_number)` — checks if a policy is active and what coverage it has. Logs show p50 320ms, p95 900ms.
> - `file_claim(policy_number, incident_details)` — writes a new claim record to the core claims system. Logs show p50 1.8s, p95 6.5s (the claims system is a legacy mainframe, slow during business hours).
> - `check_repair_shop_availability(zip_code)` — calls a third-party network of partner repair shops. No logs yet, but engineering estimates "a few seconds, sometimes it just hangs for 10+ seconds if the partner API is degraded."
> - `get_adjuster_callback_slots(policy_number)` — reads an internal scheduling calendar. p50 150ms, p95 400ms.
>
> Tone: calm and reassuring, this is often someone's car accident or home damage. No chipper language.
> Barge-in detection: we have VAD-based interruption but haven't load-tested it under real call volume, so treat it as "unknown reliability."

## Pass criteria

- `lookup_policy_status` and `get_adjuster_callback_slots` are both correctly marked "No filler needed" (both p50 and p95 are below the 700ms/1.5s default threshold) — the skill must not invent filler phrases for them.
- `file_claim` is correctly flagged as needing filler (p50 1.8s > 700ms) AND gets an escalation ladder (worst-case 6.5s is well over 3x the 700ms threshold) with at least an initial line and an escalation/fallback line.
- `check_repair_shop_availability` is classified `external-passthrough`, and its "a few seconds, sometimes 10+ seconds" description is treated as valid approximate latency data (not rejected as "no data") — it gets a filler phrase and should get an escalation ladder given the stated worst case.
- All filler/escalation phrasing is calm/reassuring, with no chipper tone ("Great news!", exclamation-heavy) and no phrase implying the claim is done before `file_claim` resolves.
- The barge-in-reliability warning appears in Open Flags for every flagged tool, since the team explicitly said reliability is unknown.
- Output includes all five required sections (coverage table, phrase library, escalation ladders, cancellation policy, open flags) and is usable as a handoff spec without further clarifying questions needed for the tools that had adequate data.

## Fail conditions

- Any tool below threshold gets a filler phrase anyway.
- `file_claim` or `check_repair_shop_availability` gets no escalation ladder despite multi-second worst cases.
- The barge-in warning is omitted despite "unknown reliability" being explicitly stated.
- Any phrase sounds chipper or implies false completion ("Found your policy and filed your claim!" before `file_claim` returns).
