# Forget This: A Caller-Facing Granular Memory Consent and Deletion Layer for Voice Agents

- **Status**: PROPOSED
- **Date**: 2026-11-20
- **Topic**: Voice & multimodal agents
- **Source**: research/2026-11-20-voice-multimodal-agents.md · P7
- **Maturity verdict**: OPEN — genuine multi-channel search found no shipped voice-agent product with caller-facing granular memory consent/deletion. Telnyx's own Agent Memory docs explicitly state per-memory deletion is "not yet available" (profile-level or whole-session only); a USPTO patent describes undo-by-voice memory deletion but is filed, not shipped; text-chat products (ChatGPT, Claude, Copilot Studio) offer per-item deletion but via a settings menu, not something a caller can invoke mid-call — a different modality that doesn't address the voice-specific gap.
- **Format**: BOTH
- **Data Sources**: CONNECTED — layers on top of the voice platform's existing cross-call memory store via its own read/write/delete API (Twilio Conversation Memory, Mem0, Synthflow, and ElevenLabs are all named in the digest as already shipping always-on cross-call memory with mature APIs); no caller or builder needs to paste memory contents manually. (The companion skill's input is MANUAL — see Skill Angle.)

## The Gap

Multiple vendors (Twilio, Mem0, Synthflow, ElevenLabs) now ship persistent cross-call memory keyed to a phone number or profile, but every one captures and reuses history as an all-or-nothing default. A Twilio-cited research figure says 66% of consumers would feel uneasy about an AI agent having all previous context from past interactions — a stat Twilio publishes right alongside its own "Conversation Memory" feature description, with no mention of per-item control. Telnyx's own documentation is the most direct confirmation: per-memory deletion is explicitly "not yet available." A 2025 arXiv paper on episodic agent memory argues users *should* get this control. The need is acknowledged in vendor marketing copy and academic argument; nothing shipped lets a caller actually exercise it.

## The Project

A consent-and-deletion layer that sits between a voice agent and its memory backend: (1) a voice-recognizable intent class ("forget what I told you about X," "don't remember this call") that the agent can detect mid-call and act on immediately, not just log for later; (2) item-level tagging in the memory store so a deletion request removes the specific fact, not the whole profile — closing exactly the gap Telnyx's docs admit is missing; (3) an optional lightweight memory-review surface (SMS link or app) where a caller can see what's stored about them and delete items outside a call. Built as an adapter layer over existing backends (Mem0, Twilio Conversation Memory, Synthflow, ElevenLabs) rather than a new memory store, so adopters keep their existing vendor.

## Tangible Impact

**Population**: The 66% of consumers (per the Twilio-cited research in this digest) who report discomfort with all-or-nothing AI memory of past interactions — a population that scales directly with every business deploying cross-call voice-agent memory across the 2026 voice-AI-agent market estimated at $3.5–5.1B (Grand View Research, Meticulous Research). Concretely: any repeat caller to a bank, healthcare line, or customer-service IVR running one of the four named memory vendors.
**Mechanism**: Today a caller uneasy about persistent memory has no action available except avoiding the service entirely or accepting the discomfort; this layer gives them an in-call, voice-native way to exercise control (comparable to what ChatGPT/Claude already give text users) without needing a web login or a support-ticket request — closing the modality gap the digest specifically flags.
**Measure**: voice-intent detection accuracy for "forget"-class requests (precision/recall against a labeled test set of real and adversarial phrasings); percentage of flagged deletion requests correctly propagated to the backend within one call turn; caller-reported comfort/trust delta in an A/B pilot with vs. without the visible consent layer.

## Why Now

Cross-call memory went from a minority feature to Twilio/Mem0/Synthflow/ElevenLabs default-on within 2026, per this digest's own evidence — the privacy gap is widening in real deployments right now, not a hypothetical future risk, and Telnyx's documented "not yet available" admission shows even a well-resourced vendor hasn't closed it yet.

## Skill Angle

A "consent UX drafting" skill: given a plain-text description of a team's memory vendor/schema (e.g. "we use Mem0 and store call summaries keyed to phone number") and their regulatory context, it drafts the specific in-call intent-detection phrasing to recognize, the exact deletion-propagation logic needed against that vendor's API, and a plain-language disclosure script explaining what's remembered — so a team gets a tailored spec before building the adapter layer.

## MVP Sketch

Scope: one memory backend (Mem0, the most developer-accessible API of the four named) and one intent class ("forget this" at the whole-call level, not yet sub-fact granularity). Stack: a small Python middleware intercepting the voice agent's memory-write calls, an intent classifier (few-shot LLM or a small fine-tuned model) listening for forget-phrasing mid-call, and a direct call to Mem0's delete API. Validating experiment: run a scripted test-call set including genuine forget-requests and adversarial near-misses ("I forget what I was saying") and measure whether the classifier correctly triggers deletion only on genuine requests.

## Risks & Open Questions

- Mid-call voice intent detection for "forget" requests risks false positives (deleting data the caller didn't mean to) or false negatives (missing a genuine request) — needs a confirmation step before executing a destructive action, not silent auto-delete.
- Item-level deletion assumes the backend stores memory in a form granular enough to target a single fact; some vendors may only store coarse summaries, limiting how fine the control can actually be without upstream changes to how memory is written in the first place.
- This is privacy-adjacent infrastructure, not full compliance tooling — it should be framed and marketed carefully as "giving callers control," not as a GDPR/CCPA compliance guarantee, since legal retention requirements may override a caller's deletion request in regulated industries.
- If a major vendor (Telnyx, Twilio) ships native per-memory deletion before this reaches production, the project's value shifts from "the missing feature" to "the cross-vendor consistent layer" — still useful, but the framing and urgency would need revisiting.
