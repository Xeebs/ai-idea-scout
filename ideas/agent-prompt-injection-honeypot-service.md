# Tripwire: A Honeypot-as-a-Service for Auditing Which Production AI Agents Follow Hidden Page Instructions

- **Status**: PROPOSED
- **Date**: 2026-11-13
- **Topic**: Agentic AI & autonomous agents
- **Source**: research/2026-11-13-agentic-ai-autonomous-agents.md · P3
- **Maturity verdict**: PARTIAL — promptfoo's mature "indirect-web-pwn" harness (27k stars) tests an agent's own susceptibility before deployment, and a narrow canary-token GitHub repo and a practitioner blog exist, but no packaged, adopted tool catches and attributes production agents that encounter a standing decoy in the wild on a live site — the sourcing Reddit post was an ad hoc one-off experiment, not a reusable service.
- **Format**: BOTH
- **Data Sources**: CONNECTED — the embedded snippet calls back to the project's own new backend telemetry API (built as part of this project, not a third-party connector); optionally correlated with the operator's existing web analytics (e.g. via a standard analytics API) to separate genuine agent check-ins from human/bot noise.

## The Gap
An r/AutoGPT post ("An AI agent hit my site, read a note hidden from humans, and did exactly what it said 61 minutes later") sparked discussion across two subreddits after a decoy instruction planted on a page was followed by a real browsing agent. The gap-analyst confirmed this exact live-site, standing-decoy pattern has only been done as a one-off experiment or in narrow, unverified repos — the mature red-team tooling that exists (promptfoo) tests an agent you control, pre-deployment, not production agents visiting your site in the wild.

## The Project
A hosted service that generates a per-page, invisible-to-humans decoy instruction plus a unique callback code, which an operator embeds on any page they want to monitor. When a browsing/scraping agent reads the page and acts on the hidden instruction, it calls back to the service's telemetry endpoint, which logs the event (page, timestamp, user-agent/IP where available, time-to-callback) and attributes it to that specific decoy variant. The continuous logging and attribution across many pages and over time is the centerpiece — the digest's single 61-minute anecdote becomes the first data point in an ongoing, queryable susceptibility record instead of a story.

Components: a snippet generator producing a unique decoy + callback code per page; a telemetry backend logging check-ins; a dashboard aggregating susceptibility rate and time-to-callback by observed agent signature over time; an optional webhook so operators get alerted the moment a real check-in occurs.

## Tangible Impact
**Population**: Operators of content platforms, marketplaces, forums, and SaaS products that are routinely visited by third-party browsing/scraping AI agents acting on behalf of users (e.g., AI shopping or research assistants), plus AI red-teaming and security research teams who want an ongoing, cross-vendor measure of real-world agent susceptibility rather than a single anecdote — the population that produced the cross-subreddit discussion the digest cites.
**Mechanism**: Today, an operator only learns their site is a prompt-injection target by accident, after the fact, from a single observed incident (as happened here) — a standing, monitored decoy converts that from a one-off anecdote into a continuous signal the operator can act on, deciding whether to harden their content against indirect injection or flag a specific agent vendor's susceptibility with evidence.
**Measure**: (1) Rate of distinct in-the-wild check-in events per 10,000 page views, trended over weeks per pilot site. (2) Mean and distribution of time-to-callback (how long after a page is read the agent acts on the decoy), with the digest's 61-minute example as the first reference point. (3) Operator-reported rate of hardening their own agent-facing features after seeing their site's own susceptibility numbers, measured in a pilot.

## Why Now
Production browsing/computer-use agents (operator-style agents, AI shopping assistants) visiting ordinary websites on users' behalf are now common enough that the exact experiment described in the digest happened organically and generated real community discussion — the population of agents that could trigger a decoy has grown enough in the last 30 days to make a continuous, hosted version of this worth running rather than a one-off test.

## Skill Angle
Given a page's HTML (or a description of its content and framework), generate an invisible-to-humans decoy instruction and unique callback snippet tuned to that page's structure, plus guidance on where to embed it for maximum realism to a browsing agent. This is useful as a one-shot drafting task even for an operator who wants to self-host the logging piece rather than use the hosted service.

## MVP Sketch
A single hosted snippet-generator endpoint, a logging backend, and a simple dashboard; pilot with 3-5 willing site operators embedding the snippet on a handful of pages for two weeks, tracking any real check-ins and validating they correspond to genuine agent traffic (not human curiosity or a misconfigured crawler). 2-3 weeks for 1-2 people.

## Risks & Open Questions
- Legal/ethical framing needs to be explicit: this tests an agent's behavior on the operator's own content, which is closer to an established canary-token security practice than to attacking a third party — but it still needs clear, defensible terms of use.
- False attribution risk: a human curiously viewing page source, a non-agentic crawler following links, or a browser extension could trigger a callback that isn't a genuine agent-injection event, requiring careful signal filtering.
- Vendors could treat detection as adversarial and start sanitizing or ignoring suspicious hidden content, eroding the metric's validity over time — an arms race the service would need to adapt to.
- promptfoo or a similar red-team vendor could extend their existing harness to a hosted, live-site mode, closing this specific gap from an already-dominant incumbent.
