---
name: public-library-ai-scraper-defense-shield
description: Audits a library or small institution's exposure to AI scraper-bot traffic and produces a prioritized, effort-ranked defense plan, grounded in documented circumvention patterns (e.g. the Anubis proof-of-work bypass). Use when a one- or two-person library/archive IT team needs to assess current posture and decide what to add next, not when they need a running defense system itself.
---

# Scraper Shield Posture Audit

## When to use this
A library, archive, museum, or small-institution IT contact (often a team of one or two people) says something like "our site keeps going down from bot traffic," "we're on Anubis/Cloudflare but bots are still getting through," "what should we add to stop AI crawlers," or "can you review our setup against known scraper bypass techniques." Use this skill to turn that moment into a concrete, ordered action plan — not to write or run the defense code itself.

Do not use this skill if the user wants a working bot-blocking proxy or shared threat-intel feed built and deployed; that is separate infrastructure work this skill does not perform.

## Inputs
**Data source**: Manual — the user pastes or describes: (a) their current stack (e.g. "Anubis," "Cloudflare free/business/enterprise," "nothing," "an Apache rule we wrote once"), (b) a sample of recent access logs or a description of symptoms (outage timing, request-rate spikes, specific URLs hit repeatedly), and (c) any incident notes (when outages happened, what they tried). No connector or API integration exists for this today — the user must copy/paste or summarize this themselves.

Minimum viable input: just the stack description and a plain-language account of symptoms. Log samples improve accuracy but are not required — if none are provided, say so explicitly in the output rather than inventing traffic patterns.

## Procedure
1. **Classify current posture.** From the stack description, bucket it into one of: (a) no bot defense, (b) static/simple rules only (e.g. hand-written rate limits, robots.txt reliance), (c) proof-of-work challenge (Anubis or similar) with no added behavioral layer, (d) commercial CDN/bot-management (Cloudflare bot management tier, AI Labyrinth, etc.), (e) layered — PoW plus behavioral or commercial signal already combined.
2. **Check log/symptom evidence against known bypass patterns**, if any samples or symptom descriptions were given. Specifically look for or ask about: challenge-solve success rates recovering after a dip (suggests bots learned to pass a PoW challenge, matching the documented Codeberg Aug-2025 Anubis-bypass pattern); traffic concentrated on expensive-to-render/searchable pages (catalog search, OPAC) rather than static pages; user-agent strings that look legitimate but request patterns that don't match human timing (fixed-interval requests, no referrer chain, no asset fetches); sudden volume spikes correlated with a known crawler's public IP ranges or ASN.
3. **Identify the single biggest gap** given the classification from step 1 — do not recommend everything at once. Priority order, cheapest-and-most-impactful first:
   - No defense at all → recommend deploying Anubis (or a managed equivalent) as the floor, with a note that this alone is already known to be bypassable and should not be treated as a permanent fix.
   - PoW only, no behavioral layer → recommend adding one cheap behavioral signal (request-timing regularity, JS-execution-fidelity check, missing asset-fetch patterns) layered on top of the existing challenge, since this is the documented gap the Codeberg bypass exploited.
   - Static rules only → recommend moving to a maintained proof-of-work tool rather than hand-rolled rules, since hand-rolled rules have no community-maintained bypass-response cadence.
   - Already layered/commercial → recommend checking for and subscribing to a shared cross-institution threat-intel/blocklist feed (if one exists) rather than tuning further alone, since a one-to-two-person team can't out-pace bot authors solo.
4. **Flag the accessibility risk explicitly.** Any recommended change must include a named mitigation for legitimate low-bandwidth, screen-reader, or JS-disabled patrons (e.g. a documented fallback/appeal path, allowlisting known assistive-technology user agents, a "degrade gracefully" mode) — never recommend tightening a defense without pairing it with how legitimate access stays protected.
5. **State effort and cost honestly.** For each recommendation give a rough effort tier (hours / days / weeks) and whether it requires budget (e.g. Cloudflare's paid bot-management tier) versus being free/self-hosted (Anubis). If the user's stack suggests they may already qualify for a nonprofit/library discount on a commercial tool, say to check for it rather than assuming cost is prohibitive.
6. **Do not fabricate specifics.** If no log sample was provided, do not claim "your logs show X" — say "without a log sample, this can't be confirmed; here's what to check for" and name the exact thing to look for.

## Output format
A short memo, in this order:
1. **Current posture** (one line: which bucket from step 1, plus any bypass evidence found/not found in step 2).
2. **Top recommendation** (the single biggest next step, step 3's output) with a one-sentence reason tied to the actual input given.
3. **Secondary recommendations** (up to 2 more, same format, clearly lower priority).
4. **Accessibility safeguard** for each recommendation that touches a visitor-facing challenge.
5. **Effort/cost table**: recommendation | effort tier | budget needed (yes/no, and rough tier if yes).
6. **What to check next** if log evidence was insufficient to confirm a bypass pattern.

Keep the whole memo under one page — this is a triage document for someone with little spare time, not a research report.

## Guardrails
- Never claim a specific bypass is "happening" to this institution without evidence in the pasted logs/symptoms — frame it as "consistent with" or "worth checking for" when inferring from description alone.
- Never recommend a single clever technique as a permanent fix. Always frame bot defense as an ongoing arms race requiring an update cadence, not a one-time deploy — this is the idea's core thesis and the number one way a shallow answer fails this skill's purpose.
- Never recommend tightening a bot challenge without naming the accessibility tradeoff and a specific mitigation for it.
- Never invent specific product pricing, uptime numbers, or named competitor bypass counts that weren't in the input or common public knowledge the user can verify — if unsure, say "verify current pricing/terms directly" rather than stating a number.
- This skill produces an assessment and prioritized plan only. It does not write firewall rules, Anubis config files, or deploy anything — if the user wants implementation code, say that's a separate follow-on task.
