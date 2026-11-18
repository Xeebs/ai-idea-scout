# Built With, Not For: A Cross-Disability Co-Design Certification Protocol for Assistive AI

- **Status**: PROPOSED
- **Date**: 2026-11-18
- **Topic**: Applied AI for underserved domains
- **Source**: research/2026-11-18-applied-ai-for-underserved-domains.md · P6
- **Maturity verdict**: PARTIAL — several named frameworks address the general co-design problem (TACTIC's academic four-loop process, Google's internal "Natively Adaptive Interfaces," INNklusion's course-based initiative, an arXiv "ability-diverse collaboration" position paper), but none is a shared, checkable certification or standard other assistive-AI vendors could adopt; each is research-stage, single-institution, or one company's internal practice.
- **Format**: BOTH
- **Data Sources**: MANUAL — a submitting builder team completes and uploads a structured co-design-process questionnaire plus evidence links (named community partners, consent/compensation records, workshop artifacts); no external API or connector exists for "has this team actually co-designed with the community" because the evidence is inherently organizational and documentary, not data another system already holds.

## The Gap
A 2026 CHI paper reports that "a prominent online deaf community has banned all posts proposing technology ideas intended to 'help' deaf people," viewing sign-language AI as a potential threat to "deaf minoritized language and community-based knowledge" rather than a benefit — a structural, community-wide trust collapse, not a single bad product. Vendors like Rylo respond individually by claiming to be "built with the Deaf community," but each asserts this on its own terms with no common standard a skeptical community member, funder, or procurement officer could check it against. This repo's existing `asl-interpreting-deaf-cogovernance-registry` idea builds a Deaf-reviewer-staffed scorecard specifically for ASL interpreting vendors; this idea differs in scope and mechanism — it is a cross-disability (not ASL-only), process-stage (not post-hoc vendor review), adoptable certification protocol any assistive-AI builder in any disability vertical can apply from project inception, not a registry that audits finished products after the fact.

## The Project
A certification protocol with two parts: (1) a published, concrete process standard specifying what counts as genuine co-design — named community partner organizations, documented and compensated participation (not token consultation), participant veto power over launch, and a plain-language summary of what was changed because of community input vs. what the builder decided unilaterally; (2) a lightweight public registry where any team can submit evidence against that standard and receive a scored, time-stamped certification reviewed by a rotating panel of disabled community reviewers drawn from the relevant vertical (Deaf reviewers for ASL/hearing-related tools, mobility-disabled reviewers for physical assistive tech, etc.), making the certification itself a signal funders and the community can trust across any assistive-AI domain, not just one.

## Tangible Impact
**Population**: The roughly 1.3 billion people globally who live with a significant disability (WHO, 2023 estimate), specifically the subset engaging with AI tools built to "help" them — the CHI paper's documented Deaf-community backlash is the proof case that this population will actively reject tools it wasn't genuinely built with, at a scale that threatens adoption of otherwise-useful assistive AI across every disability vertical, not just Deaf/ASL.
**Mechanism**: A builder who completes certification has concrete, checkable evidence of genuine community involvement to show skeptical users, funders, and procurement officers, lowering the trust barrier that currently causes wholesale community rejection of outsider-built tools (as documented in the CHI paper); a builder who can't or won't complete it signals exactly that risk before launch, not after a backlash.
**Measure**: Number of certified projects per disability vertical over time; community-reviewer-reported trust/legitimacy score pre- vs. post-certification for a pilot cohort of projects; adoption/retention rate of certified vs. uncertified comparable tools within the same disability community, where measurable.

## Why Now
The CHI paper's community-wide ban finding is a 2026 escalation from isolated complaints to structural rejection, and at least four independent organizations (Ontario Tech's TACTIC, Google Research, INNklusion, and an arXiv position-paper team) have converged on wanting a shared co-design standard in the same window — the demand signal is dense but none has shipped a checkable, cross-vertical certification yet.

## Skill Angle
A companion skill takes a team's draft product plan and a description of their community-engagement process so far, and produces a gap report against the certification standard — naming exactly which required evidence is missing (e.g. "no documented compensation for community reviewers," "no veto-power mechanism described") before the team applies for formal certification.

## MVP Sketch
One disability vertical to start (Deaf/ASL, given the CHI evidence and existing Rylo-style claims to test against), a published one-page process standard, a simple submission form plus Airtable-backed review queue, and 3-5 volunteer Deaf community reviewers scoring the first cohort of submissions. The single experiment: do certified projects in a pilot cohort see measurably higher community trust/adoption signals (surveyed or observed) than a matched set of uncertified ones over a few months.

## Risks & Open Questions
- Certification bodies can become captured or rubber-stamp over time (a known failure mode of accessibility/ethics certifications generally) — reviewer rotation and public evidence trails are a partial mitigation, not a solved problem.
- Recruiting and fairly compensating disabled community reviewers across multiple verticals is itself a real operational cost this project must budget for, not treat as free labor.
- Risk that the community-specific standard (what counts as "genuine" co-design) varies enough across disability verticals that one protocol can't honestly generalize — the MVP's single-vertical scope is partly a hedge against this.
- A certification with no legal or funder-mandated teeth may simply be ignored by builders who don't already want to do this work; distribution/adoption strategy (e.g. funder requirement) matters as much as the standard itself.
