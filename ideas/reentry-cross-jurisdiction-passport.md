# Reentry Passport: A Person-Controlled Continuity Record Across Facilities, Parole, and State Lines

- **Status**: PROPOSED
- **Date**: 2026-11-13
- **Topic**: Applied AI for underserved domains
- **Source**: research/2026-11-13-applied-ai-underserved-domains-5th.md · P2
- **Maturity verdict**: OPEN — at least five independently-built, non-interoperating AI reentry tools exist (Recidiviz Opportunities, Next Steps/RREPS, CEO's AI Voice Coach, a Kansas/Michigan exoneree app, Parish Tec), each siloed per org/state with no shared data standard or handoff mechanism. The only cross-jurisdiction data-sharing effort found (IJIS Institute's offender-information pilot) is not AI-driven and not person-controlled.
- **Format**: PROJECT
- **Data Sources**: MANUAL — the person leaving incarceration (or a reentry case manager acting with their consent) uploads/enters their own discharge paperwork, case plan, resume/work history, and program enrollment records once, into a record they control. No mature cross-jurisdiction reentry-data API exists to connect to; building the portable record itself is the point of this project, not a gap to paper over with a fake connector.

## The Gap

Recidiviz Opportunities runs in 8 states with 80,000+ users; Next Steps is North Carolina-specific; CEO's AI Voice Coach piloted with 500+ participants on prison phone lines; a separate exoneree-focused app runs in Kansas/Michigan. Each is a well-funded, independently-built silo. None of the trade-press coverage mentions a shared standard or handoff mechanism, so a person who moves between a facility, parole supervision, and a different state or county has to start their navigation history over at every single transition — the exact moments reentry risk is highest.

## The Project

A lightweight, person-owned record (think a digital folder the individual controls, not an institution) that holds their reentry plan, case history, document checklist status (ID, housing applications, job leads, program enrollments), and notes from any program they've used — exportable as a structured file and importable into participating reentry programs' own intake processes. Rather than asking Recidiviz, RREPS, or CEO to adopt a new shared backend (unlikely, given independent funding), the project starts as a neutral, open-format "resume for reentry" the person carries themselves and hands to whichever program they land in next, with light integrations (CSV/PDF export, a simple API) that participating programs can optionally read from.

## Tangible Impact

**Population**: Of the roughly 1.9 million people incarcerated in the US at any time (Vera Institute data), a large share are released and move across facility, parole, and sometimes state lines during their reentry period — people who, under the status quo, lose their case history and have to re-explain their situation to each new program or caseworker.

**Mechanism**: A portable, person-controlled record eliminates the "start over" tax at every transition — a new parole officer, a new county program, or a move to another state can pick up an already-built plan instead of re-interviewing from scratch, reducing the chance a documented need (housing lead, job interview, medical appointment) falls through a handoff gap.

**Measure**: (1) time from intake at a new program to having an active case plan, for users with vs. without a prior passport record; (2) self-reported rate of "had to re-explain my situation from scratch" among users at program transitions; (3) number of participating programs accepting passport-format imports within the first year.

## Why Now

Every piece of underlying technology (structured document export/import, a simple consented-data-sharing API, LLM-assisted plan summarization for export) is mature and cheap today; what's missing is simply that no one building a reentry tool has prioritized portability over their own program's walls, and the five independent, well-documented 2026 silos make that gap newly visible and citable.

## MVP Sketch

A single-page web app where a person creates an account, fills in or uploads their current reentry plan/case notes, and can export a clean PDF/JSON summary plus a shareable read-only link. No integration with existing platforms required for v1. Single experiment: partner with one reentry nonprofit (not Recidiviz/RREPS-scale) serving people who are about to transition between a facility and parole in two different counties, and measure whether caseworkers at both ends found the exported record useful enough to act on without re-interviewing.

## Risks & Open Questions

- Existing well-funded tools (Recidiviz, RREPS) have no commercial incentive to support export/import into a neutral format; adoption depends entirely on the person, not the institution, which may limit where the record is actually useful.
- Reentry data is highly sensitive (criminal history, health, housing status); a person-controlled record still needs a credible security and consent model before any nonprofit will recommend it to clients.
- "Interoperability" sounds like infrastructure for institutions; keeping the product framed and built around individual control (not another case-management system for agencies) is essential to the Tangible Impact thesis and easy to drift away from.
- It's possible a state-level reentry agency is already quietly building something like this that didn't surface in trade press — worth a direct check with state DOC digital-services offices before committing scope.
