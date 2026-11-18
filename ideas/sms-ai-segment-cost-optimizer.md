# SegmentWise: A Per-Message-Cost-Aware Response Compressor for SMS-Based AI Access

- **Status**: EXPLORING (promoted cycle 151 — evidence density: teks/tech.eu and ChatMtaani/Citizen Digital are 2 independently-reported SMS-AI deployments, both left unsolved on the per-message cost problem per separate CGD/NextBillion analysis)
- **Date**: 2026-11-18
- **Topic**: Applied AI for underserved domains
- **Source**: research/2026-11-18-applied-ai-for-underserved-domains.md · P3
- **Maturity verdict**: PARTIAL — SMS Works' "AI SMS Message Optimiser" already demonstrates the core mechanic (shrinking a 162-char/2-credit message to 142-char/1-credit) but as a generic SMS-marketing feature from one vendor, not purpose-built for AI-chatbot response protocols or targeted at the ultra-low-income/feature-phone population CGD and NextBillion describe; no second implementation or any product treating this as a first-class design constraint for underserved-population AI access was found.
- **Format**: BOTH
- **Data Sources**: CONNECTED — sits as middleware between an LLM's generated response and an SMS gateway API (e.g. Africa's Talking, Twilio — both mature, already the transport layer in the teks/ChatMtaani deployments cited below), rewriting the outbound text before it is billed and sent, rather than requiring the underlying chatbot to be rebuilt.

## The Gap
teks, ChatMtaani, and textgpt have all shipped AI chatbot access over SMS for the "3.45B people lacking mobile internet access globally" (tech.eu), solving channel availability. But the Center for Global Development and NextBillion both frame the real blocker as SMS pricing itself — "high markups on text messages" that "will prevent the world's poorest from making use of the technology" even with a working channel. None of the three tools found describes compressing per-interaction segment count as a design constraint; they are thin wrappers around an existing LLM API that pass its full, unoptimized response straight to the SMS gateway.

## The Project
A response-compression middleware purpose-built for AI-chatbot-to-SMS pipelines: it rewrites a model's generated answer to minimize billed SMS segments (160-char GSM-7 boundaries, concatenated-segment thresholds) while explicitly preserving the semantic content a low-literacy, low-bandwidth user needs — not just generic shortening, but segment-boundary-aware rewriting (e.g. trimming 2 characters to avoid crossing into a second billed segment is worth far more than trimming 20 characters that don't cross a boundary). It sits between any existing SMS-AI chatbot's LLM call and its SMS gateway send, requiring no change to the chatbot's own logic.

## Tangible Impact
**Population**: The ~3.45 billion people globally lacking mobile internet access who are the explicit target market of teks, ChatMtaani, and textgpt's SMS-AI products (tech.eu, 2025).
**Mechanism**: Every SMS segment a user is billed for either comes out of their own airtime budget or constrains how often an aid/health program can afford to message them; a response that silently spans 2–3 segments instead of 1 directly taxes the poorest users the tool claims to serve. Compressing at the segment boundary, not just the character count, converts a chatbot interaction from a 2-3-segment cost into a 1-segment cost whenever the content allows it.
**Measure**: Average billed segments per AI response before/after (target: a majority of responses crossing 1→2 segments are pulled back under the boundary); total monthly SMS cost per active user in a pilot deployment; user-reported comprehension/satisfaction on compressed vs. uncompressed responses (to confirm compression isn't trading cost for clarity).

## Why Now
Three independent SMS-AI products (teks, ChatMtaani, textgpt) have launched in the last cycle specifically targeting this 3.45B-person gap, and CGD/NextBillion's framing of SMS pricing as the real remaining blocker is itself recent (2025-2026) — the market now exists to plug this middleware into, where a year ago there was no SMS-AI product to sit in front of.

## Skill Angle
A standalone skill audits a set of an existing SMS-AI deployment's past sent messages (pasted as a log) and reports what fraction crossed a segment boundary unnecessarily, with concrete before/after rewrite examples — useful for a team deciding whether building or adopting the full middleware is worth it before committing engineering time.

## MVP Sketch
A single Python function/service: input raw LLM response text, output segment-optimized text, using GSM-7/UCS-2 encoding-aware segment-boundary math (not just character counting) plus a lightweight rewrite pass (either rule-based trimming or a cheap LLM call constrained to "shorten to fit N characters, preserve all factual content"). Stack: a thin FastAPI wrapper deployed as a webhook between one pilot chatbot's LLM call and its Africa's Talking/Twilio send step. The single experiment: measure segment-count reduction and a native-speaker panel's comprehension rating on a batch of real historical responses from an existing SMS-AI deployment.

## Risks & Open Questions
- Aggressive compression risks dropping safety-relevant nuance (e.g. a health chatbot trimming a dosage caveat to save one segment) — needs a content-criticality flag that overrides compression.
- GSM-7 vs. Unicode encoding differences across languages (some local-language scripts force UCS-2's much smaller 70-char segments) may make this harder in exactly the languages underserved populations most need it in.
- Risk this is already solved inside teks/ChatMtaani's proprietary stack and simply undocumented — worth a direct outreach check before building from scratch.
- SMS carrier markup structures vary by country/carrier; the segment-cost savings this delivers may be large in some markets and marginal in others.
