# Handoff Line: A Reusable Open-Source Library for Attended SIP Warm Transfer

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Voice & multimodal agents
- **Source**: research/2026-11-12-voice-multimodal-agents-iii.md · P2
- **Maturity verdict**: PARTIAL (search found only generic SIP building blocks — SIP.js's transfer guide, PJSIP's XFER module, Asterisk's `res_pjsip_refer.c`, sipsorcery's signaling-only attended-transfer example, a Go REFER/NOTIFY package, LiveKit's SIP API with an open issue #91 asking about REFER support — plus Dograh's platform-bundled implementation; no dedicated, maintained, platform-agnostic library packaging consultation-leg + REFER-with-Replaces + NOTIFY tracking was found)
- **Format**: PROJECT
- **Data Sources**: CONNECTED — the library speaks SIP directly against the voice agent's own telephony trunk (LiveKit SIP, Twilio Elastic SIP Trunking, Telnyx, or any carrier/PBX exposing a standard SIP interface) to send INVITE/REFER/NOTIFY messages and inject the briefing payload; it never requires a user to paste call data. The underlying SIP primitives (PJSIP, SIP.js, sipsorcery) are mature and widely deployed — the warm-transfer flow built on top of them is what's missing.

## The Gap
Every attended-transfer implementation found in the research is either a generic protocol primitive (SIP.js, PJSIP, Asterisk, sipsorcery — signaling-only, no media/briefing logic) or bundled inside one vendor's product (Dograh). A direct search for "a dedicated open-source library for warm handoff over SIP REFER" came up empty. LiveKit's own GitHub issue #91 is an open, unresolved ask for REFER support — live demand from a maintained platform with no answer yet. Every team building AI-to-human escalation currently re-solves the consultation leg, REFER-with-Replaces signaling, and NOTIFY-based completion tracking from scratch.

## The Project
A stack-agnostic library that implements the full attended-transfer flow as a drop-in component: open a consultation leg to the receiving human agent, inject a structured briefing payload (call summary, caller intent, sentiment, any gathered data) over a SIP side-channel or a companion API, complete the handoff via REFER-with-Replaces once the human accepts, and track completion via NOTIFY so the calling application knows definitively whether the transfer succeeded, failed, or was abandoned. The novel pattern is the centerpiece, not a feature bolted on: this is the full briefing-aware attended flow, not just transfer signaling.

Components: a consultation-leg manager, a briefing-payload injector, a REFER-with-Replaces completion handler, a NOTIFY-based status/event emitter, and a reference adapter layer proving the API holds across at least two SIP trunk providers and one open-source softswitch.

## Tangible Impact
**Population**: callers escalated from an AI voice agent to a human — patients on telehealth triage lines, policyholders on insurance claims lines, customers on bank fraud/dispute lines. Industry sources (Caller.Digital, Start Telecom — both vendor-sourced and unverified by independent audit, but directionally consistent) describe 25-60% of AI-to-human transfers failing or dropping industry-wide for lack of a proper warm-handoff architecture; every one of those failures is a caller who has to repeat their issue, re-authenticate, or hang up and call back.
**Mechanism**: a packaged, briefing-aware warm-transfer flow means the human agent receives the caller's context before picking up, so the caller isn't forced to restate anything, and the completion-tracking layer means the calling application knows the transfer actually succeeded instead of silently losing the call.
**Measure**: call-drop rate on transfer, measured on a reference SIP stack before/after adopting the library against the 25-60% industry baseline; percentage of transfers where the receiving human has to ask the caller to repeat their issue (re-ask rate); time-to-connect for warm vs. a naive cold-transfer baseline.

## Why Now
2026 has seen voice agents cross from pilot to production specifically needing a human-escalation path, and LiveKit's own open issue shows a maintained, widely-adopted platform currently has no first-party answer. This is pure protocol/infrastructure engineering on mature SIP primitives (PJSIP, SIP.js, sipsorcery already handle the signaling layer) — nothing here depends on a future model capability.

## MVP Sketch
Build the library as a Python or Node package wrapping an existing SIP stack (sipsorcery or PJSIP bindings), implementing the four components above. Integrate it into an existing open-source voice-agent demo (Pipecat or a LiveKit agent) and validate against two SIP trunk providers (e.g., Telnyx and Twilio Elastic SIP) plus one open-source softswitch (Asterisk). Single experiment: run 50 simulated transfer scenarios comparing drop rate and re-ask rate against a naive cold-transfer baseline on the same stack.

## Risks & Open Questions
- SIP REFER-with-Replaces support varies by carrier/PBX; some budget carriers may not support it at all, limiting where the library is usable without a fallback cold-transfer path.
- Risks becoming "yet another thin wrapper" if it doesn't meaningfully reduce integration work versus using PJSIP/SIP.js directly — the reference integration must demonstrably save time, not just re-export existing primitives.
- The 25-60% drop-rate figures are vendor-sourced and unverified independently; if the real baseline is materially lower, the quantified impact story needs revisiting with an independent audit.
- A dominant voice-agent platform (LiveKit, given its own open issue) could ship this as a first-party feature before an independent library gains adoption, reducing the project's relevance window.
