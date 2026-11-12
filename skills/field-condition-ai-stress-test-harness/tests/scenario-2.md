# Scenario 2 — On-device crop-disease identification app, offline-first, mid-tier Android

## Input (as a user would paste it)

> My tool: a mobile app for smallholder farmers that identifies crop diseases from a photo, using an on-device vision model (no network call needed for the actual inference — it's bundled and runs locally). There's an optional sync step that uploads results and pulls model updates when connectivity is available.
>
> Connectivity: deploying across several agricultural regions with patchy mobile data; sometimes days pass with no connectivity at all for some users, so we built it offline-first on purpose.
>
> Device: targeting mid-tier Android phones, roughly 3-4GB RAM, nothing high-end; some users are on devices that are a few years old and run hot in direct sun during field use.
>
> Known issues: a field tester mentioned the app felt "slow to open" the first time after being off for a while, and once reported the app closing itself after using it outside for a long session.

## Expected behavior

- Classifies architecture as **(D) Hybrid** (on-device inference + periodic sync), not pure (C) on-device-only, because the optional upload/model-update sync step is explicitly described.
- Connectivity profile: should lean toward **Tier 4 (offline-first, connectivity is the exception)** given "days pass with no connectivity," stated explicitly as the basis, not asserted as a precise figure.
- Prioritized failure modes should include, ranked near the top: OS/app backgrounding or thermal-related kill mid-run (directly matches "closing itself after using it outside for a long session" — thermal throttling / overheating in direct sun), and slow cold-start model load (directly matches "slow to open... after being off for a while"). Sync-conflict and stale-cache-served-as-current should also appear since this is Hybrid, ranked appropriately given no sync-related complaint was reported yet.
- Should flag that true thermal-throttling testing needs a physical device in realistic sun/heat conditions, not just an emulator — this must appear in "Test Instructions" and/or "Gaps This Plan Can't Close," since it's explicitly called out as hard to simulate accurately in the source idea.
- Should NOT include messaging-provider-specific failure modes (webhook retries, provider rate limits) since there is no messaging-channel component here.
- Checklist table present with at least 4 rows, including the two failure modes tied to reported symptoms (slow cold start, thermal/backgrounding kill).
- Does not claim the plan has been executed or that it proves field-readiness.

## Pass/fail criteria

- PASS if: architecture correctly classified as (D) Hybrid; connectivity tier explicitly tied to offline-first/Tier-4 reasoning; thermal/backgrounding kill and cold-start load both appear near the top of prioritized failure modes and are explicitly linked to the two reported symptoms; physical-device limitation for thermal testing is flagged somewhere in the output; no messaging-bot-specific failure modes included; checklist table present.
- FAIL if: architecture classified as pure on-device (C) with the sync step ignored, or as cloud-API (A); thermal/backgrounding and cold-start issues are missing or not connected to the reported symptoms; the plan implies emulator testing alone is sufficient for thermal throttling without flagging the physical-device limitation; messaging-bot failure modes appear despite no messaging component.
