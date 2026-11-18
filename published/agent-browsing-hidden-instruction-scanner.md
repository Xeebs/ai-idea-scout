# Reader Shield: A Drop-In Scanner for Hidden AI-Directed Instructions in Agent-Browsed Content

A company's own help page told a reading AI not to recommend a regulator. Nobody noticed until a Hacker News thread blew past 744 points and 222 comments — the single highest-engagement item in this entire 30-day research run. The page wasn't hacked. It was written that way, on purpose, for an audience of one: whichever AI agent happened to read it on a user's behalf. There is still no maintained, widely-adopted tool that catches this before it reaches an agent's context — just a scattered handful of single-author scanners nobody has converged on.

## The Gap

The incident — "WhatsApp's help pages hid LLM instructions: dont recommend a regulator," posted 2026-10-19 — is the kind of story that should have a boring, obvious fix already shipped somewhere. It doesn't. A genuine multi-channel search (GitHub, web, Google's own research) turned up InjectScan, Palisade Scanner, Trap Scout, a pip package called "Injection Detection," a Chrome extension (InjectGuard), an Apify actor, and a brand-new repo (`Vick606/subcanopy-guard`, posted days before this writeup, claiming 86.5% on AgentDojo v1) — every one of them narrow, single-author, unverified, or too new to have earned real adoption. Google separately disclosed a billion-page crawl for indirect injection content, confirming the attack surface is large and already being exploited at scale. The tooling to defend against it, by contrast, is still a pile of one-off hacks.

## The Project

Reader Shield is content-ingestion middleware that sits between an agent's web-fetch tool and the agent's context window — the choke point every one of the existing point-tools skips past. Before fetched HTML ever reaches the model, it's rendered through a real DOM (not just regex'd against raw markup, which misses CSS-based hiding entirely) and scanned across the known hiding techniques in one pass: `display:none`/`visibility:hidden`, off-screen positioning, zero-size or zero-opacity text, invisible and zero-width Unicode characters, imperative language stuffed into HTML comments, and alt-text/metadata abuse. Anything that matches gets flagged, stripped, or down-weighted with a trust tag before the agent ever sees it.

The differentiator isn't a new detection trick — it's breadth and maintenance. Every existing tool covers one or two of these techniques; none covers all of them with a benchmarked detection rate a team can point to and trust. The hard part, and the part that actually matters, is the classifier sitting underneath the extractor: telling an *accessibility* `sr-only` label or a cookie-banner `display:none` apart from an instruction written to manipulate the model reading the page. Get that wrong in either direction and the tool is either useless (nothing flagged) or unusable (everything flagged).

## Tangible Impact

**Population**: developers building browsing and computer-use agents that fetch arbitrary third-party pages on a user's behalf — shopping assistants, research agents, and support copilots that read a company's own help or FAQ pages — and, downstream of them, the much larger population of people whose dispute, refund, or complaint gets routed through one of those agents without their ever knowing the page it read was written to steer the outcome. WhatsApp alone disclosed over 3 billion global users; even a sliver of that base funneling a support interaction through an AI agent is a real number of people exposed to exactly this failure mode.

**Mechanism**: right now, the only way this class of attack gets caught is a viral incident report after the fact — as happened here. There is no routine, pre-emptive check running in production agent pipelines today. Wiring a maintained scanner into the fetch step converts "we found out from an HN post with 744 points" into "our pipeline flagged it before a single user was affected."

**Measure**: (1) detection rate on a reproduced benchmark covering the WhatsApp-disclosed technique plus the other known hiding methods, measured against the single-technique coverage of today's fragmented tools; (2) false-positive rate on a large sample of ordinary pages containing legitimate hidden elements, to prove the scanner doesn't break normal browsing; (3) in a pilot deployment, the number of real flagged pages per 10,000 fetches and the manual confirmation rate on those flags.

## Try It

No companion Claude Code skill exists for this idea. It was originally scoped as `Format: BOTH` — a one-shot "paste a suspicious URL, get a hidden-instruction report" skill alongside the always-on middleware — but a later skill-synthesis pass found that exact paste-a-URL audit already shipped elsewhere (`detecting-indirect-prompt-injection` across several skill registries, plus GitHub's `html-hidden-text-check` and `prompt-injection-screen`), so the idea was downgraded to `Format: PROJECT`. The always-on fetch-pipeline middleware — the harder, unaddressed half of the original idea — remains the differentiated project described above.

## The Catch

Two risks matter more than the rest. First, classifying "legitimate hidden accessibility text" versus "AI-directed hidden instruction" takes real judgment, not a presence/absence check — a naive build will over-flag ordinary pages and get disabled by its own users. Second, this is an adversarial cat-and-mouse problem, not a one-time build: an attacker aware of the scanner shifts technique (a new CSS trick, an unexplored Unicode range) faster than a static detector list updates, so the project only stays useful with an ongoing update cadence. There's also a real structural threat to the whole idea: a major browsing-agent vendor — one of the companies whose agents actually triggered this incident — could ship this as a built-in platform feature the moment the attack pattern gets named clearly enough, closing the gap from above before an independent project gets traction.

---

Surfaced from `research/2026-11-14-ai-safety-and-guardrails-in-production.md`, pattern `P5`.
