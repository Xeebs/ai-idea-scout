# Signal Normal: A Carrier-Agnostic SIP Event Abstraction Layer for Voice Agents

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Voice & multimodal agents
- **Source**: research/2026-11-12-voice-multimodal-agents-iii.md · P3
- **Maturity verdict**: PARTIAL (only proprietary vendor gateways partially normalize carrier SIP differences — SignalWire's protocol-normalization pitch, a telephony-bridge vendor's ~7-carrier DTMF-variant testing, didlogic's transfer-reliability guide, LiveKit's telephony docs — each a closed cloud connector, not a shared open library; Exotel and Caller.Digital describe the problem as still being discovered "one production incident at a time")
- **Format**: PROJECT
- **Data Sources**: CONNECTED — reads live SIP signaling events directly from the voice agent's telephony providers (Twilio, Telnyx, Exotel, or any SIP trunk/PBX) in real time via their webhook/event or SIP-proxy interfaces; no manual data entry. The carriers' own SIP interfaces are mature; the normalization layer sitting across them is what's missing.

## The Gap
Exotel's own engineering blog states plainly that signaling events — a DTMF press, a transfer, a hold, a mid-sentence hangup — "live in SIP, not in the audio stream," and that teams "discover [carrier] differences one production incident at a time." Caller.Digital reports that in one Indian enterprise deployment, every fourth call drops on transfer specifically because every regional cloud-telephony provider has a slightly different SIP profile. Every existing fix found is a single vendor's proprietary cloud connector (SignalWire, a bridge vendor tested against ~7 carriers) — none is a shared, open abstraction any team can adopt regardless of which carriers they use.

## The Project
A normalization shim that sits between the voice-agent runtime and multiple SIP trunk providers, translating carrier-specific signaling encodings (DTMF via RFC 2833 vs. SIP INFO, hold/resume variants, mid-call hangup detection, transfer-initiation framing) into one consistent event stream (`dtmf_pressed`, `hold_requested`, `transfer_initiated`, `hangup_detected`, `timeout`) that agent logic can consume without per-carrier special-casing. The centerpiece is a differential-testing harness that proves the normalization holds across real carriers, not just a single integration guide.

Components: per-carrier signaling adapters, a normalized event emitter, a differential test harness that replays identical call scripts across carriers and diffs the emitted events, and a public compatibility matrix (which carriers support which signaling behaviors cleanly) maintained like a browser-compat table.

## Tangible Impact
**Population**: end customers of enterprises running voice agents across telephony-fragmented markets — Exotel's own post frames this specifically for Indian enterprise voice-agent deployments, where Caller.Digital reports roughly 1 in 4 transferred calls drop due to carrier SIP-profile differences. Every dropped or misread signaling event in that population is a customer whose call silently fails, who gets transferred into dead air, or whose DTMF input is ignored.
**Mechanism**: a shared, open normalization layer means a voice-agent team stops hand-discovering carrier quirks incident-by-incident in production and instead ships against one consistent event model, catching signaling mismatches in a test harness before they reach a real customer's call.
**Measure**: rate of signaling-event misclassification (missed DTMF, undetected mid-sentence hangup) across N tested carriers, before vs. after adopting the shim; number of carrier-specific special-case branches removable from a reference agent's codebase; call-transfer success rate across carriers measured on the same reference stack.

## Why Now
Voice agents are scaling into telephony-fragmented markets in 2026 faster than any shared tooling has emerged to handle it — Exotel and Caller.Digital's posts describe this as a live, current operational pain point, not a hypothetical one, and the carrier SIP primitives these quirks sit on top of are stable enough today to build a durable abstraction against.

## MVP Sketch
Build a signaling-normalization shim with adapters for three to four initial carriers/trunks (Twilio, Telnyx, Exotel, and a self-hosted Asterisk test carrier for a ground-truth baseline), emitting the normalized event stream above. Build a differential test harness that sends the same scripted test call (a DTMF sequence, a mid-sentence hangup, a hold-then-resume) through each carrier and confirms the shim reports identical normalized events regardless of carrier. Single experiment: measure how many of the scripted signaling events each raw carrier integration mishandles before normalization vs. after.

## Risks & Open Questions
- Carrier SIP quirks are often undocumented and discovered only via production incidents, making an exhaustive test matrix hard to build without paying for test lines across many carriers.
- Some "quirks" originate in the PBX/softswitch layer rather than pure SIP signaling, which could sit outside what this abstraction can actually normalize.
- This risks becoming a permanent-maintenance burden chasing carrier firmware/profile changes over time — needs a sustainable, community-contributed compatibility-table model (like browser-compat tables) to stay accurate rather than rotting.
- Vendor gateways (SignalWire and others) already solve this for their own platform; an open alternative needs enough carrier coverage and real adoption to beat "just use one vendor's gateway and accept lock-in."
