# Clear Signal: A Self-Service Smart-Device and Cloud-Account Abuse Auditor for DV Survivors

- **Status**: EXPLORING (promoted 2026-11-13 cycle 61: evidence density — ≥2 independent threads, Refuge UK's reporting on rising wearable/cloud-linked abuse cases and the independent SSWR 2026 conference study finding advocates' only taught strategy is "turn off location," both confirming no automated cross-account audit tool exists, only manual checklists)
- **Date**: 2026-11-13
- **Topic**: Applied AI for underserved domains
- **Source**: research/2026-11-13-applied-ai-underserved-domains-6th.md · P3
- **Maturity verdict**: OPEN — GitHub search found multiple device-side stalkerware/malware scanners (GetByeBye, selfguard, Zero, StealthDetect, tsunamicodes/Stalkerware_detection, foundation-safe-harbor), all scanning a single phone for spyware apps, none auditing cross-account or smart-home/wearable cloud linkage. The closest real matches (Nansen Digital Forensic Services, Salvation Army's "Safer in the Home" tech health check, eSafety.gov.au's checklist) are all human-led or a manual worksheet, not a self-service AI tool.
- **Format**: BOTH
- **Data Sources**: MANUAL (deliberately, not CONNECTED) — the survivor or advocate uploads or pastes screenshots/exports from account security-checkup pages (Google Security Checkup, Apple ID device list, Find My/Life360 paired-device screens, smart-home app shared-access lists, shared calendar/photo permissions). A live-login CONNECTED version is explicitly ruled out at this stage: handling a DV survivor's actual account credentials turns the audit tool itself into a new attack surface, and an OAuth consent flow can itself be visible to an abuser with device access — MANUAL screenshot review is the safer design choice here, not a fallback.

## The Gap
Refuge (UK) reports a "significant rise" in abuse cases misusing wearables and AI, including a documented case where a smartwatch left behind during a flight kept surveilling the survivor through its linked cloud account even after the device was recovered. A 2026 SSWR conference study found that within most agencies, the only explicit tech-safety strategy taught to clients is disabling phone location tracking — advocates self-reported feeling undereducated on tech-related safety planning more broadly. The study's own proposed fix, a "Technology Abuse Clinic," is a human-staffing model requiring on-call cybersecurity experts, not an AI tool. No product found does automated device/account-linkage auditing for survivors.

## The Project
A guided, self-service audit flow: the survivor (or an advocate alongside them) uploads screenshots of their account security and device-sharing settings pages across the platforms they actually use, and the tool pattern-matches against a maintained database of known abuser-tactics-by-platform (legacy shared Apple/Google family accounts, still-linked wearable cloud accounts, smart-home app co-owner access, calendar/photo sharing left over from the relationship) to produce a prioritized "what to revoke, in what order, and why" report. The maintained tactics database is the part that must stay current — platforms change their settings UIs constantly — which is the genuine infrastructure piece; the audit-and-report logic on top of it is the centerpiece.

## Tangible Impact
**Population**: domestic violence survivors in the immediate post-separation period whose former partner retains or retained shared access to smart devices or cloud accounts. CDC estimates roughly 41 million US women and 26 million US men have experienced contact sexual violence, physical violence, and/or stalking by an intimate partner in their lifetime; NNEDV's Safety Net surveys report a majority of advocates' clients disclose tech-facilitated stalking specifically.
**Mechanism**: surfaces abuser-linked access points in minutes that a manual advocate checklist — which the SSWR study found stops at "turn off phone location" — would miss, closing the specific cross-account/smart-home blind spot the study's advocates admitted they aren't trained to check.
**Measure**: (1) number of abuser-linked access points found per audit vs. the baseline manual-checklist detection rate (measurable via a side-by-side pilot with a partner DV agency); (2) time to complete an audit (minutes, vs. advocates' self-reported ad hoc/undereducated process); (3) survivor-reported reduction in unexplained "they always know where I am" incidents after remediation, tracked at 30/90 days.

## Why Now
The smartwatch/cloud-account case and the SSWR 2026 study's finding that advocates feel undereducated on exactly this gap both surfaced in the last reporting cycle, and consumer smart-device/cloud-account settings pages are now standardized enough (Google Security Checkup, Apple ID device management) that a screenshot-based pattern-match is feasible without any new platform API.

## Skill Angle
Trigger: a DV advocate or survivor has a batch of account/device settings screenshots and needs an immediate read on what's risky, without waiting for an agency audit slot. Inputs: the screenshots themselves (paste or upload), plus which platforms they're from. Output: a prioritized, plain-language list of flagged access points with a revoke-this-first ordering and a one-line reason each — a one-shot self-checkup distinct from the project's maintained, continuously-updated tactics database and advocate-facing workflow.

## MVP Sketch
Partner with one DV advocacy org to validate an initial tactics database covering 3-4 common platforms (Google, Apple, one smart-home ecosystem, one location-sharing app), build the screenshot-to-flagged-report pipeline, and pilot it against the org's existing manual checklist on 10-15 real (consented, anonymized) cases to compare detection rates. 3-4 weeks, 1-2 people plus the partner agency's review.

## Risks & Open Questions
- The single highest risk is physical safety: if a survivor runs this on a device the abuser can see activity on, or if the tool itself logs identifying data insecurely, it could cause direct harm — this needs explicit, prominent safety-planning guidance (private device, incognito/clear history) before any audit step, not just a disclaimer.
- Platform settings UIs change frequently; the tactics database needs real maintenance capacity, not a one-time build, or it silently goes stale and gives false reassurance.
- Strongest reason this might already be solved: an advocacy org could have an internal, unpublished version of this checklist already — worth direct outreach before assuming greenfield.
- A pattern-match audit can't catch genuinely novel abuser tactics not yet in the database; it should be framed as a floor, not a guarantee.
