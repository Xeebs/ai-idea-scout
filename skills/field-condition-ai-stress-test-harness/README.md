# Field-Condition AI Stress-Test Plan Generator

Paste this whole document into any AI chat tool (Claude, ChatGPT, etc.) along with your answers to the four questions below, and it will produce a field-condition test plan for your AI tool — the specific ways it's likely to break under bad connectivity or low-end hardware, how to test for each one (even without building any new tooling), and a pass/fail checklist you can attach to a release.

## When to use this

You're about to ship (or audit) an AI tool — a cloud-API chat assistant, a WhatsApp/SMS/USSD bot, an on-device model, or a hybrid — into a setting where connectivity is unreliable (2G/3G, frequent drops, high latency) or the hardware is low-end/resource-constrained (low RAM, thermal throttling, small batteries). You want to know what to test before a real user discovers the failure in the field, and you want that plan now, not after someone builds a full automated harness.

## What to provide

1. **Architecture** — which of these four is closest to your tool:
   - (A) Cloud API-based chat/assistant (streamed or non-streamed calls to a hosted model)
   - (B) Messaging-channel bot (WhatsApp, SMS, USSD, or similar, via a third-party provider)
   - (C) On-device/edge inference (model runs locally, no network round-trip for inference)
   - (D) Hybrid (on-device with periodic cloud sync)
2. **Target connectivity profile** — a region/tier if you know it (e.g., "rural sub-Saharan Africa, mostly 2G/EDGE") or raw specifics ("drops every few minutes," "1-2 Mbps when connected, long latency"). If you don't know, say so — you'll be offered a generic tier to pick from instead of having one assumed for you.
3. **Target device profile** (if relevant — matters most for on-device or UI-heavy clients): RAM, known low-end hardware, battery/thermal limits. Skip if it's a pure cloud-API text bot.
4. **Anything already known to break** (optional) — past incident reports, support tickets, informal field feedback. Sharpens what gets prioritized.

## What you get back

A single report with five sections:

1. **Architecture & Profile Used** — which architecture type was identified and which connectivity/device profile is being tested against, stating clearly whether that profile came from your own numbers or was inferred from a named region (and flagged as qualitative if inferred — no invented latency/bandwidth figures).
2. **Prioritized Failure Modes** — the most relevant failure modes for your specific architecture, ranked with silent failures (the tool thinks it worked, it didn't) ranked above loud failures (visible error) above slow-but-working, because silent failures are what quietly kill field pilots.
3. **Test Instructions** — for each failure mode, a concrete way to test it, including a no-tooling fallback (e.g., toggling airplane mode mid-request instead of needing a network-simulation harness), and a note on whether it's testable today or needs a real device lab / provider sandbox.
4. **Pass/Fail Checklist** — a table: Failure Mode | Test Method | Pass Criteria | Status, ready to work through and attach to a release.
5. **Gaps This Plan Can't Close** — an honest line naming what the plan flags but can't fully verify without more infrastructure (e.g., real thermal data on physical hardware, access to a messaging provider's test sandbox).

## The failure-mode logic behind this (so you can sanity-check the output)

- **Cloud API-based chat**: timeout with no retry/fallback, response truncated silently on a mid-stream drop, duplicate requests from naive auto-retry, session/auth token expiring mid-conversation, retry-storm cost blowup.
- **Messaging-channel bot**: "delivered" receipt but the message never reached your backend, out-of-order delivery after reconnect, webhook retry storms, provider rate-limiting during burst reconnects, the bot going silent with no fallback message to the user.
- **On-device inference**: thermal throttling slowing inference over a session, out-of-memory kills on low-RAM devices, slow cold-start model load, storage exhaustion from cached weights/logs, OS backgrounding killing a run mid-inference.
- **Hybrid (on-device + sync)**: everything under on-device inference above (it's still running local inference), plus sync conflicts after a long offline gap, stale cached data served as current, and partial sync leaving an inconsistent state.

The tool picks the 4-6 most relevant failure modes for your specific case — it doesn't dump every category on you regardless of architecture.

## Ground rules this follows

- It will not invent specific latency/bandwidth/packet-loss numbers — it uses qualitative connectivity tiers unless you give it real figures.
- It will not tell you this plan equals a passed test — it's an unexecuted plan and checklist, a planning step before (or instead of) building the full automated harness.
- It will not guess your architecture or connectivity profile if you haven't specified — it asks rather than assumes.
- It will not hand you a generic performance/QA checklist in place of connectivity-drop and device-resource failure modes — it stays scoped to field-condition stressors specifically.
- It will not cite adoption numbers or case-study statistics as if they were facts about your specific tool.

## Example prompt to paste alongside your answers

> Using the Field-Condition AI Stress-Test Plan Generator procedure above: my tool is [architecture], deployed to [region/connectivity specifics], running on [device profile, if relevant]. [Anything already known to break, if any.] Produce the five-section field-condition test plan.
