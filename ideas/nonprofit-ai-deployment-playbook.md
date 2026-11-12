# NonprofitStack: A Tested Cost-and-Reliability Playbook for Running AI on Behalf of Underserved Populations

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Applied AI for underserved domains
- **Source**: research/2026-11-12-applied-ai-for-underserved-domains.md · P3
- **Maturity verdict**: PARTIAL — WebSearch found scattered partial answers (localaimaster.com's "Local AI for Nonprofits" guide, Tech to the Rescue's tooling list, a Knowbot deployment-lessons case study) but no single authoritative, tested cost/reliability playbook; each source covers one slice (software cost, hardware cost, or deployment lessons) and none resolves SSIR's flagged problem that free tiers don't hold at scale. Content exists but is fragmented and blog-grade, not validated.
- **Format**: BOTH

## The Gap
An Ask HN thread (item 47499498, a poster working with an African government think tank on funding) asked concretely "what would it take to provide free AI to the underprivileged" and got only scattered, unverified point-answers — AWS nonprofit credits (~$5000/yr, unverified forum claim), Oracle Always Free/Scaleway free tiers explicitly caveated as "not intended for reliable, professional, and/or commercial use," and Hugging Face's free tier + $2/mo PRO. SSIR's "The Low-Cost AI Illusion for Nonprofits" warns that advanced features cluster behind paid tiers so free access collapses exactly when an org scales usage — and no one has published a durable, tested answer.

## The Project
A continuously-updated, independently-measured benchmark and decision tool: actually run representative nonprofit AI workloads (FAQ chatbot, document Q&A/RAG over program materials, basic translation) against the real candidate stacks (AWS nonprofit credits, Oracle Always Free, Scaleway free tier, Hugging Face free/PRO, self-hosted via Ollama on budget hardware) for a sustained period, and publish measured cost-at-scale and reliability — rate limits hit, silent throttling, outages — instead of vendor marketing. Pair it with a lightweight calculator: an org enters expected usage and gets an honest recommended stack with a realistic cost ceiling, not a best-case number.

## Tangible Impact
**Population**: small nonprofits and community organizations deciding whether/how to deploy AI to serve underprivileged clients — the U.S. has roughly 1.5 million registered 501(c)(3) nonprofits (IRS data), most with no dedicated technical staff per National Council of Nonprofits workforce surveys — plus nonprofit-adjacent builders in lower-income countries, like the Ask HN poster working with an African government think tank.
**Mechanism**: replaces guesswork and vendor marketing with measured numbers, so an org picks a stack that survives real usage instead of hitting an undocumented "not intended for reliable/commercial use" wall mid-deployment (the exact "low-cost AI illusion" SSIR describes) and either overpaying in panic or abandoning the project.
**Measure**: (1) share of orgs following the recommended stack that are still running it, unchanged by a forced mid-deployment switch, after 90 days; (2) delta between predicted and actual monthly cost after 3 months of real usage; (3) logged rate-limit/outage incidents per org per month against the playbook's stated expectations.

## Why Now
The Gates Foundation's $1B/2yr equitable-AI commitment (Sept 2026) and active nonprofit cloud-credit programs (AWS, Oracle, Scaleway, Hugging Face) create real options worth benchmarking right now, and SSIR's own Oct/Nov 2026 warning piece plus the unresolved Ask HN thread show the demand is active and currently unmet by any durable published answer.

## Skill Angle
Trigger: a nonprofit ops person or technical volunteer is about to choose an AI stack and hands over expected usage (users/month, query types, budget ceiling, data sensitivity). The skill queries the maintained benchmark dataset and produces a written recommendation — stack choice, realistic monthly cost range, specific reliability caveats to expect, and a fallback plan — as a one-shot advisory judgment for that org. This differs from the project, which is the ongoing measured-benchmark infrastructure the skill's recommendations draw from.

## MVP Sketch
Pick 3 representative nonprofit workloads (FAQ chatbot, document Q&A, basic translation), run them for 30 days against AWS nonprofit credits + Oracle free tier + self-hosted Ollama on a ~$200 mini PC, log cost/throttling/outages publicly (a static site or spreadsheet), and ship a one-page calculator referencing the logged numbers. 2-4 weeks, 1-2 people.

## Risks & Open Questions
- Free-tier terms change unpredictably — the dataset needs a refresh cadence or it goes stale fast, mirroring the exact problem it's trying to solve.
- Three self-selected workloads may not generalize to every nonprofit's actual usage pattern.
- Publicizing providers' free-tier limits/throttling behavior is unlikely to violate any ToS but is worth a quick legal skim before publishing specifics.
- Strongest reason this might already be solved: a well-funded nonprofit-tech org (TechSoup, Tech to the Rescue) could be running something like this internally without publishing it — the gap-analyst's search found only fragmented blog-grade answers, not this, but worth a direct check before building.
