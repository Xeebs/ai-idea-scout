# Commons Line: A Shared, White-Labelable Resource-Navigation Platform for Refugee and Immigrant Casework Orgs

- **Status**: PROPOSED
- **Date**: 2026-11-13
- **Topic**: Applied AI for underserved domains
- **Source**: research/2026-11-13-applied-ai-underserved-domains-5th.md · P8
- **Maturity verdict**: PARTIAL — at least eight independently-built, overlapping tools surfaced (HeyFriend Helper, Harvard's digital-literacy program, USCRI's Multilingual Resource Finder, Omdena's helpline bot, SiBot, IRC's ALMA, University of Waterloo's Newcomer App, Clear Global/IOM's Planeta Azul), none sharing a codebase, dataset, or maintenance commitment. SiBot's announced white-label plan for other charities/councils is the nearest precedent toward a shared model but is itself new, narrow, and single-vendor.
- **Format**: PROJECT
- **Data Sources**: MANUAL — each participating nonprofit uploads its own existing resource directory (spreadsheet, document, or scraped webpage) to seed the shared knowledge base, since no single live API covers refugee/immigrant services comprehensively across regions and languages. 211.org's regional APIs (mature in some US regions) are a viable partial CONNECTED upgrade path for US-based partners.

## The Gap

Four to eight separate teams — two academic labs, two nonprofit/hackathon-adjacent projects, and several standalone platform vendors — built functionally similar multilingual resource-navigation chatbots for substantially overlapping refugee and immigrant populations in the same period, each maintained independently with none sharing infrastructure, content, or upkeep commitment. HeyFriend Helper's own literature review names conversational AI as a promising "informational intermediary" for this population, but only as prior-work framing — not as an existing shared product any of these teams actually built together.

## The Project

A multi-tenant resource-navigation platform that any refugee-serving or immigrant-serving organization can adopt and white-label (own branding, own number/channel) instead of building its own chatbot from scratch. Each participating org seeds the shared knowledge base with its own curated resource list (housing, legal aid, benefits, English classes, job programs) in whatever languages it already serves; the platform handles the multilingual conversational layer, intent routing, and content-freshness tooling (flagging resources not reconfirmed in N months) centrally, so no single small org bears that engineering cost alone. Orgs can see — and optionally pool — resource content covering the same city/region contributed by other participating orgs, turning today's duplicated effort into shared coverage.

## Tangible Impact

**Population**: Staff and volunteers at small refugee- and immigrant-serving nonprofits (the USCRI affiliate network, local resettlement agencies, university-adjacent programs like HeyFriend Helper's Chicago deployment) who currently each build or commission a narrow, single-org chatbot — and by extension the refugee and immigrant clients those orgs serve, who today get inconsistent coverage depending on which single org's bespoke tool they happen to find.

**Mechanism**: Pooling the conversational-AI and content-freshness engineering into one shared platform lets a small org (which couldn't otherwise afford or maintain its own chatbot) offer the same navigation quality as a well-funded lab project, and lets clients get consistent, cross-org resource coverage in their region instead of whatever one org's narrow directory happened to include.

**Measure**: (1) number of participating orgs onboarded and actively maintaining resource content after 6 months (adoption and retention, not just signup); (2) resource-content freshness rate (% of entries reconfirmed within the staleness window) compared to typical single-org chatbot upkeep; (3) client-reported successful resolution rate for a navigation query, especially for queries spanning more than one participating org's original service area.

## Why Now

SiBot's 2026 move toward an explicit white-label offering is the first concrete market signal that resource-navigation orgs themselves recognize the shared-platform model as viable, after years of each building solo — timing a pooled, more deliberately multi-tenant and open version to launch into that same recognized need rather than ahead of any demand signal.

## MVP Sketch

Partner with 3-4 small nonprofits serving overlapping or adjacent regions (not large, already-resourced orgs like IRC or USCRI, which have their own tooling) to seed a shared knowledge base and multilingual chat interface each can white-label behind their own branding. Stack: a multi-tenant content-management layer, an LLM-based multilingual intent/retrieval layer over the pooled resource content, and a staleness-flagging dashboard. Single experiment: measure whether query resolution rate and content coverage for the pilot region improves over each org's prior solo tool (or lack of one) within the first 2-3 months.

## Risks & Open Questions

- Small nonprofits are often protective of "their" client relationships and resource lists; pooling content requires a genuine trust and governance model (who can edit what, how disputes over accuracy get resolved), not just shared software.
- SiBot or another well-positioned vendor could move into exactly this white-label-commons space faster than an independent new entrant, given they already have working multilingual infrastructure and a stated roadmap toward it.
- Resource-content accuracy liability (sending someone to a shelter that's actually full, or legal-aid info that's outdated) is a real harm risk in this domain; the staleness-flagging mechanism needs to be a hard requirement, not a nice-to-have, before any multi-org launch.
- It's possible some of the eight tools found are already quietly discussing consolidation that wasn't visible in the search results — worth a direct outreach check to HeyFriend Helper's and SiBot's teams before committing to build a competing shared platform from zero.
