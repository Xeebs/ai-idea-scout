# Policy Diff: A Usage-Policy-to-Guardrail-Config Drift Detector

- **Status**: PROPOSED
- **Date**: 2026-11-14
- **Topic**: AI safety & guardrails in production
- **Source**: research/2026-11-14-ai-safety-and-guardrails-in-production.md · P4
- **Maturity verdict**: OPEN — GitHub search returned nothing; two rounds of web search found only generic "configuration drift detection" marketing content (a single vendor's SEO blog network) and gateway products that apply one guardrail config uniformly across providers, with no claim of diffing against updated provider policy text. No tool, product, or paper diffs a team's own deployed guardrail ruleset against a provider's revised usage policy.
- **Format**: BOTH
- **Data Sources**: CONNECTED — pulls the provider's public usage-policy page (e.g. anthropic.com/legal/usage-policy, OpenAI's usage policies) on a schedule; no official structured/versioned policy API exists today for any major provider, so the scraper-plus-diff component would need to be built as part of this project. Paired with the team's own guardrail config, read from wherever they keep it (a YAML/JSON rules file in their repo, pulled via the GitHub/GitLab API — a mature, already-existing connector) rather than pasted by hand.

## The Gap
Anthropic's updated Usage Policy took effect 2026-11-12, adding a new prohibited-use clause and revising rules on political content, weapons, surveillance, and high-risk domains (healthcare, finance). Teams who built guardrails against the prior policy version have no tool that flags which configured rules are now stale, under-covering, or non-compliant against the new clauses — they re-read the policy by hand, if at all. ConductAtlas tracks provider-policy-text version-to-version changes but is read-only documentation; nothing plugs a team's own deployed ruleset into that diff.

## The Project
A service that watches a provider's usage-policy page for changes (diffing the raw text release-to-release, the same mechanism ConductAtlas already proves works for human-readable tracking), extracts newly-added or materially-changed clauses, maps them against categories in the team's own guardrail config (read from their repo), and produces a flagged report: "new clause X has no corresponding rule," "existing rule Y now under-covers clause Z's broadened scope." It's the missing link between a provider's policy text and a team's actual enforcement config, not another policy-text tracker.

## Tangible Impact
**Population**: engineering and compliance staff at the thousands of startups and mid-size companies building production LLM products on top of a foundation-model API (Anthropic, OpenAI, Google) who are contractually bound to the provider's usage policy and risk API account suspension for undetected non-compliance — a population sized roughly to the active developer base of any major model API, in the tens of thousands per public developer-count disclosures from the major providers.
**Mechanism**: converts a yearly manual policy re-read (if it happens at all) into an automatic, dated flag the moment a provider updates its policy, cutting the window between "policy changed" and "team knows their guardrails are stale" from however long until someone notices to the detector's polling interval.
**Measure**: time from provider policy update to first flagged report (target: under 24 hours vs. indefinite today); number of genuinely under-covered categories caught per policy update (validated against a held-out historical policy diff, e.g. this exact Nov-12 update); false-positive rate on flagged rules (teams shouldn't be spammed with noise on cosmetic wording changes).

## Why Now
Anthropic's Nov-12 usage-policy update, two days before this digest, is a live, concrete test case: a real policy change with specific new clauses (abusive-behavior prohibition, revised high-risk-domain carve-outs) exists right now to validate the detector against, and model providers revising usage policies roughly yearly means this gap recurs predictably.

## Skill Angle
A one-shot companion skill: given the pasted text of a provider's policy update (redline or full text) and a pasted or uploaded copy of the team's current guardrail ruleset, produce the same flagged gap report without needing the continuously-running watcher — useful the moment a policy update is announced, before the project's own scraper has a chance to fire, and for teams who'd rather run this ad hoc than stand up a watching service.

## MVP Sketch
A script that takes two policy-text snapshots (old/new) plus a team's guardrail config file, extracts added/changed clauses via a structured diff, and uses an LLM pass to map each clause against the config's existing categories, flagging gaps. Validate against the real Anthropic Nov-11-vs-Nov-12 policy diff and a sample guardrail config: does it correctly flag the new "sustained abusive behavior toward our models" clause as uncovered? Buildable by 1 person in 2-3 weeks.

## Risks & Open Questions
- Scraping a provider's legal page for structured diffing is fragile against page redesigns; needs a resilient extraction approach (e.g. targeting the policy's own changelog/versioning if one exists, falling back to full-page diff).
- LLM-based clause-to-rule mapping risks false negatives on subtly-reworded clauses that are semantically covered but lexically different from the existing rule's wording — needs a human-review step before trusting the flag as actionable.
- Strongest case this is already solved: if a provider itself ships a structured, versioned policy API or changelog (plausible given growing regulatory pressure), the scraping half of this project becomes unnecessary overnight.
