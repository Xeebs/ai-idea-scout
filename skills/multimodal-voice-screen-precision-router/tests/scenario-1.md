# Scenario 1 — Router/ISP remote tech support agent, architecture only, no transcript

## Input

**Architecture description** (as the user would paste it): "We're building a voice support agent for a home internet ISP. The customer shares their screen showing the router admin panel (a web page at 192.168.1.1) while talking to our agent by voice. Right now everything — voice dialogue and screen understanding — runs through a single multimodal model (GPT-4o-class) that gets a downsampled frame every 2 seconds alongside the live voice transcript. We don't have any separate vision model yet. Frame resolution gets scaled down to roughly 960x540 before it reaches the model to keep latency low.

Tasks the agent is asked to do:
1. Walk the customer through finding the Wi-Fi SSID and password fields and reading them back.
2. Tell the customer which status lights/icons mean the router is online vs. in an error state.
3. Guide the customer through a settings page with ~15 small toggles (QoS, port forwarding, parental controls, etc.) to find and flip one specific toggle.
4. Read the signal strength / connection speed numbers shown on a diagnostics graph and tell the customer if they look normal."

**No transcript provided.**

## Expected output characteristics

- **Architecture Reviewed**: must correctly restate that there is one model handling both voice and vision, no existing specialist, frames downsampled to ~960x540 every 2 seconds — and should flag that this is the kind of resolution/interval combination that makes small-detail misses plausible.
- **Risk Table**: must classify all four named tasks against the taxonomy:
  - Reading SSID/password fields → small/dense body text → likely-miss, HIGH priority (password fields especially — getting a character wrong fully breaks the task).
  - Status lights/icons → status icons/toggles → likely-miss, should be flagged (small icons at 960x540 scaled-down frames).
  - The 15-toggle settings page → dense forms/settings grids → likely-miss, HIGH priority (explicitly the "tiny icons/dense menus" case from the idea's own gap).
  - Diagnostics graph numbers → numeric readouts/graphs → likely-miss, flagged.
  A response that calls all four tasks fine for the single model as-is, or that skips any of the four without justification, fails this scenario.
- **No invented evidence**: since no transcript was given, the response must explicitly state the risk table is architecture-level reasoning, not based on observed failures. A response that cites specific "incidents" or invented engagement/complaint numbers fails.
- **Routing Policy**: must recommend OCR-class specialists for the text/password-field and settings-grid categories, and a UI-element/icon detector class for status lights and toggles — named as categories, not a single mandated vendor.
- **Not Recommended For Routing**: should name at least one thing the primary model stays fine for (e.g., general scene-level orientation — "is this the router's admin panel at all" — or high-level voice dialogue itself).
- **Missing-fact handling**: should not demand more info before answering, since the task list given is concrete enough to classify (contrast with Scenario 2's thin-input branch, not tested here).

## Pass/fail

PASS if all four named tasks are each correctly placed in a taxonomy category with a non-generic risk reasoning, the output states no transcript evidence was used, and at least one "not recommended" category is named. FAIL if any task is missed, if invented failure evidence appears, or if a single vendor is mandated instead of a specialist category.
