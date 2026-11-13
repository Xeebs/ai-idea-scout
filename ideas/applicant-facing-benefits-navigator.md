# SNAP/Medicaid Co-Pilot: An Applicant-Controlled Benefits Navigator

- **Status**: PROPOSED
- **Date**: 2026-11-13
- **Topic**: Applied AI for underserved domains
- **Source**: research/2026-11-13-applied-ai-underserved-domains-5th.md · P1
- **Maturity verdict**: PARTIAL — every notable AI benefits tool found (Nava Labs' Form-Filling Assistant and Caseworker Empowerment Toolkit, Code for America/Anthropic's SNAP Policy Navigator, Pyx Health's compliance-outreach bot) is caseworker- or agency-facing; the one applicant-facing bot (SNAP Screener) only answers pre-application eligibility questions, not form completion or notice interpretation. No shipped, applicant-controlled full navigator exists.
- **Format**: BOTH
- **Data Sources**: MANUAL — the applicant uploads/pastes the actual confusing notice or denial letter they received and their own household details (income, household size, state) each time. A CONNECTED version would need a live per-state SNAP/Medicaid applicant-data API, which does not exist publicly in any state today (CDT and Propel's own reporting confirm this is not deployed at scale) — this is a genuine MANUAL-only gap, not a default choice.

## The Gap

Nava's caseworker-side tool reportedly cut application-processing time 73% in a California pilot — a large win that flows entirely to agency staff. The applicant on the other end of that same process still gets a dense notice, a confusing form, and no AI help interpreting either. Propel documented one-off experiments where general-purpose agents (ChatGPT Agent, Claude) could start a SNAP application on a user's behalf, but no one has shipped a dedicated, maintained applicant-facing product that explains notices and completes forms.

## The Project

An applicant uploads a notice, denial letter, or blank application and answers a short set of plain-language questions about their situation. The tool explains what the notice actually means and what's being asked of them, pre-fills the application from their answers, flags documentation likely to be requested (pay stubs, ID, lease), and drafts any required response or appeal letter in the applicant's own words. It tracks deadlines across multiple pending actions (recertification, verification requests, appeals) so nothing lapses from a missed 10-day window. State-specific rule packs (SNAP/Medicaid vary by state) drive what gets flagged.

## Tangible Impact

**Population**: The ~42 million people receiving SNAP and ~79 million Medicaid enrollees nationally (USDA/CMS program data) who must personally interpret notices and complete applications, most without an advocate or caseworker relationship — disproportionately low-income households, non-native English speakers, and people with limited reading time due to multiple jobs or caregiving.

**Mechanism**: Plain-language notice translation and guided form completion reduce the two most common failure points applicants hit alone — not understanding what a notice requires, and missing a procedural deadline because the requirement wasn't clear — both of which can trigger a procedural termination unrelated to actual eligibility.

**Measure**: (1) completion rate of started applications/recertifications among pilot users vs. a baseline cohort; (2) rate of procedural (non-eligibility) denials or terminations among users vs. agency-reported baseline rates; (3) median time from receiving a notice to submitting a compliant response.

## Why Now

Nava and Code for America's 2026 caseworker-side pilots prove the underlying LLM-based form/notice-interpretation task works well enough to deploy in government contexts; the applicant-facing half of the same workflow is untouched and uses the same core techniques (document understanding, guided form-fill), so there's no new capability gap to wait on.

## Skill Angle

A standalone "Notice Explainer & Response Drafter" skill: the user pastes the text of a benefits notice/letter plus 2-3 sentences on their situation; the skill explains the notice in plain language, lists exactly what's needed and by when, and drafts a response or appeal letter. This is the single-document judgment task; the full project additionally tracks multiple pending deadlines and pre-fills entire applications over time, which needs persistent state the skill doesn't carry.

## MVP Sketch

Scope to one state (e.g., California SNAP) and one notice type (recertification). Stack: a document-upload + chat interface, an LLM prompted with the state's specific SNAP recertification rules (manually curated rule pack), and a deadline tracker stored per user. Single experiment: recruit 15-20 real or simulated applicants through a legal-aid or benefits-navigator nonprofit partner, compare completion rate and time-to-submit against their normal unassisted process.

## Risks & Open Questions

- Applicants may not trust an AI tool with sensitive income/household data without a credible privacy story — needs a clear no-retention or local-processing design, not just a privacy policy.
- State-by-state rule variation means the rule-pack curation work scales linearly with coverage; an MVP locked to one state won't easily generalize without ongoing maintenance investment.
- Incorrect guidance on a benefits application carries real consequences (fraud flags, benefit loss) — needs explicit human-review framing and liability disclaimers, not an "autonomous filer."
- A well-resourced incumbent (Code for America, Propel) could extend their existing caseworker-side tooling to applicants directly, closing this gap faster than an independent team could.
