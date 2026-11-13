# OpenFurrow: A Fully Open-Stack Crop-Advisory Assistant for Smallholder Farmers

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Applied AI for underserved domains
- **Source**: research/2026-11-12-applied-ai-for-underserved-domains.md · P4
- **Maturity verdict**: PARTIAL — real but incomplete attempts exist (AgroTutor, a WUR local-inference stack, a hackathon-grade offline advisor) but every low-bandwidth success story found (Ulangizi AI on Azure, Rwanda rice-advisory on Gemini, VIONEX on Gemini) still depends on a proprietary cloud model; no fully open end-to-end (model + data + hosting) stack was found.
- **Format**: BOTH
- **Data Sources**: CONNECTED — the agronomic knowledge base is built once from openly-licensed sources (CGIAR/CIMMYT crop-advisory corpora, FAO's open GIEWS data) rather than pasted per query; live localization pulls from NASA POWER or Open-Meteo (both free, mature, keyless or low-friction APIs) for rainfall/temperature data by coordinates; the farmer-facing channel runs over Meta's WhatsApp Business Cloud API (mature, widely integrated already by Ulangizi and others). No step requires a farmer or org to manually paste agronomic reference material.

## The Gap
SciDev.Net reports that subscription-priced AI tools are pricing smallholders out while "farmer-led, open-source, and ecological innovations... are sidelined" in favor of big-tech products. The digest's own clearest low-bandwidth success story, Opportunity International's Ulangizi AI (a WhatsApp chatbot usable without broadband), still runs on Microsoft Azure — solving connectivity but not openness. The AIEP Initiative's arXiv paper explicitly calls for shared corpora and benchmarks as still-needed infrastructure, and GitHub/web search confirmed no project combines open model + open data + self-hosted/cooperative hosting end to end.

## The Project
A self-hostable crop-advisory stack that a farmer cooperative, agricultural extension office, or regional NGO can run without a per-query bill to a US cloud vendor: an open-weight model (Gemma/Llama-class, quantized) fine-tuned or RAG-grounded on openly-licensed agronomic corpora (CGIAR/CIMMYT, FAO), served from commodity hardware the org controls (a local VM, a shared regional server, or a co-op-funded box), with farmer interaction over WhatsApp/SMS rather than a dedicated app. The centerpiece is the open-stack packaging itself — a reproducible deploy recipe (model weights, RAG corpus, hosting config) any org can stand up and audit, replacing the current pattern of bolting a chat UI onto whichever proprietary API happened to be easiest to wire up.

## Tangible Impact
**Population**: Smallholder farmer cooperatives and the extension/NGO organizations serving them in regions where per-query cloud AI pricing is a real adoption barrier — FAO estimates roughly 500 million smallholder farms worldwide; the near-term beneficiaries are the extension orgs (like those running Ulangizi-style pilots) who want the low-bandwidth WhatsApp pattern without recurring per-token exposure to a vendor whose pricing or terms they can't control.
**Mechanism**: Today an org adopting a "low-bandwidth" farm-advisory bot still inherits a proprietary cloud dependency — unpredictable per-query cost, data-residency exposure, and vendor lock-in that SciDev.Net's sources flag as actively sidelining farmer-led alternatives. A fully open, self-hostable stack removes the recurring API bill and the dependency, letting an org budget a one-time hosting cost instead of a usage-scaled one and keep farmer query data in-region.
**Measure**: (1) per-query marginal cost of the open-stack deployment vs. a comparable Azure/Gemini-backed deployment, measured over 90 days of real traffic; (2) advisory-answer quality (agronomist-rated accuracy on a held-out question set) vs. the proprietary-API-backed comparators (Ulangizi-style); (3) number of independent orgs successfully standing up their own instance from the published deploy recipe within a year.

## Why Now
Open-weight models in the 2-8B range now run acceptable-latency RAG-grounded inference on commodity hardware a regional NGO can actually afford to host, and WhatsApp Business Cloud API access is mature and already proven at Ulangizi's scale — the only missing piece per the digest's own search is someone assembling the open-model + open-corpus + self-hosted pieces into one reproducible stack instead of defaulting to the nearest proprietary API, which is an assembly problem, not a capability gap.

## Skill Angle
A Claude Code skill version: given a description of an org's current farm-advisory chatbot architecture (which model/API it calls, how farmer messages arrive, where data is stored), the skill audits it against an "open-stack checklist" — flagging specific proprietary dependencies (a locked model API, a vendor-hosted database) and recommending the matching open-source swap from this project's deploy recipe. This is the one-time architecture-review task an org runs before migrating; the project is the actual running self-hosted stack the audit points them toward.

## MVP Sketch
Scope to one crop domain (e.g., maize or cassava, where CGIAR corpora are richest) and one region/language pair. Stack: a quantized Gemma 3B/8B served via vLLM or Ollama on a single rented or co-op-owned GPU box, a RAG index over the CGIAR/FAO corpus, Open-Meteo for weather context, and WhatsApp Business Cloud API for the farmer channel. The validating experiment: run the same 50 real farmer questions (sourced from a partner extension org) through this stack and through a reference Gemini/Azure-backed bot, and compare answer quality and per-query cost side by side.

## Risks & Open Questions
- Open-weight models may lag proprietary frontier models on nuanced agronomic reasoning for ambiguous cases — the MVP's quality comparison needs to be honest about where the open stack loses, not just cost-optimistic.
- Hosting cost and maintenance burden shift from "pay-per-query to a vendor" to "an org now owns a server" — this only wins if the target orgs have (or can pool for) the technical capacity to run it, which needs validating with a real partner before building further.
- CGIAR/FAO corpora may have regional gaps for some crops/geographies, requiring supplementary data-collection work that could dominate project timelines.
- Strongest reason this might already be solved: a CGIAR-affiliated or Digital Green-adjacent team could have an unpublished internal open-stack build — worth direct outreach before assuming greenfield.
