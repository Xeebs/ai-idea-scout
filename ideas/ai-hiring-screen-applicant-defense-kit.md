# Screen Defense: An Applicant-Side Toolkit Against AI Hiring-Screen Exclusion

- **Status**: PROPOSED
- **Date**: 2026-11-13
- **Topic**: Applied AI for underserved domains
- **Source**: research/2026-11-13-applied-ai-underserved-domains-5th.md · P3
- **Maturity verdict**: OPEN — every mitigation found (Mentra, OECD governance recommendations) targets employers or policymakers; search surfaced only legal/regulatory response (Mobley v. Workday, ACLU's FTC complaint, a HireVue complaint from a Deaf Indigenous applicant, EEOC ADA guidance), with commentary explicitly noting proposed law gives rejected applicants no mechanism to challenge an algorithmic outcome. No applicant-side software tool was found.
- **Format**: BOTH
- **Data Sources**: MANUAL — the applicant pastes the job posting text and their own resume/application draft, plus (optionally) details of a disability or conviction history they're deciding whether/how to disclose. No API exposes employer-side ATS/AI-screening logic to applicants or third parties, so a CONNECTED version reaching into the actual screening model is not viable — this gap is exactly why the tool has to work from visible, applicant-side signals instead.

## The Gap

Vera Institute (Oct 2026) warns AI hiring tools are "filtering job applications before they ever reach a human reviewer" and "reinforcing barriers for formerly incarcerated people." AEI separately documents AI-driven employment losses concentrated among disabled workers. Every response found — Mentra's bias-reduction product, OECD governance guidance, the active Mobley v. Workday lawsuit — operates on the employer or policy side. No tool helps the person actually being screened understand their risk or exercise the (limited) rights they already have.

## The Project

A two-part toolkit. First, a screening-risk scanner: given a job posting and the applicant's draft resume/application, flag signals correlated with automated pre-screening risk — ATS keyword mismatches, employment-gap flags, disclosure checkboxes (conviction history, disability accommodation) known to interact badly with automated filters — and suggest concrete edits. Second, an ADA accommodation-request drafter: under current law, a disabled applicant can request an alternative to a purely automated screening step; the tool drafts that specific request in the applicant's own words, tied to the actual posting and process described. A lightweight, opt-in, anonymized log of outcomes (applied, screening method if disclosed, result) across users builds an aggregate evidence base usable by legal-advocacy groups investigating a given employer or vendor's pattern — without the project itself making unprovable claims about any single rejection's cause.

## Tangible Impact

**Population**: Disabled job seekers and formerly incarcerated job seekers navigating employer-side AI pre-screening they have no visibility into — AEI's analysis puts AI-driven job losses as concentrated in automation-prone roles disproportionately held by disabled workers, and Vera Institute documents the same filtering effect for people with conviction histories, both sizable and currently unserved populations within the broader US disabled (61M, per CDC) and formerly-incarcerated (~70-100M with a record, per NELP estimates) populations.

**Mechanism**: Surfacing known AI-screening risk signals before submission lets an applicant make an informed choice about disclosure framing and application edits instead of submitting blind; the accommodation-request drafter gives them a concrete, legally-grounded action (a request for human review) that today almost no applicant knows exists or how to invoke.

**Measure**: (1) rate of accommodation requests successfully filed vs. drafted (a proxy for whether the drafting lowers the activation-energy barrier); (2) self-reported change in human-review outcomes among users who filed a request vs. those who didn't; (3) volume and employer/vendor concentration of the anonymized outcome log, usable by legal-advocacy partners.

## Why Now

The underlying legal hook (ADA's reasonable-accommodation right extended to automated screening steps) and the Mobley v. Workday litigation are both live and newly citable in 2026, giving this tool a concrete legal mechanism to operationalize rather than a vague "fight the algorithm" framing that wouldn't be actionable.

## Skill Angle

A "Screening-Risk & Accommodation Drafter" skill: the user pastes a job posting and their resume/disclosure situation; the skill flags likely automated-screening risk signals and drafts an ADA accommodation-request email tailored to the posting. This is the single-application judgment task; the full project additionally maintains the opt-in aggregate outcome log across many applicants and users over time, which needs persistent, shared storage the skill alone doesn't provide.

## MVP Sketch

A single-page tool: paste job posting + resume, get a risk-flag list and a draft accommodation-request email. No outcome-logging in v1 — that's the riskiest, most infrastructure-heavy piece and should wait until the core drafting tool proves useful. Single experiment: partner with a disability-employment or reentry-employment nonprofit to have 20-30 real job seekers use it on real applications and report whether they filed the drafted request and what happened.

## Risks & Open Questions

- The tool cannot actually see or diagnose any specific employer's AI model — risk flags are necessarily heuristic and could be wrong or give false confidence; framing must stay firmly "here's a known risk pattern and a right you can exercise," never "here's why you were rejected."
- Encouraging disclosure (for an accommodation request) could itself trigger the exact bias it's trying to counter if the employer's process isn't actually ADA-compliant; needs legal review before any user-facing launch.
- The aggregate evidence-log idea is valuable but legally and privacy-sensitive (potential for defamation/accuracy disputes about named employers); should be scoped as a v2 partnership with an actual legal-advocacy org, not shipped solo.
- It's plausible a career-coaching or disability-employment nonprofit already offers manual versions of this advice one-on-one; worth confirming no existing structured digital tool does this before building.
