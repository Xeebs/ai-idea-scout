# Below Spanish: An Offline, Voice-First Pesticide-Safety App for Indigenous-Language Farmworkers

- **Status**: PROPOSED
- **Date**: 2026-11-13
- **Topic**: Applied AI for underserved domains
- **Source**: research/2026-11-13-applied-ai-underserved-domains-6th.md · P5
- **Maturity verdict**: PARTIAL — Follow-up WebSearch found PNASH's relaunched app (branded PestiSafe/PestiSeguro, March 2026 relaunch, 2026 grant expanding its product database 100→2,000) already works offline and is bilingual English/Spanish — a real, actively-maintained implementation. "Pesticide Labels, Now!" is a second English/Spanish app. The connectivity-gap half of the original pattern is solved; what remains unaddressed is coverage below Spanish for indigenous-language speakers combined with offline delivery — no tool found does both together.
- **Format**: PROJECT
- **Data Sources**: MANUAL — content is offline-first by design (the entire point is working when employer-provided internet is unreliable or absent); farmworkers interact with pre-loaded audio/text safety modules, no live data pulled at runtime. The content pipeline itself is fed manually by domain experts (adapting EPA Worker Protection Standard text, PNASH's own validated content) and voice-recorded with native-speaker validators per language variant — not sourced from an external API.

## The Gap
University of Washington's PNASH program's relaunched PestiSafe/PestiSeguro app and "Pesticide Labels, Now!" both deliver offline, bilingual (English/Spanish) pesticide-safety content — real progress on the connectivity problem a 2025 commentary flagged (employer-provided internet often doesn't guarantee reliable access, leaving workers without information during disconnected periods). But pesticide labels remain largely English-only to begin with, "bilingual" stops at Spanish, and a 2018 Washington figure attributes most farmworker pesticide illnesses to English-only label instructions — a gap that persists untouched for the sizable population of workers who speak neither English nor Spanish as a first language.

## The Project
An offline-first, voice-first (for low literacy) pesticide-safety and labor-rights app covering 1-2 priority indigenous-language variants to start — recorded and validated by native speakers, not machine-translated, given the documented unreliability of AI translation for these languages (see the companion idea on indigenous-language MT confidence, `indigenous-language-translation-confidence-gate.md`). Content centers on the same EPA Worker Protection Standard material PNASH already validated, adapted into audio modules a worker can access with zero connectivity. The maintained, native-speaker-validated content library and its offline distribution mechanism are the centerpiece — not a translation engine, which this deliberately avoids given the quality risk.

## Tangible Impact
**Population**: indigenous-language-speaking migrant farmworkers in US agriculture. California state data counts 7,681 Mixteco speakers and 374 Zapotec speakers among students alone (2024-25); the Middlebury Institute cites 20,000+ Salinas Valley immigrants who speak neither English nor Spanish; the National Center for Farmworker Health's broader estimates put several hundred thousand indigenous-language-speaking farmworkers nationally.
**Mechanism**: removes both the connectivity barrier (employer wifi unreliable, per the 2025 commentary) and the Spanish-only language barrier simultaneously, where every existing app — including PNASH's own validated, actively-maintained relaunch — solves at most one of the two.
**Measure**: (1) comprehension-test pass rate on key safety instructions among indigenous-language-speaking users, vs. the near-zero baseline implied by the 2018 WA English-only-label illness-attribution figure; (2) app usage/completion rate measured under real low-connectivity field conditions; (3) number of native-speaker-validated language variants shipped and actively maintained.

## Why Now
PNASH's March 2026 relaunch and its 2026 grant expanding the product database to 2,000 entries prove the offline-delivery technical approach works and is fundable right now — the remaining gap is specifically the language coverage, not the delivery mechanism, which de-risks the hardest technical piece of this project before it starts.

## MVP Sketch
Partner with PNASH or a Salinas Valley community org (e.g. an Indigenous Interpreting+-adjacent organization) to pick one well-documented variant (e.g. the specific Mixteco variant used in Greenfield, CA schools), adapt PNASH's existing validated WPS content into audio modules with native-speaker voice talent, and ship as an offline-capable app for a pilot group of 20-30 workers, measuring comprehension before/after against the existing English/Spanish-only baseline. 3-4 weeks for the content pipeline and app shell, 1-2 people plus community-org partnership and paid native-speaker reviewers.

## Risks & Open Questions
- Dialect fragmentation is severe (INALI counts 81 Mixtec variants, 50+ Zapotec languages, often differing town-to-town per the companion P6 research) — a single "Mixteco" module may not serve workers from a different town's variant, so scope and validate narrowly rather than claiming broad coverage.
- Native-speaker voice recording and validation is genuinely slow and costly compared to text/MT-based approaches; this is a deliberate tradeoff for quality over speed, and the project needs a realistic per-variant content budget from day one.
- Strongest reason this might already be solved: PNASH or a similar org could already have an indigenous-language pilot in progress not yet publicly announced — worth direct outreach before assuming greenfield.
- Pesticide-safety content changes as regulations update; the native-speaker-validated audio library needs a real maintenance plan, not a one-time recording.
