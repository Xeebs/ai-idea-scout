# Vetted Answer: A Safety-Evaluated Assistant and Advocate Review Aid for Tech-Facilitated-Abuse Questions

- **Status**: EXPLORING (promoted 2026-11-13 cycle 61: evidence density — 3 independent sources, the USENIX Security 2026 paper (Prakash et al.), Refuge's narrow-scope live chatbot, and Chayn's discontinued 3-year "Little Window" pilot, all confirming only narrow/unevaluated/discontinued attempts exist)
- **Date**: 2026-11-13
- **Topic**: Applied AI for underserved domains
- **Source**: research/2026-11-13-applied-ai-underserved-domains-6th.md · P4
- **Maturity verdict**: PARTIAL — WebSearch found Refuge (UK) runs a live chatbot offering automated tech-abuse support, co-designed with a PhD researcher and tested directly with survivors, but scoped narrowly to device-securing guidance, not general TFA Q&A. Chayn's "Little Window" chatbot ran a 3-year survivor-tested pilot before being taken down in 2020 over safety/sustainability concerns. The cited USENIX Security 2026 paper (Prakash et al., arXiv 2602.17672) found two models already built for intimate partner violence contexts specifically, but none independently vetted as safe/complete/actionable at scale. GitHub search for "domestic violence chatbot safety assistant" returned no relevant repos.
- **Format**: BOTH
- **Data Sources**: MANUAL — the survivor's or advocate's question about technology-facilitated abuse, pasted verbatim, is checked against a maintained, vetted reference knowledge base assembled from NNEDV Safety Net, Refuge's published guidance, and the Prakash et al. paper's own documented failure cases. The knowledge base ships with/is maintained by the project itself; no live external API exists for "vetted TFA guidance" to connect to.

## The Gap
Prakash et al. (USENIX Security 2026) evaluated four LLMs' responses to survivor questions about technology-facilitated abuse specifically because "LLMs are already integrated into widely used online platforms where survivors seek support," and because advocates are scarce and generic online TFA information is often inaccurate or misleading. Their own evaluation axes — accuracy, completeness, safety, and actionability — are framed as an open research question, not a solved one. Two IPV-context-specific models already exist per that paper, but neither is independently vetted as safe/complete/actionable at scale, and no shipped general-purpose "TFA-safe assistant" was found.

## The Project
A maintained, safety-reviewed knowledge and guardrail layer purpose-built for TFA questions: a vetted reference base covering the most common survivor questions (device-securing, account-separation, evidence-preservation, safety-planning around disclosure), paired with crisis-detection logic that routes genuinely high-risk disclosures (immediate danger, suicidal ideation) to a human hotline handoff rather than answering in-line — the exact safety failure mode an unvetted general LLM risks. The vetting-and-escalation pipeline is the centerpiece, built and re-evaluated against the Prakash et al. axes on a fixed cadence as new TFA tactics emerge, not a one-time model fine-tune.

## Tangible Impact
**Population**: survivors experiencing technology-facilitated abuse who seek help outside advocate business hours or without advocate access, and the advocates who must vet AI-drafted guidance before passing it to a client. Prakash et al.'s own framing establishes this population directly: survivors already turn to platforms with embedded general LLMs specifically because advocates are scarce.
**Mechanism**: a safety-vetted knowledge layer and advocate-facing review tool improves accuracy/completeness/safety/actionability of TFA guidance relative to unvetted general-LLM answers — the exact axes the cited paper measured as deficient — and gives advocates a fast second opinion before sending AI-assisted guidance to a survivor, instead of either blocking AI use entirely or trusting it unreviewed.
**Measure**: (1) accuracy/completeness/safety/actionability scores vs. a baseline general-purpose LLM on the same TFA question set, replicating Prakash et al.'s own eval methodology; (2) advocate time-to-review an AI-drafted answer vs. drafting one from scratch; (3) survivor-reported helpfulness and perceived safety rating, collected via a partner agency pilot.

## Why Now
The Prakash et al. paper's publication gives a concrete, citable eval methodology and failure-case set to build the vetted knowledge base and test suite against — before this, there was no documented, academically-grounded baseline for what "safety-vetted" even means for this specific use case.

## Skill Angle
Trigger: an advocate has drafted or received an AI-generated answer to a survivor's TFA question and needs a fast safety check before sending it on, or a survivor-facing platform wants to review its own chatbot's TFA-adjacent responses. Inputs: the question and the candidate answer, pasted verbatim. Output: a scored check against the four Prakash et al. axes (accuracy, completeness, safety, actionability) with specific gaps flagged and a revised answer suggested — a one-shot review aid for advocates, distinct from the project's standing, continuously-maintained assistant service with live crisis-escalation routing.

## MVP Sketch
Build the vetted knowledge base from NNEDV Safety Net's public guidance plus the Prakash et al. paper's documented failure cases, implement a simple keyword/classifier-based crisis-escalation trigger, and benchmark against the paper's own four-axis rubric on a held-out 20-30 question test set, with a partner DV advocacy org reviewing results. 3-4 weeks, 1-2 people plus advocate review time.

## Risks & Open Questions
- Chayn's "Little Window" being taken down after a 3-year pilot over safety/sustainability concerns is a direct, recent cautionary precedent — this needs a concrete sustainability plan (funding, maintenance ownership) before launch, not just a successful pilot.
- A crisis-escalation trigger that's too conservative floods a human hotline with false positives; too permissive and it misses a genuine emergency — thresholds need real pilot tuning, not a guess.
- Strongest reason this might already be solved: the two IPV-specific models Prakash et al. cite could already cover this if independently vetted — worth direct outreach to their maintainers before assuming greenfield.
- Generic "safety-vetted assistant" framing risks survivors over-trusting it in a genuine emergency; the design must make the human-handoff path unmissable, not buried behind a chat interface.
