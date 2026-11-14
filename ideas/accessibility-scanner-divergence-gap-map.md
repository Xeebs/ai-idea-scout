# Gap Map: A Validated Automated-vs-Manual Accessibility Scanner Divergence Database

- **Status**: PROPOSED
- **Date**: 2026-11-14
- **Topic**: Applied AI for underserved domains
- **Source**: research/2026-11-14-applied-ai-for-underserved-domains.md · P1
- **Maturity verdict**: PARTIAL — vendor blogs quantify the automated-vs-manual gap in aggregate (TestParty: 30-70%; AudioEye: "2.5x more issues"; a 35-audit study: Evinced 62.8% vs axe-core 22.6%) but no product ships "which specific WCAG success criteria does automation reliably miss" as a consultable deliverable; even the founder soliciting this data (Inkluso, r/accessibility, 2026-11-10) doesn't have it yet.
- **Format**: BOTH
- **Data Sources**: CONNECTED — the project runs its own headless-browser scan directly via axe-core + Chromium (both mature, widely-used open-source libraries) against a target URL; no manual paste required for the core workflow. A secondary manual path lets a user paste an existing third-party scanner's JSON/CSV export (e.g. from Lighthouse, Siteimprove, WAVE) to cross-reference against the gap-map instead of re-scanning.

## The Gap
A startup founder building an axe-core-based accessibility scanner publicly admitted automated checks cover "roughly 30 to 40 percent of WCAG" and asked r/accessibility auditors to help him find where his own tool's report misleads a non-expert buyer (r/accessibility, "Auditors: where does an automated accessibility report mislead a non-expert?", 2026-11-10). WebSearch confirmed the underlying data exists in fragments across vendor marketing (TestParty, AudioEye, a 35-audit Evinced-vs-axe-core study) but no one has consolidated it into a WCAG-criterion-by-criterion confidence map that a non-expert buyer — or a developer relying on a green scan score — can actually consult before shipping.

## The Project
A continuously-validated, open reference database mapping every WCAG 2.2 success criterion to a confidence score: "automation catches this reliably" / "automation catches this partially — verify manually" / "automation cannot test this — requires a human." The score for each criterion is derived by running multiple open-source scanners (axe-core, Pa11y, IBM Equal Access) against a corpus of real sites with independently-published manual-audit findings, then measuring how often automation's pass/fail agreed with the manual verdict. The project exposes this as (1) a public API/website anyone can query by WCAG criterion, and (2) a CLI/CI tool that takes a scan result and annotates it: "scanner says pass, but this criterion has only 40% automation-reliability — schedule a manual check."

## Tangible Impact
**Population**: Small-to-mid-size organizations (estimated tens of thousands of U.S. small businesses doing some accessibility remediation per WebAIM's annual Million report coverage) that rely on an automated scanner's "compliance score" as their only accessibility signal because they can't afford a full manual audit — and, downstream, the ~61 million U.S. adults with a disability (CDC) who hit the barriers that score missed.
**Mechanism**: Instead of a false-confidence green checkmark, the org gets a prioritized, criterion-specific list of exactly which checks still need a human — turning "we passed the scan" into "we passed the scan AND know these 6 specific things still need eyes on them," closing real barriers before launch instead of after a complaint or lawsuit.
**Measure**: (1) % of criteria in the gap-map validated against ≥3 independent manual-audit corpora; (2) for pilot orgs, change in real barriers found in a follow-up manual spot-check after using the gap-map vs. a scan-only baseline; (3) API query volume / CI-tool adoption as a proxy for reach.

## Why Now
Open-source scanners (axe-core 4.12, Pa11y, IBM Equal Access) are mature and stable enough to run head-to-head at scale cheaply; LLMs make it newly tractable to automatically classify and cluster manual-audit findings against WCAG criteria at the volume needed to build this corpus without a large human-labeling team.

## Skill Angle
A companion skill takes a pasted automated scan report (JSON/CSV from any scanner) plus the target page's live URL, cross-references it against a bundled snapshot of the gap-map, and drafts a plain-English "manual review checklist" ranked by risk — the design/review aid a non-expert can run before their next release, independent of whether they ever touch the full live project.

## MVP Sketch
Scope: pick 10 WCAG criteria most commonly cited as "automation misses this" in the existing vendor blogs (image alt quality, focus order, meaningful sequence, error identification, etc.). Run axe-core + Pa11y against 30 public sites that already have a published manual audit (government/university accessibility statements often publish these). Compute per-criterion agreement rate. Ship as a static queryable table + a simple CLI that annotates a fresh axe-core JSON output. Single experiment: does the gap-map's "needs manual check" flag correlate with where a real manual auditor actually found something the scanner missed, on a held-out 10-site sample?

## Risks & Open Questions
- Corpus-building depends on finding enough paired automated-scan + independently-published manual-audit data; this may be the hardest part to source at scale.
- Scanner vendors have an incentive to dispute or ignore a third-party gap-map that makes their product look weaker than its marketing claims.
- Risk this becomes "yet another accessibility checklist" unless the confidence scores are empirically derived and re-validated on a cadence, not just restated vendor claims.
- Legal liability framing (ADA/Section 508) could make orgs reluctant to publicly adopt a tool that documents known gaps in their compliance process.
