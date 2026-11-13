# Who's Reading My Page: Attribution Fingerprinting for Agents That Obey Hidden Instructions

- **Status**: PROPOSED
- **Date**: 2026-11-13
- **Topic**: Multi-agent architectures
- **Source**: research/2026-11-13-multi-agent-architectures-ii.md · P6
- **Maturity verdict**: PARTIAL — mature general-purpose prompt-injection detection tooling exists (Arize, Promptfoo, the open-source Agent Security Scanner, Google scanning billions of pages/month) plus one narrow write-up (itnext.io) on reverse-prompt-injection honeypots to fingerprint which agent responds, but no maintained tool attributes a specific agent/operator identity once the agent actively disguises itself — the attribution-specific slice of the gap remains real; closest prior art is a single blog technique.
- **Format**: PROJECT
- **Data Sources**: CONNECTED — reads the site's own request/access logs (standard web server logs, or Cloudflare/Vercel-style edge logs) and serves honeypot content directly from the site's own stack. Log ingestion itself is mature/standard; the cross-session attribution/correlation layer is the new piece this idea builds.

## The Gap
A Reddit r/AI_Agents follow-up post ("AI agents keep obeying the hidden note on my sites. Not one of them will say who it is," 2026-10-28) describes an AI agent reading a hidden-from-humans instruction on the author's site, obeying it, then returning 61 minutes later from a different address disguised as an iPhone — with no way to tell who runs it or why. Mature detection tools tell a site owner *that* something obeyed a hidden instruction; nothing tells them *who*, especially once the agent disguises its traffic.

## The Project
A deployable honeypot-and-fingerprinting layer site operators install to both detect and attribute agentic traffic that reads and acts on page content, even when that traffic spoofs its user-agent or IP to look human or like a different device. It plants calibrated, invisible-to-human instruction variants across pages — a different logged variant per session/cohort — and correlates downstream behavior (API calls, follow-up visits, purchases, form submissions elsewhere) back to the specific variant served, to infer which agent or operator complied. This is combined with passive behavioral fingerprinting (request-timing patterns, JS-execution signatures, header inconsistencies that distinguish a scripted agent from a genuine mobile browser) to produce a confidence-scored attribution report instead of the current "no one will say who it is."

Components: a honeypot-instruction-variant injector; a passive fingerprinting layer distinguishing scripted/headless clients from genuine browsers; an attribution/report engine correlating a compliance event back to a confidence-scored likely operator or an "unidentified automated agent" verdict, with an exportable incident report.

## Tangible Impact
**Population**: website operators, publishers, and SaaS product teams whose sites are now routinely visited by general-purpose AI browsing/research agents (ChatGPT Atlas, Claude's computer-use/browsing mode, Perplexity Comet, and similar) — a population already large and growing, per Google's own reported scanning of billions of pages a month for injection cited in the gap-analyst's verdict — specifically those who, like the digest's source author, have confirmed their site is a target of hidden-instruction manipulation and currently have no way to identify the responsible party.
**Mechanism**: turning a single anecdotal "something obeyed my hidden note" complaint into a per-session traceable experiment moves an operator from "an unknown agent did something" to "operator X's agent complied with variant 3, at Y% confidence" — enabling an abuse report, a targeted fingerprint block, or an evidence-based content-strategy change instead of guesswork.
**Measure**: % of controlled test agents (run against known, labeled agent clients during validation) correctly attributed to the right operator at a stated confidence level; false-positive rate on real human visitors incorrectly flagged as automated agents; time from a compliance event firing to an attribution report being available.

## Why Now
Agentic browsing went mainstream through 2026 (ChatGPT Atlas, Claude computer-use/browsing, Perplexity Comet all shipping agents that read and act on page content autonomously) — exactly what makes hidden-instruction planting a newly live manipulation surface, and exactly why no attribution tool has caught up. The underlying fingerprinting techniques (timing analysis, header-inconsistency detection) are mature and require no new model capability.

## MVP Sketch
Build a small server-side/JS snippet serving 3–5 rotating honeypot instruction variants, log session fingerprints, and manually test it against 3–5 known AI browsing agents (ChatGPT Atlas, Claude computer-use, Perplexity Comet, a deliberately disguised Playwright-scripted client) run under the team's own control to see whether variant-correlation actually distinguishes them, before widening to detecting unknown traffic in the wild. Stack: a lightweight server-side middleware (Node/Express or similar), a simple fingerprint-logging store, a rules-based (not ML, to start) correlation scorer. Single experiment: can the harness correctly attribute each of the 3–5 known test agents to itself, including the deliberately disguised one, at better than chance confidence?

## Risks & Open Questions
- Fingerprinting techniques here overlap with anti-bot/ad-fraud tooling privacy advocates already criticize; needs a clear scope boundary (attributing agentic compliance with planted instructions, not general visitor tracking) to avoid becoming a surveillance tool.
- Sophisticated disguised agents may rotate fingerprints as fast as the honeypot rotates variants, making correlation an arms race — the MVP experiment above is the direct test of whether this holds up at all.
- The original Reddit thread was removed; the strongest evidence is a follow-up referencing a now-deleted post, worth independently re-verifying before building further.
- Legitimate automated clients (accessibility tools, screen readers using AI, legitimate crawlers) could be false-positived as disguised agents, making the tool actively harmful to accessibility if not carefully tuned.
