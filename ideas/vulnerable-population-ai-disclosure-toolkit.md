# Plain Disclosure: A Reusable AI-Use Consent & Disclosure UX Toolkit for Vulnerable-Population Products

- **Status**: PROPOSED
- **Date**: 2026-11-18
- **Topic**: Applied AI for underserved domains
- **Source**: research/2026-11-18-applied-ai-for-underserved-domains.md · P7
- **Maturity verdict**: PARTIAL — generic building blocks exist (SAP Fiori's AI-acknowledgment design pattern, Washington's MHMDA consent-flow legal requirement, a personal "AI Attribution Toolkit" generating generic disclosure statements) but none is targeted at disclosing AI involvement in decisions about vulnerable populations specifically (disability, asylum, elder care); the only team building this for a real vulnerable population (ausdisau/MapAble PR #46) is doing so as one bespoke, unreleased feature inside a matching tool, not a reusable library.
- **Format**: BOTH
- **Data Sources**: MANUAL — a host application passes in the decision context it needs disclosure copy for (what the AI did, what population/jurisdiction, what data it used) as configuration, not a live external data read; this is a self-contained embeddable component library/SDK, so there is no external connector to integrate — the "data" it operates on is the host app's own description of its AI usage, supplied once at integration time.

## The Gap
The MapAble PR that surfaced pattern P2 ships, as a named bespoke feature, "participant-directed Relational Fit v1 with worker opt-in and legal AI disclosures" — one team deriving its own legal disclosure language and consent UX from scratch, with no sign of a shared library, spec, or naming convention any other vulnerable-population-facing product could reuse instead. The generic disclosure-pattern space (SAP Fiori's acknowledgment checkbox, MHMDA's legal requirement) is partly covered, but none of it is built for the specific stakes of telling a disability participant, an asylum seeker, or an elder-care client that an AI contributed to a decision about them.

## The Project
A drop-in, embeddable UI component library (React/web-component, plus a framework-agnostic spec) that any product serving a vulnerable population can integrate to disclose AI involvement in a decision — pre-written, legally-reviewed template language for common decision types (matching, eligibility screening, risk flagging), an opt-in/consent capture flow with a clear withdrawal path, and a plain-language "what the AI used" explainer panel — configured per-product with the specific decision type, population, and jurisdiction rather than every team re-deriving the legal language and UX from a blank page, which is exactly what MapAble is doing right now.

## Tangible Impact
**Population**: The three vulnerable-population verticals the evidence names directly — the 782,013 NDIS disability-support participants in Australia (ndis.gov.au, 30 June 2026) whose matching MapAble is building disclosure for, and the roughly 2.3 million people with asylum applications pending in U.S. immigration/USCIS systems (TRAC, August 2026) whose cases increasingly involve AI-assisted translation or triage decisions.
**Mechanism**: Today, whether a vulnerable person is even told an AI was involved in a decision about them depends entirely on whether the specific team building that one product happened to prioritize it — this toolkit makes disclosure the default, low-effort path rather than the bespoke, easy-to-skip one, directly increasing how often affected people actually know and can act on AI involvement in decisions that affect them.
**Measure**: Integration adoption count across products/verticals; time-to-integrate for a new product (target: hours, not the multi-week legal-review cycle MapAble is presumably going through alone); end-user comprehension of the disclosure (can a tested user correctly state, after seeing it, that an AI was involved and what they can do about it) vs. a product's own prior ad hoc disclosure, where one existed.

## Why Now
A live, dated PR (2026-11-16) just proved real legal/product teams are being required to build exactly this, with no existing library to reach for — launching a reusable version now means the next MapAble-equivalent team in disability, asylum, or elder-care tech has something to adopt instead of re-deriving the same legal language from zero, which is the state of the art today.

## Skill Angle
The skill half takes a product team's description of their AI-mediated decision (what it does, who it affects, what jurisdiction) and drafts the specific disclosure copy, consent-flow sequence, and withdrawal mechanism for that case — distinct from the project half (the installable component library/SDK itself, which is the runtime infrastructure a team wires into their actual UI) in that the skill is a one-shot drafting/review aid a team uses before or alongside integrating the library.

## MVP Sketch
A small React component package (`<AIDisclosurePanel>`, `<AIConsentFlow>`) with 2-3 pre-written template sets (matching decisions, eligibility/screening decisions, risk-flagging decisions) reviewed by one disability-rights-focused legal advisor, plus a config schema for population/jurisdiction/decision-type. The single experiment: integrate it into one real or simulated vulnerable-population product flow (ideally in dialogue with the MapAble team or a similar org) and measure integration time and end-user comprehension against that product's prior ad hoc approach.

## Risks & Open Questions
- Legal disclosure language genuinely varies by jurisdiction (NDIS/Australia vs. US asylum vs. US elder-care regulation like MHMDA) — a one-size-template risks being wrong somewhere, not just generic; this needs real per-jurisdiction legal review, not just UX design.
- A library that makes disclosure "easy" could paradoxically encourage checkbox-style compliance theater instead of genuine informed consent — the component design needs to resist being gamed into a dark-pattern "consent" click-through.
- Risk that MapAble (or a similarly positioned org) ships and generalizes this feature independently before this toolkit reaches adoption — worth direct outreach to gauge interest in a shared library versus their own bespoke build.
- Overlap with P2's matching project is real (same evidence source) but the project boundary is clean: P2 is the matching runtime, this is the disclosure-UX component any vulnerable-population product — matching or otherwise — can reuse.
