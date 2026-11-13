# Dial-In Navigator: A Full Resource-Navigation Reentry Tool for People Without Smartphones

- **Status**: PROPOSED
- **Date**: 2026-11-13
- **Topic**: Applied AI for underserved domains
- **Source**: research/2026-11-13-applied-ai-underserved-domains-5th.md · P7
- **Maturity verdict**: PARTIAL — nearly every reentry tool found (Recidiviz's tablet app, Next Steps, the Kansas/Michigan exoneree app, Parish Tec) is app- or tablet-based, assuming a baseline of device access most people leaving incarceration don't have (per Michigan Public's "No ID, No Support, No Plan" and Route Fifty's digital-economy-unpreparedness coverage). CEO's AI Voice Coach is the one confirmed exception — piloted with 500+ participants entirely over monitored prison phone lines, no app needed — but it's narrowly scoped to interview coaching, not full resource navigation.
- **Format**: PROJECT
- **Data Sources**: CONNECTED — Twilio Voice/SMS (a mature, widely-used telephony API) to deliver the IVR/SMS interface over ordinary phone lines, including monitored prison phone systems where CEO's own tool already proves feasible. Resource content (shelters, ID-replacement offices, job programs, benefits offices by county) is MANUAL at the start — curated and entered by the project team or a partner nonprofit, since no single live API covers county-level reentry resources comprehensively, with 211.org's regional APIs as a partial CONNECTED upgrade path where coverage exists.

## The Gap

Michigan Public and Route Fifty both frame the access gap itself — no ID, no smartphone, no recent exposure to app-based services — as the primary barrier for people leaving incarceration, not the content of the support they'd otherwise receive. Yet the AI reentry tooling actually being built (Recidiviz, Next Steps, the exoneree app, Parish Tec) is almost entirely app- or tablet-based, assuming exactly the access baseline this population doesn't have. CEO's AI Voice Coach proves phone-line delivery works technically and is already trusted enough to pilot at 500+ participants, but it only does interview coaching — full resource navigation (housing, ID replacement, benefits, job leads) over a phone-only interface doesn't exist yet.

## The Project

A toll-free number a person can call (including from a monitored prison phone line, matching CEO's proven delivery channel) that walks them through resource navigation entirely by voice or SMS — no app, smartphone, or internet access required. The caller describes their immediate need ("I need a shelter tonight in [county]" or "I lost my ID, what do I do") in plain speech; the system looks up curated, county-specific resources and reads back the relevant contact, address, hours, and required documents, with an option to text the same information to any phone (including a borrowed one) for later reference. A lightweight case memory (tied to a PIN, not an account) lets a returning caller pick up where they left off across multiple calls.

## Tangible Impact

**Population**: People leaving incarceration without a smartphone, ID, or recent app-based service experience — the population Michigan Public and Route Fifty both document as being "sent home unprepared for the digital economy," a substantial share of the roughly 600,000+ people released from US prisons annually (Bureau of Justice Statistics), concentrated among those with longer sentences and the least pre-release digital-literacy support.

**Mechanism**: Delivering full resource navigation over an access channel this population already has (any phone, including monitored facility phones) removes the device/app-literacy barrier that makes every existing AI reentry tool effectively inaccessible to them at the exact moment — release day — when they need it most.

**Measure**: (1) call completion rate (reached a usable resource/contact vs. abandoned call); (2) self-reported or partner-confirmed rate of successfully obtaining the needed resource (shelter bed, ID appointment, benefits office contact) within 48 hours of a call; (3) repeat-caller rate as a proxy for trust and perceived usefulness.

## MVP Sketch

Scope to one county or region with an existing reentry-services nonprofit partner willing to supply and keep current a curated resource list. Stack: Twilio Voice + a speech-to-text/intent layer routing to a small curated resource database, with SMS fallback for text-based info delivery. Single experiment: run the toll-free line for 4-6 weeks through a reentry program's existing release-day handoff, and compare resource-contact completion rates against that program's prior unassisted process.

## Risks & Open Questions

- Prison phone systems are monitored and often charge per minute (a real cost CEO's own pilot had to navigate) — the project needs either a toll-free/collect-call-accepting number or a facility partnership, not an assumption of free calling.
- County-level resource data goes stale (shelters fill up, hours change, programs lose funding) faster than an app's content would, since there's no app-store review mechanism forcing updates — needs a committed maintenance process, likely via the nonprofit partner, from day one.
- Speech recognition accuracy for a stressed caller on a noisy prison-phone line is a real engineering risk, not a solved problem by default; CEO's narrower interview-coaching scope may have sidestepped harder open-ended intent recognition this project needs.
- Overlaps conceptually with cross-facility reentry continuity (a separate pattern, P2 in this digest) but solves a distinct problem — access channel, not data portability — and should stay scoped separately rather than merged into one product.
