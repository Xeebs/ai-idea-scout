# Scraper Shield: An Adaptive, Circumvention-Resistant Bot Defense for Public and University Libraries

A university library's catalog goes down. Not from a cyberattack in the dramatic sense — just from the ordinary, relentless weight of AI scraper bots hitting every searchable page, over and over, until the servers buckle. The librarians running that site are, more often than not, a team of one or two people. They deployed the best open-source defense available. It worked for a while. Then the bots learned to get past it, and they're back to square one — except this time the outage is the headline.

## The Gap

This is a live, named crisis, not a hypothetical one. A Hacker News discussion of a CBC story — "University libraries are being swarmed by AI bots, putting public access at risk" — pulled 137 points and 61 comments, well past the engagement bar this pipeline uses to flag a gap as urgent rather than merely interesting. The institutions named aren't abstractions: Marmot, a small multi-library consortium, is reporting over 2 billion monthly bot hits; UNC Chapel Hill built its own AI-based firewall in response; UDSpace has been fighting the same fire.

The frustrating part is that real mitigations already exist. Anubis, the MIT-licensed proof-of-work reverse proxy, has been running at Duke University Libraries since mid-2025 and is used by OAPEN and DOAB too. Cloudflare has AI Labyrinth and enterprise bot management. These aren't vaporware. But Codeberg reported in August 2025 that many AI scraper bots had already learned to solve Anubis's proof-of-work challenge — and the coverage from CBC, cybernews.com, 404media.co, and American Libraries Magazine all show outages and multi-billion-hit months still happening as of November 2026, despite these defenses being in place. The honest read of the evidence is: PARTIAL, not SATURATED. The tools that exist are being outpaced, and the people maintaining the fallback are exactly the people with the least slack to fight an arms race — one- or two-person library IT teams, not CDN-backed enterprises.

## The Project

The idea isn't to replace Anubis or Cloudflare — it's to build on top of what's already deployed and treat bot defense as the ongoing arms race it demonstrably is, rather than a one-time install.

Three pieces make up the core loop. First, behavioral fingerprinting layered on top of the existing proof-of-work challenge — request timing regularity, header and entropy patterns, JS-execution fidelity — specifically aimed at catching the bots that have already learned to solve the static Anubis challenge, since that's the documented failure mode. Second, a shared, cross-institution threat-intelligence feed: because library IT teams are small and isolated, every library currently has to independently rediscover the same bypass pattern on its own. Pooling what's observed across institutions means Marmot's lesson helps UDSpace without UDSpace having to get hit first. Third, a tunable "degrade gracefully" mode, because the single biggest risk in tightening any bot defense is accidentally blocking the legitimate low-bandwidth or screen-reader patron who has no other way to reach the library's resources — which would mean the defense itself became the access barrier the project exists to prevent.

## Tangible Impact

**Population**: patrons who rely on public and university libraries as a primary or only point of free internet/digital-resource access — roughly 2.5 million Americans without home broadband use public library terminals as their main connection (per Pew/FCC-adjacent library-usage surveys; libraries remain a key digital-equity access point per ALA's own reporting) — plus students at under-resourced universities whose library IT teams, like Marmot's small multi-library consortium named in the coverage, lack the budget of a large CDN-backed institution.

**Mechanism**: as bot traffic degrades library site/catalog availability, the patrons hit hardest are the ones with no alternative — someone with home broadband just switches services; someone relying solely on the library doesn't. A defense that actually holds against circumvention, instead of repeating the current Anubis-bypass arms race, keeps that access reliable, and the graceful-degradation mode specifically prevents the defense itself from becoming a new accessibility barrier.

**Measure**: (1) legitimate-patron page-load success rate and latency during active bot-swarm periods, before vs. after deployment; (2) bot-traffic volume successfully blocked/throttled against baseline, targeting a measurable cut into the "2B+ monthly hits" figure reported at Marmot; (3) false-positive rate against known assistive-technology/screen-reader traffic patterns.

## Try It

A companion skill exists at [`skills/public-library-ai-scraper-defense-shield/`](../skills/public-library-ai-scraper-defense-shield/):

> "Audits a library or small institution's exposure to AI scraper-bot traffic and produces a prioritized, effort-ranked defense plan, grounded in documented circumvention patterns (e.g. the Anubis proof-of-work bypass). Use when a one- or two-person library/archive IT team needs to assess current posture and decide what to add next, not when they need a running defense system itself."

This is deliberately scoped as a triage memo, not a deploy-this-code tool — the posture audit a resource-strapped team can act on today, separate from the maintained defense software and shared threat feed the full project would build. To use it: paste the contents of `skills/public-library-ai-scraper-defense-shield/README.md` into any AI chat tool along with a description of your current stack and any log samples or outage symptoms, or drop the whole `skills/public-library-ai-scraper-defense-shield/` folder into `~/.claude/skills/` if you're working in Claude Code.

One caveat worth stating plainly, carried straight from the idea's own risk assessment: Cloudflare's AI Labyrinth and other enterprise bot-management products already do sophisticated behavioral detection. If those are affordable and accessible to small libraries — unclear, and worth checking their nonprofit/library pricing before building anything from scratch — a from-scratch open alternative may be solving a cost problem, not a capability problem. The arms-race framing also means no specific technique added here is a permanent fix; the real differentiator has to be the update cadence and the shared threat-intel model, not a one-time clever trick, or this just repeats Anubis's own trajectory.

---

Surfaced from `research/2026-11-12-applied-ai-for-underserved-domains.md`, pattern `P8`.
