# Open Oral: A Portable Voice-First Advisory Framework for Low-Literacy, Low-Resource-Language Users

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Applied AI for underserved domains
- **Source**: research/2026-11-12-applied-ai-for-underserved-domains.md · P5
- **Maturity verdict**: PARTIAL — Sarvam AI already runs one proprietary LiveKit-based voice-agent pattern across government-services and agriculture verticals, and an arXiv paper (2603.05743) proposes a general oral-first multi-agent architecture demonstrated only on Guaraní, but no reusable, open framework spanning health/legal/civic domains beyond Sarvam's proprietary API pattern was found — every other example (Darli AI, Project Gecko, ToumAI, Wiseyak) is a bespoke, single-domain, org-specific build.
- **Format**: PROJECT

## The Gap
Five-plus independent organizations (Farmerline's Darli AI across 27 languages, Microsoft's Project Gecko with Digital Green, GSMA's ToumAI and Wiseyak cohort projects) have each built a voice-first, local-dialect advisory agent for low-literacy users — but every one is scoped to a single domain, almost always agriculture, and rebuilt from scratch per organization. A WEF piece notes mainstream chatbots cover only ~100 of the world's 7,000+ languages. The interaction pattern (voice in, voice out, local dialect, low-literacy-appropriate phrasing, works on a basic smartphone) is proven and repeated — but it has never been extracted into a reusable, open framework that a health, legal-aid, or civic-services org could pick up the way agriculture orgs keep independently reinventing it.

## The Project
An open, portable voice-advisory framework that separates the domain-agnostic interaction layer (turn-taking, local-dialect ASR/TTS pipeline selection, low-literacy-appropriate response simplification, fallback-to-human escalation) from the domain-specific knowledge layer (the actual agriculture, health, or civic-services content a given org plugs in). An org building a voice advisory tool for, say, maternal-health guidance or civic-benefits information in a given dialect would configure the framework with their domain content and get the proven interaction pattern — ASR/TTS routing for their target language, conversational flow tuned for low-literacy phrasing, human-escalation hooks — without re-engineering what Darli AI, Project Gecko, and ToumAI each built independently.

## Tangible Impact
**Population**: Low-literacy, non-dominant-language speakers outside agriculture who currently have no voice-first AI advisory option in domains like maternal health, civic benefits, or basic legal information — the WEF's ~7,000-language, ~100-language-coverage gap implies hundreds of millions of speakers of the thousands of uncovered languages, and the specific near-term beneficiaries are the health/civic/legal-aid orgs serving these populations who today can only point to agriculture examples as a proof of concept, not a tool they can use.
**Mechanism**: Today, a health or civic-services org wanting to replicate what Darli AI does for farmers has to independently solve ASR/TTS pipeline selection, dialect handling, and low-literacy conversational design from zero, which is exactly why these tools remain agriculture-only. A reusable framework lowers that build cost enough that domains beyond agriculture become feasible for small orgs, not just Farmerline-scale operations.
**Measure**: (1) number of distinct non-agriculture domains/orgs successfully deployed on the framework within a year; (2) task-completion rate (e.g., correctly understood health-guidance query, correctly completed benefits-info request) by low-literacy users compared against existing single-domain bespoke tools' published rates; (3) time-to-deploy for a new org/domain/language combination vs. the multi-month bespoke builds described in the digest.

## Why Now
Open ASR/TTS models with usable multilingual coverage (Whisper-family and newer open alternatives) and cheap LLM-based conversational simplification have both improved enough in the last cycle that the hard parts of a voice pipeline no longer require a proprietary stack like Sarvam's — the gap is now assembly and generalization, not raw capability, which is exactly the kind of gap a focused open-source project can close.

## MVP Sketch
Scope to one additional domain beyond agriculture (maternal/child health guidance is a reasonable choice, given overlap with P1/P3's health focus) and 1-2 pilot languages with decent existing ASR support (to de-risk the hardest sub-problem first). Stack: an open multilingual ASR/TTS pipeline (Whisper + an open TTS model), an LLM for response simplification tuned to low-literacy phrasing norms, a basic phone-call or WhatsApp-voice-note interface, and a human-escalation hook. The validating experiment: deploy the same framework core for two different domains (agriculture as a sanity-check replication of existing work, plus the new health domain) and measure whether the domain-swap genuinely only requires swapping the knowledge layer, not re-engineering the interaction layer.

## Risks & Open Questions
- ASR/TTS quality for genuinely low-resource dialects (not just "low-resource" languages with some existing Whisper support) may still be too poor for a usable MVP — language/dialect selection for the pilot matters enormously.
- Sarvam AI's proprietary pattern may already be licensable or open enough (worth checking docs.sarvam.ai terms directly) that building a parallel open framework is only valuable if Sarvam's isn't accessible to smaller orgs.
- Health-domain voice advisory carries higher stakes than agriculture advice (wrong guidance has worse consequences than wrong crop advice), which may require the same kind of deterministic safety-gating discussed in the P1 CHW-triage idea — these two ideas could eventually share a safety-layer design even though they're separate builds.
- Risk that "voice-first low-literacy interaction pattern" is genuinely domain-coupled in ways not obvious until building two real domains — the MVP's two-domain test is specifically designed to surface this early.
