# ScaleKit: Pilot-to-Scale Deployment Tooling for Frontline-Health WhatsApp/Telegram Bots

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Applied AI for underserved domains
- **Source**: research/2026-11-12-applied-ai-for-underserved-domains.md · P3
- **Maturity verdict**: PARTIAL — ASHABot (CHI 2025/MSR, arXiv 2409.10913) completed a real two-month field deployment, and Turn.io's "Chat for Health Accelerator 2026" (Anthropic-backed) is explicitly funding reusable open-source scaling assets, but the accelerator has no shipped output yet and ASHABot remains a research pilot, not deployment-integration tooling — the pilot-to-scale gap is real and still open.
- **Format**: PROJECT

## The Gap
A February 2026 ICTworks piece puts a number on the problem: only 34% of CHW-facing AI chat initiatives show any sign of scaling beyond pilot phase, and a separate survey found 61% of health systems are "piloting" such tools but only one reports "meaningful integration" nationally. The digest shows the chatbot technique itself (ASHABot, Aarogya Saathi, Dimagi's Open Chat Studio) is proven — the gap is specifically the unglamorous integration layer: multi-tenant deployment, offline-tolerant message queuing, human-escalation routing, and monitoring-and-evaluation reporting that turns a working pilot into something a health ministry can run at scale.

## The Project
An open-source deployment and operations layer purpose-built for CHW-facing WhatsApp/Telegram health bots, sitting between an org's existing chatbot logic (built on whatever LLM/platform they chose) and the messaging API. It provides: a queue-and-retry layer that tolerates intermittent connectivity on the CHW's end without dropping messages, a structured human-escalation workflow (routes a flagged conversation to a supervisor's dashboard instead of silently failing or looping), a built-in M&E event log mapped to the metrics health ministries actually report on (message volume, escalation rate, response latency, language mix), and a multi-tenant config system so one NGO running bots across several districts or languages doesn't redeploy a bespoke stack per site. It deliberately does not try to be a new chatbot framework — it is the scaling plumbing every pilot currently reinvents badly or skips.

## Tangible Impact
**Population**: CHW programs and the patients/communities they serve across the health systems the ICTworks/newsletter data describes as currently stuck in pilot — a conservative estimate from the WHO's ~3 million-strong global CHW workforce suggests tens of thousands of CHWs are actively using or piloting a messaging-based AI support tool today, per the volume of named pilots (ASHABot in India, Aarogya Saathi, Turn.io's accelerator cohort) in just this one digest cycle.
**Mechanism**: A program that stalls at pilot because of connectivity drops, no escalation path, and no reportable M&E data never reaches the CHWs or patients outside the original pilot district. Reusable scaling plumbing removes the specific integration blockers the ICTworks piece names, letting a validated pilot bot extend to additional districts without a full re-engineering cycle each time.
**Measure**: (1) percentage of pilot deployments using the toolkit that are still active and expanding (not just surviving) at 12 months, benchmarked against the 34% baseline; (2) median message-delivery success rate under intermittent connectivity vs. a non-queued baseline; (3) time for an org to add a second district/language deployment using the multi-tenant config vs. their prior from-scratch integration time.

## Why Now
Turn.io's Anthropic-backed "Chat for Health Accelerator" launching cohort applications in 2026 signals that well-resourced players have just identified this exact gap as fundable and urgent, but their output won't ship for months — there's a live window to build the open, vendor-neutral version before a single accelerator's proprietary toolkit becomes the de facto (and possibly closed) standard.

## MVP Sketch
Scope to the two highest-value pieces first: the offline-tolerant message queue/retry layer and the human-escalation dashboard, built as a thin middleware that wraps the WhatsApp Business API/Telegram Bot API and sits in front of any existing chatbot backend (Dimagi's Open Chat Studio, a custom LLM, or a rules engine). Stack: a message broker (Redis/SQS-equivalent) for queuing, a small web dashboard for escalations, Postgres for the M&E event log. The validating experiment: integrate the middleware in front of one existing open chatbot (e.g., recreate a minimal ASHABot-style flow) and measure message-delivery success and escalation-routing latency under a simulated intermittent-connectivity test versus running the same bot without the middleware.

## Risks & Open Questions
- Turn.io's accelerator may ship exactly this as an open asset within the next 1-2 cycles, which would make an independent build redundant — worth monitoring their output before heavy investment.
- Health-ministry integration requirements vary enormously by country (data residency, reporting formats); a generic toolkit risks being too generic to actually satisfy any one ministry's procurement bar.
- Risk that Dimagi's Open Chat Studio or CommCare already has an unpublicized scaling layer that covers this — worth a direct technical evaluation of Open Chat Studio before building a parallel layer.
- The underlying problem may be organizational (funding cliffs after pilot phase, not technical) rather than something software can fix — worth validating with 2-3 real program operators before committing to the build.
