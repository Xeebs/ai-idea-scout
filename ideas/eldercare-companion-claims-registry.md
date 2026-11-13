# Honest Companion: An Independent Evidence Registry for Elder-Care AI Companion Claims

- **Status**: PROPOSED
- **Date**: 2026-11-13
- **Topic**: Applied AI for underserved domains
- **Source**: research/2026-11-13-applied-ai-underserved-domains-5th.md · P4
- **Maturity verdict**: PARTIAL — real independent academic evaluations exist (a 2026 NYU-hosted meta-analysis, a JMIR Aging review showing mixed/null results across Pepper/AIBO/Paro, a 2023 Frontiers paper on deception risk) but they are fragmented, small-sample, one-off studies, not a sustained, running benchmark holding ongoing vendor claims (e.g. ElliQ's unreplicated self-reported "95.9%" loneliness-reduction figure) accountable.
- **Format**: BOTH
- **Data Sources**: CONNECTED — ClinicalTrials.gov's public API and PubMed/PMC's public API (both mature, free, and already used for exactly this kind of evidence aggregation) to pull registered trials and published studies on a given companion product. MANUAL for the vendor-side input: the user pastes the specific marketing claim, press release, or product page text being checked, since vendor claims aren't published through any structured API.

## The Gap

The most-repeated public claim in this space — ElliQ's "95% reduction in loneliness" — traces to a state-agency press release describing a self-selected, screened group, not a controlled study, a gap a critical commentary explicitly calls out. Meanwhile a 2025 nursing-home feasibility study of "Meela" showed improvement on only 23 completers with authors themselves calling for larger trials, and two relevant registered trials are Withdrawn or not-yet-recruiting. Real independent research exists but is scattered across journals and preprints with no single place that tracks, scores, and updates vendor claims against it.

## The Project

A public registry, per companion product, that pairs every major marketing claim with: (a) what independent, peer-reviewed or registered-trial evidence actually exists for it, pulled live from ClinicalTrials.gov and PubMed; (b) a methodology-quality score (sample size, controlled vs. uncontrolled, vendor-funded vs. independent, replicated vs. single-study); and (c) a plain-language verdict ("unreplicated self-report," "small controlled pilot," "no evidence found"). New vendor claims get submitted (by the user, a journalist, or a facility buyer) and checked against the same pipeline, keeping the registry current as new press releases and studies appear — unlike a one-time meta-analysis that goes stale.

## Tangible Impact

**Population**: Nursing-home administrators and family caregivers deciding whether to purchase or recommend an AI companion device for an older adult — a decision point touching a meaningful share of the roughly 1.3 million US nursing-home residents and the far larger population of seniors living alone whose families are weighing devices like ElliQ, plus the clinicians and policy staff who cite these claims in funding and procurement decisions.

**Mechanism**: Replacing a vendor's self-reported statistic with a transparent, sourced, continuously-updated evidence score lets a buyer weigh an actual methodology-quality signal before a purchase or facility-wide rollout decision, instead of a marketing number with no visible counter-evidence.

**Measure**: (1) number of distinct vendor claims tracked and kept current (checked against new PubMed/trial-registry entries within 90 days of publication); (2) adoption by at least one procurement-facing audience (a state aging-services agency, a nursing-home association) citing the registry in a purchasing decision; (3) a before/after survey of facility buyers' confidence in a given claim after seeing the registry entry.

## Why Now

ClinicalTrials.gov and PubMed/PMC's APIs are mature, free, and already widely used for exactly this kind of automated evidence-matching; what's new is simply that 2026 produced enough citable, scattered independent studies (NYU meta-analysis, JMIR Aging review, the Meela feasibility study) to make a registry pulling them together immediately useful rather than empty.

## Skill Angle

A "Companion Claim Verifier" skill: the user pastes a specific vendor claim or press-release excerpt; the skill searches ClinicalTrials.gov/PubMed for relevant trials and studies, scores the claim's methodology support, and returns a plain-language verdict with citations. This is the one-shot verification judgment; the full project additionally maintains the registry as a living, browsable, continuously-refreshed public resource across many products, which needs persistent storage and scheduled re-checks the skill alone doesn't provide.

## MVP Sketch

Scope to the 3-4 most publicly claimed companion products (ElliQ, Meela, Pepper/Paro academic coverage) with manually curated claim entries to start, backed by a script that queries ClinicalTrials.gov and PubMed APIs on a schedule and flags new matching entries for human review before publishing an update. Single experiment: publish the initial registry and track whether any aging-services trade press (Route Fifty, StateScoop, skillednursingnews.com — all already covering this space) cites or links to it within 60 days.

## Risks & Open Questions

- Legal exposure from publicly scoring a named vendor's claim as "unreplicated" or "no evidence found" — needs careful, strictly evidence-sourced language and likely a legal review before launch, not a casual blog-style take.
- The underlying academic evidence itself is thin and sometimes conflicting (the digest notes two contradictory accounts of the same UK Pepper trial); the registry's credibility depends on transparently showing disagreement, not papering over it with a single score.
- A well-resourced advocacy or research org (AARP, a university aging-research center) could plausibly build this faster with more institutional credibility than an independent small team.
- Vendors could simply decline to engage or dispute the registry's framing, limiting its practical leverage without a procurement-side partner who already requires evidence citations.
