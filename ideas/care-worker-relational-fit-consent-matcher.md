# ConsentMatch: Participant-Directed Relational-Fit Matching for Disability Support Workers

- **Status**: PROPOSED
- **Date**: 2026-11-18
- **Topic**: Applied AI for underserved domains
- **Source**: research/2026-11-18-applied-ai-for-underserved-domains.md · P2
- **Maturity verdict**: PARTIAL — the matching mechanic (skills/availability/location/pay-rate) is commercially saturated-ish (ShiftCare SmartMatch, CareMatch), but no shipped product bundles that matching with participant-directed consent and legal AI-use disclosure; the only team building that combination (ausdisau/MapAble PR #46) is an unreleased draft feature from a single org.
- **Format**: PROJECT
- **Data Sources**: CONNECTED — reads existing worker/participant roster, availability, and skill data from care-management platforms disability providers already run on (e.g. ShiftCare, Lumary, Brevity — mature, widely adopted rostering/CRM tools in the Australian NDIS market) via their existing APIs, instead of requiring a provider to re-enter profiles. MANUAL fallback for providers without a connected platform: a structured intake form for each participant's preferences and each worker's self-described compatibility traits, pasted or uploaded once per profile.

## The Gap
A live GitHub PR (ausdisau/MapAble #46, 2026-11-16) is building, from scratch, inside one feature, "participant-directed Relational Fit v1 with worker opt-in and legal AI disclosures." Commercial tools already match on skills/availability/location/pay (ShiftCare's SmartMatch, CareMatch's "how well you get along" filter), but both are closed-source and neither ships the participant-directed consent-and-disclosure layer that is the actually novel, unmet part — the bundled combination exists nowhere outside this one unreleased draft.

## The Project
A matching engine purpose-built for disability support-worker/participant pairing that treats consent as a first-class, structural step rather than a bolt-on: participants explicitly opt in to AI-assisted matching (vs. default caseworker-only assignment), workers separately opt in to being matched this way, and every match surfaces a plain-language disclosure of what the AI used to make the recommendation (which traits, how weighted) before either party confirms. The matching model itself scores compatibility on self-reported traits (communication style, interests, lived-experience overlap) layered on top of the hard constraints (availability, qualifications, location) existing commercial tools already solve.

## Tangible Impact
**Population**: NDIS participants and the disability support workforce in Australia — 782,013 NDIS participants as of 30 June 2026 (ndis.gov.au) matched against an estimated ~270,000-person support workforce (2025 PMC workforce retention survey), the exact market ausdisau/MapAble serves.
**Mechanism**: Participants currently get assigned a worker by caseworker judgment or basic availability matching, with no visibility into why, and no choice about whether an algorithm was involved. This project gives them an explicit opt-in/opt-out and a plain-language explanation of the match rationale, shifting control of a decision that materially affects daily-life quality (who comes into their home) from opaque backend logic to an informed participant choice.
**Measure**: Participant-reported match satisfaction vs. caseworker-only baseline assignment; opt-in rate and opt-out-after-disclosure rate (a high opt-out rate signals the disclosure, not just the match, needs work); worker retention/turnover on AI-assisted vs. traditionally assigned pairings over 6 months.

## Why Now
A live, dated PR (2026-11-16) just proved a real provider is building exactly this and that the legal-disclosure requirement is now being treated as non-optional in the sector — but as a single team's bespoke, unreleased feature, meaning a reusable, provider-agnostic version built now would launch into a market that has just validated demand without yet having a shared implementation to compete against.

## MVP Sketch
A standalone matching microservice with a REST API: input a participant's hard constraints + soft-trait profile and a pool of opted-in workers, output a ranked match list with a disclosure payload (what was weighted, how). Stack: a simple weighted-scoring model (not deep learning — explainability matters more than marginal accuracy here) behind FastAPI, a Postgres store for profiles/consent state, and a thin integration adapter for one pilot provider's existing roster platform. The single experiment: run it in shadow mode against a provider's live caseload and measure whether its top-3 ranked matches align with what an experienced caseworker would have chosen, before any participant-facing rollout.

## Risks & Open Questions
- Explainability vs. accuracy tradeoff: a more complex model might match better but be harder to disclose honestly — this project should bias toward the simpler, explainable model even at some match-quality cost.
- Consent fatigue: if every match requires a fresh opt-in click-through, participants (and overworked workers) may rubber-stamp without reading; disclosure UX design matters as much as the matching logic.
- Risk that MapAble ships this feature and open-sources it before this project reaches parity — worth monitoring the PR's merge status before committing resources.
- NDIS-specific regulatory requirements (privacy, worker screening checks) need legal review before any pilot touches real participant data.
