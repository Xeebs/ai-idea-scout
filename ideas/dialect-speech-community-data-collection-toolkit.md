# Dialect Commons: A Reusable Toolkit for Community-Sourced Dialect and Colloquial-Speech Data Collection

- **Status**: EXPLORING
- **Date**: 2026-11-17
- **Topic**: Applied AI for underserved domains
- **Source**: research/2026-11-17-applied-ai-for-underserved-domains.md · P2
- **Maturity verdict**: PARTIAL — Masakhane's Hub for African Languages (~50 languages) and Lesan AI's custom Tigrinya tooling both prove the technique but are one-off, per-flagship-language efforts; Mozilla Common Voice is mature and reusable but built for read-aloud sentence ASR, not the colloquial/dialect speech that never appears in text, which is exactly the gap Lesan built bespoke tooling to fill. SANTLR (2019, stale) and an Interspeech 2025 Akan cookbook (single-language, narrow) don't close it either.
- **Format**: BOTH
- **Data Sources**: CONNECTED — WhatsApp Business API and Telegram Bot API (both mature, already the default channel for reaching these communities, per this same digest's CHW-chatbot and care-navigation patterns) for voice-note submission and elicitation prompts, so contributors never need to install a dedicated app; a web upload fallback is MANUAL (contributor records/uploads audio directly) for organizers without a WhatsApp/Telegram deployment.

## The Gap
Masakhane (≈50 African languages) and Lesan AI (Tigrinya) each built their own custom pipeline to capture "things you cannot find online, including colloquial speech and dialects" — the Gates Foundation names over 6,000 of 7,000+ living languages as "digitally disadvantaged," meaning thousands of smaller communities face the identical problem these two flagship efforts solved, with no shared tool to copy. Mozilla Common Voice, the obvious reusable candidate, is scoped to scripted read-aloud sentences, not the spontaneous/dialectal speech this gap specifically needs. No GitHub repo, product, or paper was found generalizing Masakhane's or Lesan's approach into something a third community could pick up and run themselves.

## The Project
A self-hostable data-collection platform purpose-built for spontaneous, colloquial, and dialect speech — not scripted ASR sentences. Contributors respond to open-ended elicitation prompts (describe your day, explain a local recipe, answer a community-submitted question) via WhatsApp or Telegram voice notes, the channel they already use; the platform transcribes a draft via general-purpose ASR, then routes it to community moderators (native speakers) for correction, dialect/region tagging, and consent confirmation before anything enters the dataset. A lightweight admin console lets a language-community organizer launch a new collection campaign — prompts, consent language, moderator roles — in hours instead of building Masakhane's or Lesan's bespoke infrastructure from scratch.

## Tangible Impact
**Population**: Grassroots language-preservation groups, diaspora community organizations, and small NLP researcher collectives working on the thousands of dialects and under-resourced languages outside the ~50 Masakhane covers and the single Tigrinya effort Lesan built for — the Gates Foundation's own estimate puts this at over 6,000 languages with no comparable data-collection infrastructure today.
**Mechanism**: Today, a community wanting to bootstrap voice AI for its own dialect must either repeat Masakhane's multi-year, grant-funded organizing effort or Lesan's custom engineering build from nothing. A ready-to-deploy, WhatsApp-native collection toolkit removes that build cost, so a community group with no engineering capacity can launch a real moderated collection campaign directly.
**Measure**: (1) time from "we want to start collecting" to first 100 validated audio clips for a new community (toolkit-enabled vs. Masakhane/Lesan's reported multi-month organizing timelines); (2) hours of native-speaker-validated spontaneous/dialect speech collected per community per month; (3) number of distinct language/dialect communities onboarded within the first year, as a direct test of whether the "thousands of communities with no toolkit" gap is real demand or just discussion.

## Why Now
Masakhane and Lesan both demonstrated the community-sourcing approach works at flagship scale within the last two years, and WhatsApp/Telegram voice-note submission removes the dedicated-app adoption barrier that would otherwise be the biggest blocker for low-smartphone-literacy communities — the same channel this digest's own CHW-chatbot and care-navigation patterns independently confirm is already how these populations interact with AI tools.

## Skill Angle
A companion skill drafts the collection-campaign artifacts a community organizer needs before launch — a localized consent/IP disclosure appropriate to the community's legal context, a set of open-ended elicitation prompts tuned to surface colloquial/dialect speech rather than scripted reading, and a moderator-review rubric — given just the language/dialect name, region, and intended use (ASR training, documentation, etc.). This is strictly a drafting/design aid: it doesn't run the collection platform, it prepares what the platform needs before a campaign goes live.

## MVP Sketch
Partner with one willing under-resourced-dialect community (ideally one adjacent to but distinct from an existing Masakhane language, so comparison is possible) to pilot a single WhatsApp-based collection campaign: a Twilio/WhatsApp Business API webhook receiving voice notes, a basic ASR draft-transcript step, and a simple web moderator queue for native-speaker correction and tagging. Stack: WhatsApp Business API, a general ASR model for draft transcripts, Postgres for the moderation queue and metadata, S3-compatible storage for audio. Single validating experiment: can the pilot community reach 100 validated clips within 4 weeks using only the toolkit and its own volunteer moderators, with no external engineering support after setup.

## Risks & Open Questions
- Consent and IP ownership for recorded speech is legally and culturally sensitive per community; a one-size-fits-all consent flow will not work everywhere and needs local legal input before any real launch, not just a generic ToS.
- Moderator recruitment (native speakers willing to review and tag submissions) may be the actual bottleneck, not the collection technology itself — worth validating directly with the pilot partner before building more collection features.
- Masakhane's own tooling or a similar effort may already be generalizing internally in ways not visible in public search results; a direct outreach check before building a parallel platform is warranted.
- Draft-ASR quality for genuinely under-resourced languages will be poor at launch (there's no model to transcribe from), so the moderator-correction step — not the ASR step — is the actual value; the project needs to be honest that it's a moderated collection tool, not an automated one.
