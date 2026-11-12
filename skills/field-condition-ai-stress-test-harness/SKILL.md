---
name: field-condition-ai-stress-test-harness
description: Produces a tailored field-condition test plan (failure modes, test presets, pass/fail checklist) for an AI tool before it ships into a low-bandwidth, intermittent-connectivity, or low-end-device deployment. Use when a team is about to release an AI chat tool, messaging bot, or on-device model into a rural or resource-constrained setting and wants to know what breaks before a real user finds out.
---

# Field-Condition AI Stress-Test Plan Generator

## When to use this
A team is preparing to release or audit an AI tool — a cloud API-based chat assistant, a WhatsApp/SMS/USSD bot, an on-device inference app, or a hybrid of these — that will be used by people on unreliable connectivity (2G/3G, frequent drops, high latency) or low-end/resource-constrained devices (low RAM, thermal throttling, small batteries). They want to know, before building or running a full automated stress-test harness, which failure modes to check and how to check them. This is a planning/audit step, not the harness itself — it produces the test plan a team works through manually or hands to whoever builds the automated version.

## Inputs
**Data source**: Manual — the user describes the tool's architecture (API-based chat, messaging-channel bot, on-device inference, or hybrid) and its target deployment conditions in prose; no API or connector is read automatically.

Specifically, ask for (fill gaps with explicit questions rather than guessing):
1. **Architecture**: which of the four types below, or a description close enough to classify.
2. **Target connectivity profile**: a named region/tier if known (e.g., "rural sub-Saharan Africa, mostly 2G/EDGE"), or raw specifics ("drops every few minutes," "high latency, ~1-2 Mbps when connected"). If the user has no data, offer the generic tier table in Step 2 of the Procedure and ask them to pick the closest match — never silently assume a tier.
3. **Target device profile** (if relevant to the architecture, e.g., on-device inference or any UI-heavy client): RAM, known low-end hardware, battery/thermal constraints. Optional for pure cloud-API/text-bot cases.
4. **Anything already known to break** — prior incident reports, support tickets, or informal field feedback, if they have any. Optional, but sharpens prioritization.

## Procedure
1. **Classify the architecture** into exactly one of:
   - **(A) Cloud API-based chat/assistant** — client calls a hosted model API, streamed or non-streamed.
   - **(B) Messaging-channel bot** — WhatsApp, SMS, USSD, or similar, where a third-party messaging provider sits between the user and the backend.
   - **(C) On-device/edge inference** — model runs locally on the user's hardware, no network round-trip required for inference itself.
   - **(D) Hybrid** — on-device component with periodic cloud sync (e.g., offline-first app that reconciles when connectivity returns).
   If the description doesn't cleanly fit one type, ask a clarifying question before proceeding — do not guess.

2. **Resolve a connectivity/device profile.** If the user gave specifics, use them directly. If they named a region only, map to the closest of these generic tiers (phrased qualitatively — never invent a specific Mbps/latency number not supplied by the user or a cited source):
   - **Tier 1** — stable broadband/Wi-Fi or strong 4G/5G, rare drops.
   - **Tier 2** — 3G/weaker 4G, intermittent drops (seconds to low minutes), moderate latency.
   - **Tier 3** — 2G/EDGE, frequent and sometimes extended drops, high latency, low throughput.
   - **Tier 4** — offline-first: connectivity is the exception, not the default; the tool must function for extended stretches with none at all.
   State which tier you're using and that it's a qualitative stand-in for ITU/GSMA-style connectivity-tier language, not a measured figure, unless the user supplied their own numbers.

3. **Apply the architecture-specific failure-mode checklist** (this is the core logic — do not substitute a generic "test your app" list):
   - **(A) Cloud API-based**: timeout with no retry or user-visible fallback; partial/streamed response silently truncated on a mid-stream drop; duplicate request fired by a naive auto-retry; auth/session token expiring mid-conversation after a long gap; cost blowup from retry storms during flaky connectivity.
   - **(B) Messaging-channel bot**: message shows "delivered" to the provider but never reaches the bot backend (silent loss); out-of-order message delivery after a reconnect; webhook retry storms from the provider during a flaky window; provider-side rate limiting triggered by burst reconnects; bot going silent with no "we're having trouble, try again" fallback message.
   - **(C) On-device inference**: inference speed degrading from thermal throttling over a sustained session; out-of-memory kill on low-RAM devices; slow cold-start model load time; local storage exhaustion from cached model weights/logs; OS backgrounding killing inference mid-run.
   - **(D) Hybrid**: everything listed under **(C) On-device inference** above (a hybrid tool still runs local inference and is subject to all of those failure modes), *plus* the sync-specific additions: sync conflicts when connectivity returns after an extended gap; stale local cache silently served as current data; partial sync leaving the app in an inconsistent state.
   Select the 4-6 failure modes most relevant to the stated architecture and connectivity/device profile; drop modes that clearly don't apply (e.g., skip thermal throttling for a pure cloud-API text chat with no heavy local UI work). For Hybrid specifically, do not drop the on-device modes just because a sync step exists — they're additive, not a replacement.

4. **Rank the selected failure modes by likely user-facing severity** — silent failures (user thinks it worked, it didn't) rank above loud failures (visible error message) above slow-but-eventually-working, because silent failures are what produce abandoned pilots rather than filed bug reports.

5. **For each ranked failure mode, write a concrete test instruction**, including a fallback method that needs no custom harness:
   - Network-condition modes: `tc`/`netem` command sketch (Linux) for packet loss/latency/drops, or "toggle airplane mode for N seconds mid-request" as the no-tooling fallback.
   - Device-resource modes: run on the cheapest available real device or an emulator profile set to the lowest RAM/CPU tier available, and note that true thermal throttling needs a physical device — flag this explicitly as something the plan can describe but can't fully substitute for.
   - Messaging-provider modes: note that some (e.g., provider-side silent loss) can only be tested against the provider's sandbox/test number, not simulated locally — flag this as an external dependency.

6. **Assemble the output** (format below). Explicitly separate "can test today with free/manual tools" items from "needs a real device lab or provider sandbox" items so the team knows what they can start on immediately versus what to plan for.

## Output format
A single Markdown report with these sections, in order:

1. **Architecture & Profile Used** — the classified architecture type and the connectivity/device tier used, stating plainly whether the tier came from user-supplied specifics or was inferred from a named region (and flagging it as qualitative if inferred).
2. **Prioritized Failure Modes** — numbered list, most severe (silent failure) first, each with a one-line description of what breaks and why it matters for this architecture.
3. **Test Instructions** — one subsection per failure mode: the concrete test method, the no-harness fallback if one exists, and whether it's testable today or needs a device lab/provider sandbox.
4. **Pass/Fail Checklist** — a table: `Failure Mode | Test Method | Pass Criteria | Status (unchecked)`. This is the artifact a team actually works through and attaches to a release.
5. **Gaps This Plan Can't Close** — one line naming anything the plan flags but can't actually verify without infrastructure the team doesn't have yet (e.g., real thermal throttling data, a messaging provider's sandbox access).

## Guardrails
- Never invent specific connectivity numbers (latency ms, Mbps, packet-loss %) not supplied by the user or a named source — describe tiers qualitatively unless given real figures.
- Never present this plan as equivalent to having run the actual stress test — it is an unexecuted plan and checklist, not a test result. Say so explicitly if the user seems to be treating it as a pass.
- Never skip asking about architecture or connectivity profile and guess instead — a wrong architecture classification produces a checklist full of irrelevant failure modes.
- Never produce a generic QA/performance checklist (page load time, UI responsiveness) in place of the four field-condition failure categories above — stay scoped to connectivity drops, latency, reconnect/retry behavior, and device resource exhaustion.
- Never claim adoption numbers, case studies, or scaling-rate statistics as fact inside the output — those belong to the underlying research digest, not to a tool-specific test plan.
