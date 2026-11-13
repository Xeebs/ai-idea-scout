# SeatPool: A Shared-License Broker Giving Micro-Nonprofits Single-Seat Access to 5-Seat-Minimum AI Tiers

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Applied AI for underserved domains
- **Source**: research/2026-11-12-applied-ai-for-underserved-domains.md · P5
- **Maturity verdict**: OPEN — WebSearch for sliding-scale or single-seat-friendly AI pricing for solo nonprofits came up empty; every source found (nonprofit AI buyer guides, Clio's legal-AI pricing page, nonprofit-tools landscape pages) describes only fixed per-seat tiers with 5-seat-type minimums or blanket free/discounted tiers, never a pooling or sliding-scale mechanism. No product, repo, or pilot addressing this as a packaging problem was found.
- **Format**: PROJECT
- **Data Sources**: MANUAL — each participating nonprofit submits (pastes/uploads) its IRS 501(c)(3) determination letter or EIN for eligibility verification, plus its intended use case and expected monthly usage, to join a pool; no vendor today exposes a public API for third-party seat resale or provisioning, so the broker manually manages logins within the pooled vendor account at MVP stage. A CONNECTED upgrade is plausible if a vendor's enterprise team-management API (e.g. Google Workspace Admin SDK, which is mature, or a future Anthropic/OpenAI enterprise seat API) were opened to third-party brokers — flagged in Risks below as the real unlock if it happens.

## The Gap
A nonprofit-AI buyer's guide found via WebSearch reports Claude's nonprofit program gives 75% off but carries a "minimum five seats" requirement, framed directly against a 2-person org ("Your org has two people who'd use it"); ChatGPT Team's discounted tier carries the same five-seat minimum. A separate source frames the resulting workaround as "digital duct tape" — staff pushed onto patchwork cheap tools lacking automation/integration because enterprise platforms are "entirely inaccessible" for organizations under 200 employees. The gap is structural (vendor seat-minimum policy), not technical, and the two sources independently converge on the same complaint.

## The Project
A broker that buys 5-seat (or larger) nonprofit-discounted licenses in bulk from AI vendors and resells individual seats, at a sliding scale tied to org size/budget, to the solo and 2-3-person nonprofits those minimums structurally exclude. The broker handles the admin burden a tiny org can't absorb alone: eligibility verification, billing consolidation, seat provisioning/deprovisioning as member orgs join or leave a pooled license, and usage isolation so one org's activity doesn't leak into another's workspace. The centerpiece is the pooling-and-resale mechanism itself — a legal/billing/provisioning layer that makes a vendor's 5-seat minimum functionally invisible to a 1-person org, rather than another tool that assumes the minimum away.

## Tangible Impact
**Population**: Micro-nonprofits (1-3 staff) serving underserved populations who are explicitly named as excluded by current nonprofit AI pricing tiers — a nonprofit-AI buyer's guide cites the National Council of Nonprofits' estimate that the majority of the US's ~1.5 million registered 501(c)(3)s operate with very small staffs, and the sources in this digest single out organizations under 200 employees as effectively locked out of current enterprise-nonprofit discount structures.
**Mechanism**: Today a 2-person nonprofit either pays full retail for a single seat, overpays by buying 5 seats it doesn't need just to unlock the discount, or falls back to "digital duct tape" — fragmented free tools lacking integration, per the cited source. A pooling broker lets that same org buy exactly one discounted seat at a price scaled to its budget, without needing four strangers to share a license with or a grant to cover five seats.
**Measure**: (1) effective per-seat price paid by a pooled-member org vs. the vendor's standalone single-seat retail price; (2) number of 1-3-person orgs successfully onboarded and retained in a pool after 6 months; (3) admin hours saved per member org vs. the org independently negotiating/managing its own license and billing.

## Why Now
Multiple vendors' nonprofit discount programs (Claude, ChatGPT Team, Microsoft 365 Copilot) are all live right now with the same seat-minimum structure, and the SSIR/Ask-HN-adjacent complaints about this gap landed in the last 30 days as explicit, named articulations — the vendor policies themselves aren't changing, which is exactly the condition under which a broker sitting between the vendor and the smallest orgs becomes valuable rather than a stopgap waiting to be obsoleted.

## MVP Sketch
Partner with 5-8 real micro-nonprofits to form one pooled license under a single vendor's nonprofit-discount tier (pick whichever vendor's terms permit sub-licensing or shared seat management without violating its terms of service — this needs a direct check before building anything). Stack: a lightweight admin dashboard (Postgres + a simple web app) for eligibility docs, billing splits, and seat assignment; manual onboarding/offboarding at this scale. The validating experiment: run one real pooled license for 90 days, track whether every member org's usage stays isolated and billing stays accurate, and measure retention and effective price paid.

## Risks & Open Questions
- Vendor terms of service may explicitly prohibit sub-licensing or seat resale — this is the single biggest existential risk and needs a direct legal read of each target vendor's nonprofit-tier terms before any pilot, not after.
- A vendor could view a pooling broker as an invitation to simply remove the seat minimum rather than tolerate resale, which would collapse the broker's value proposition — worth treating as a plausible best-case outcome, not a threat.
- Liability/billing risk if a member org defaults or misuses shared access under a license the broker's name is on, not theirs.
- Strongest reason this might already be solved: a fiscal-sponsorship or shared-services nonprofit (TechSoup-adjacent) could already informally broker shared software licenses for member orgs — worth direct outreach before building a dedicated platform.
