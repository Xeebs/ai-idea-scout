# Scenario 1 — Mid-size healthcare SaaS company

## Input

> We're a healthcare SaaS company, about 280 employees. We just started piloting mem0 as a shared memory layer so our teams' AI agents can draw on institutional knowledge instead of each team's agent starting from zero. Teams involved: Support (uses Zendesk, answers customer tickets), Sales (uses Salesforce CRM notes and call summaries), Clinical Ops (reviews case summaries pulled from our EHR integration — this touches real patient data), and Legal (handles contracts, NDAs, and incident-response write-ups). We use Okta for SSO with roles roughly matching those four teams plus an Admin role. We're a HIPAA-covered entity because of the Clinical Ops data. Draft us a memory-access governance policy before we open this up org-wide. One thing that already happened: a Support agent's memory surfaced a snippet from a Legal incident-response note during a customer call — that's what triggered this whole effort.

## Pass criteria

- [ ] Produces 3–7 memory categories that map clearly to the four named teams/data sources (e.g., something like General/Internal, Support History, Sales/CRM, Clinical/PHI, Legal/Confidential) — not more sources than were named, not invented sources.
- [ ] Clinical Ops's category is tagged with a sensitivity tier reflecting PHI/HIPAA (Confidential or equivalent top tier), and Legal's category is similarly tagged Confidential/Restricted.
- [ ] The access matrix gives each team read/write on its own category, and explicitly denies Support and Sales read access to Clinical/PHI and Legal/Confidential categories by default — directly addressing the stated incident (Support surfacing a Legal note).
- [ ] Redaction rules explicitly name PHI and privileged/incident-response legal content as trigger patterns, each with a stated hard-block or mask-and-flag treatment.
- [ ] Provenance schema includes at minimum source_system, contributing_team, contributing_agent_or_user, ingestion_timestamp, sensitivity_tier, redaction_status — and reasonably adds a compliance-relevant field given HIPAA (e.g., a PHI flag or legal-hold flag).
- [ ] Audit & Go-Live checklist states a cadence and a concrete, testable go-live bar (e.g., zero cross-boundary leaks in a red-team simulation), referencing the kind of incident that already happened.
- [ ] Open Questions section surfaces at least one real gap (e.g., Admin role's scope wasn't defined, or whether Clinical Ops needs any read access to Legal during investigations) rather than claiming the policy is fully complete.
- [ ] Does not claim HIPAA compliance is achieved by this document alone; says legal/compliance sign-off is still required.
- [ ] Does not invent teams, data sources, or regulations beyond what was stated (no mention of GDPR, SOC2, etc. unless the user had said so).

## Self-check notes

Walking the procedure: categories derive directly from the four named teams' data sources, each gets a tier (Clinical/PHI and Legal get Confidential, Support and Sales get Restricted/Internal). The access matrix denies cross-team Restricted/Confidential reads by default, which directly prevents a repeat of the stated Support→Legal leak. Redaction rules name PHI and privileged legal language explicitly. Provenance schema matches the minimum fields plus a PHI/legal-hold flag given HIPAA context. Open Questions correctly flags the undefined Admin role scope, since the user never said what Admin can see. Output stays within six sections, Markdown, no compliance certification claim. Scenario passes.
