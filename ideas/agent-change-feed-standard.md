# Agent Change Feeds: a diffable, consent-based "RSS for agents"

- **Status**: PROPOSED
- **Date**: 2026-06-10
- **Topic**: Agentic AI & autonomous agents
- **Source**: research/2026-06-10-agentic-ai-autonomous-agents.md · P9
- **Maturity verdict**: PARTIAL — Adjacent standards exist but none is a polling-friendly change feed: AnswerDotAI/llms-txt (2.4k★) is a static site-description file, and Microsoft's NLWeb gives sites conversational endpoints — neither offers the diffable, low-token, permissioned feed of *changing* content the essay calls for. GitHub search for agent-feed implementations otherwise came up empty.
- **Format**: PROJECT — a spec plus a publishing/consuming runtime, not a one-shot prompt task.

## The Gap
HN "Now AI agents need what RSS does" (2026-06-02, 85pts, 65cmt) argues agents need a standardized, structured feed of site changes instead of re-scraping HTML — but it's an essay, not a spec or implementation. Same-window threads on CAPTCHAs still detecting agents (84pts) and Amazon-vs-Perplexity blocking show the current agent-web interface is adversarial, with no cooperative alternative shipped. llms.txt describes a site once, statically; nothing tells an agent *what changed since its last visit* cheaply and with the publisher's consent.

## The Project
A small open spec plus reference implementations: a site publishes `/agent-feed.json` — a cursor-paginated changelog of content mutations (created/updated/deleted, structured payload or pointer, token-count hint, license/permission terms) that agents poll with `?since=<cursor>` and receive only diffs. The novel pattern is the cooperative contract: publishers get a declared, rate-limited, auditable channel that diverts agent traffic away from origin-hammering scrapers; agents get changes at a fraction of the token cost of re-parsing rendered HTML. Centerpiece deliverables: the spec, generator plugins for static-site and CMS ecosystems (Hugo/Astro/WordPress), and a client library exposed as an MCP server so any agent can subscribe today.

## Tangible Impact
**Population**: Operators of small and mid-size content sites bearing AI-crawler load without consent — the Wikimedia Foundation reported a ~50% rise in multimedia bandwidth since January 2024 driven by AI scrapers, and the same pressure falls on the long tail of independent publishers, docs sites, and the hundreds of sites already adopting llms.txt (llms-txt-hub directory, 854★); on the consuming side, builders of monitoring/research agents who currently pay full-page re-scrape token costs per check.
**Mechanism**: A publisher adds one plugin and agents polling the feed fetch a few hundred tokens of structured diff instead of re-crawling whole sections — origin bandwidth and bot-defense friction drop for the publisher, while the agent's per-check inference and scraping cost collapses; the consent terms in the feed replace the CAPTCHA/blocking arms race with a declared contract.
**Measure**: (1) Tokens per content-freshness check on a benchmark of 50 sites drops ≥90% versus HTML re-scrape. (2) Pilot publishers see measurable reduction in AI-crawler origin requests (server logs) within 60 days of publishing a feed. (3) Adoption: ≥100 sites publishing valid feeds and ≥2 independent agent frameworks consuming them within 6 months.

## Why Now
The 85-point essay and the Amazon-vs-Perplexity dispute both landed inside the last 30 days — the adversarial default is becoming legally and economically untenable for both sides. llms.txt's traction proves publishers will adopt a simple convention; MCP's ubiquity means a feed client is instantly usable by every major agent framework. Token-cost pressure (the P4 evidence cluster) makes diff-based access an easy economic sell to agent builders.

## MVP Sketch
A one-page spec (JSON schema + polling semantics), a Hugo/Astro plugin that emits the feed from the content directory's git history, and an MCP server client (`watch_site`, `get_changes_since`). Experiment: instrument one documentation site and one news-ish blog, run a monitoring agent both ways for two weeks, and publish the token/bandwidth comparison — if the diff feed doesn't beat scraping by ~10x on cost, or publishers won't install even a one-line plugin, kill it. 2–3 weeks for 1–2 people.

## Risks & Open Questions
- Chicken-and-egg: feeds are worthless until agents poll them and vice versa; RSS itself is a cautionary tale of a cooperative standard decaying without aggregator economics.
- llms.txt could simply grow a `changes` extension, or Microsoft could fold change feeds into NLWeb — the strongest already-solved path.
- Large publishers may prefer paid licensing deals (per the Amazon/Perplexity fight) over any free cooperative channel, capping adoption at the long tail.
- Sitemaps + `lastmod` + conditional GET already cover a crude version of this; the spec must prove the structured-diff and permission layers add enough over existing plumbing.
- Consent terms in a feed are not enforcement; bad scrapers ignore it, so publisher benefit depends on well-behaved agents being the majority of load.
