# Breach Bounty: A Micro-Bounty Red-Teaming Platform for Self-Hosted Guardrails

- **Status**: EXPLORING (promoted 2026-11-13 cycle 39: evidence density — 2 independent, unlinked attempts at the same micro-bounty mechanic)
- **Date**: 2026-11-13
- **Topic**: AI safety & guardrails in production
- **Source**: research/2026-11-13-ai-safety-guardrails-in-production.md · P1
- **Maturity verdict**: PARTIAL — GitHub search found only `meitipro/redline` (0 stars, one-off prompt-injection bounty board). WebSearch surfaced adjacent gamified red-teaming products (Bordair's "Castle" CTF, HackAI, Product Hunt's "Break My Guard") plus enterprise-scale programs (HackerOne/Anthropic $15k, OpenAI $10k-50k, IBM Granite $100k) — none packages reusable, automated micro-bounty tooling (payout automation, payload triage) specifically for self-hosted/solo guardrail builders.
- **Format**: BOTH
- **Data Sources**: CONNECTED — the team's own self-hosted guardrail endpoint (NeMo Guardrails, Guardrails AI, LLM Guard, or a custom webhook) via its existing HTTP API, plus a payment rail for payout (USDC via a smart-contract escrow, or Stripe payment intents) — no single mature connector exists across guardrail products today, so the project ships adapters for the top open-source toolkits as part of the build; the payment rails themselves (Stripe, USDC/Coinbase) are mature today.

## The Gap
A GitHub issue (`ak10082247-max/canaryguard-402#2`, "[BOUNTY] $5.00+ USDC: Adversarial Prompt Injection Bypass on CanaryGuard Firewall," 28 comments) shows a solo builder manually running a prompt-injection bounty as a one-off GitHub issue, with no reusable tooling behind it. Enterprise programs (HackerOne/Anthropic, OpenAI, IBM Granite) pay $15k-$100k but are invite-only, high-overhead, and out of reach for solo/small-team self-hosted guardrail builders — there is a visible gap between those two extremes with no accessible, automated middle tier.

## The Project
A platform where a guardrail builder registers their guardrail endpoint and funds a small bounty pool; red-teamers submit adversarial payloads, the platform auto-runs each submission against the registered endpoint, verifies whether it achieved a bypass (e.g., a "clean"/low-risk verdict on content that should have been flagged), dedupes against prior submissions, and releases payout from escrow once verified — removing the manual triage a GitHub-issue bounty requires today. Components: adapter layer for popular guardrail toolkits, escrow/payout integration, a dedupe/triage engine, and a public per-guardrail leaderboard.

## Tangible Impact
**Population**: solo developers and small teams (2-10 people) self-hosting LLM guardrails on NeMo Guardrails, Guardrails AI, or LLM Guard — not enterprise security teams with $15k-$100k bounty budgets, a distinction the digest's own contrast between the enterprise programs and the $5 CanaryGuard issue makes directly.
**Mechanism**: lowers adversarial-testing cost and overhead from "manually run a GitHub issue bounty and triage each submission by hand" to "register an endpoint, fund a pool, get automatically-verified bypass reports" — surfacing real jailbreak bypasses before an attacker exploits them in production, for teams priced out of HackerOne-tier programs.
**Measure**: genuine verified bypasses found per guardrail-month at a given bounty spend; median time from submission to verified payout (target: minutes to hours, vs. the manual GitHub-issue baseline of days); post-remediation bypass rate on a retest after a found bypass is patched.

## Why Now
Enterprise programs already prove the bounty mechanic works at scale; the CanaryGuard thread shows real demand at the opposite end of the market with zero tooling; stablecoin micropayment rails (USDC) now make sub-$10 automated payouts operationally viable in a way that wasn't practical a few years ago.

## Skill Angle
A "Bypass Triage" skill — given a submitted adversarial payload, the guardrail's verdict on it, and the guardrail's stated detection rules, the skill judges whether the submission is a genuine novel bypass, a duplicate of a known pattern, or a false claim, and drafts the payout/rejection response. This is usable by a manual bounty runner today, before any team builds the full automated platform.

## MVP Sketch
2-4 weeks, 1-2 people. Build one adapter (NeMo Guardrails, the most widely deployed open-source option) exposing a "submit payload, get back verdict" webhook; wire a basic escrow (Stripe payment intents held until verification, automate release later) and a public leaderboard page. Single experiment: run a live $50 bounty pool against one real open-source guardrail deployment for two weeks and measure whether it attracts more verified bypasses than the project's own internal red-team testing found in the same period.

## Risks & Open Questions
- Payout automation on unverified adversarial claims risks gaming (submitters crafting near-duplicate payloads to farm the pool) — needs a dedupe/similarity check against prior submissions.
- Adjacent paid products (Bordair's Castle, HackAI, Break My Guard) could add a per-issue micro-bounty mode and absorb this niche.
- Hosting a platform that pays people to find exploits in third-party guardrails needs clear terms distinguishing it from unauthorized security testing.
- Thin evidence base (one 28-comment GitHub issue) — real validation requires confirming more than one team wants this mechanic, not just one.
