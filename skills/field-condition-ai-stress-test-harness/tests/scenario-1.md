# Scenario 1 — WhatsApp-based maternal health Q&A bot, rural Kenya

## Input (as a user would paste it)

> My tool: a WhatsApp bot that answers maternal and newborn health questions for community health workers (CHWs). It's built on the WhatsApp Business API, with a backend that calls an LLM and sends the reply back through the provider. We're piloting it with CHWs in rural Kenya.
>
> Connectivity: I don't have hard numbers, but CHWs report the connection "comes and goes," they're mostly on basic Android phones, and some visit households with no signal at all for stretches during the day.
>
> Device: Android phones, several are older/lower-end models (CHWs mentioned some are 2-3 years old, nothing high-end), nothing more specific known.
>
> Known issues so far: one CHW mentioned the bot "went quiet" for a few minutes during a visit and she wasn't sure if her question went through.

## Expected behavior

- Classifies architecture as **(B) Messaging-channel bot** (WhatsApp Business API + LLM backend), not cloud-API or on-device.
- Does not invent a specific connectivity tier number; either asks the user to pick from the qualitative Tier 1-4 table or explicitly states it's inferring **Tier 3 (2G/EDGE-like, frequent/extended drops)** or **Tier 4 (offline stretches)** from "comes and goes" + "no signal for stretches," and flags that inference as qualitative, not measured.
- Prioritized failure modes include, near the top: silent message loss ("delivered" but never reaches backend) — directly matches the reported "went quiet" incident — and bot-silent-with-no-fallback-message. Out-of-order delivery and webhook retry storms should also appear, lower priority than the silent-loss case.
- Does NOT include on-device inference failure modes (thermal throttling, OOM kill, cold-start model load) since this is a messaging-bot architecture, not on-device inference. (Device profile is noted but device-resource failure modes should not dominate — they're secondary at most, since the LLM runs server-side.)
- Test instructions for the silent-loss failure mode note that it requires testing against the WhatsApp provider's sandbox/test number — flagged explicitly as needing external access, not something a local `tc`/`netem` command can simulate.
- Includes a pass/fail checklist table with at least 4 rows.
- "Gaps This Plan Can't Close" explicitly names that true field connectivity data (vs. CHW anecdote) and provider-sandbox access are missing inputs.
- Report does not claim this plan proves the bot is field-ready, and does not cite the 34%-scaling-rate or any specific percentage as if validated for this specific bot.

## Pass/fail criteria

- PASS if: architecture correctly classified as (B); connectivity profile explicitly flagged as inferred/qualitative rather than presented as a hard number; silent-message-loss ranked at or near top of failure modes and tied back to the reported incident; on-device-only failure modes absent or clearly secondary; checklist table present; external-dependency flag present for provider-sandbox-only tests; no fabricated statistics attached to this specific bot.
- FAIL if: architecture misclassified (e.g., treated as on-device or generic cloud API without acknowledging the messaging-provider layer); a specific Mbps/latency number is invented without being marked as inferred/qualitative; silent message loss is omitted or buried below unrelated device-resource failure modes; no external-dependency flag on provider-only tests.
