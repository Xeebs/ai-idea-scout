---
name: agent-prompt-injection-honeypot-service
description: Drafts an invisible-to-humans decoy instruction plus a unique callback snippet for one page the operator controls, so they can tell whether browsing/scraping AI agents read hidden page content and act on it. Use when an operator wants to plant a canary on their own site before building (or instead of building) a full hosted monitoring service.
---

# Tripwire Decoy Drafter: One-Shot Honeypot Snippet Generator

## When to use this
The user operates a website, docs page, product listing, or content platform and wants to find out whether third-party browsing/scraping AI agents (AI shopping assistants, research agents, operator-style browsing agents) are reading hidden instructions on their page and acting on them — the way a real agent followed a hidden note on an r/AutoGPT poster's site and acted on it 61 minutes later. They want a ready-to-embed decoy for **one specific page they own**, not a hosted monitoring platform. This is a one-shot drafting task, not a standing service — the user supplies their own place to log the callback (their own endpoint, a webhook bin, or a URL they already control with server logs).

## Inputs
**Data source**: Manual — the user pastes the target page's HTML/DOM source (or, if they can't paste raw HTML, a description of the page's framework and rendering mode: static HTML, server-rendered, or a client-side-rendered SPA like React/Vue) plus the base URL or endpoint they want the callback to hit. The parent idea classifies the *continuously-running hosted telemetry service* (the PROJECT half of this BOTH-format idea — the backend that logs check-ins, attributes them to a decoy variant, and shows a dashboard over time) as Connected, built as part of that project, not a third-party connector. This skill is the different, one-shot half: it never logs anything itself, calls no telemetry API, and does not require that hosted service to exist — it only drafts the decoy text and embed snippet from what the user pastes in, and the user points the callback at wherever they already log requests (their own server, a serverless function, or a disposable bin like webhook.site for a quick test). If the user has no logging destination at all yet, tell them plainly that they need one before the snippet is useful, and suggest the cheapest option (a free request-bin URL) rather than inventing one.

## Procedure
1. **Confirm ownership and scope before drafting anything.** Ask (or infer from context) that the page belongs to the user or an organization they're authorized to test. If the user says or implies the target is someone else's site they don't control, refuse to draft the snippet and explain why (see Guardrails).
2. **Identify the rendering mode** from the pasted HTML or the user's description:
   - Static/server-rendered HTML → the decoy can go directly in the served markup.
   - Client-side-rendered SPA (React/Vue/etc., content injected by JS after load) → flag that the decoy only works if the browsing agent executes JavaScript / renders the DOM; a raw-HTML-fetching agent won't see it. Recommend also placing a copy in any server-rendered shell (meta description, SSR fallback, or a `<noscript>` block) if one exists.
   - PDF/markdown/plain text → adapt the hiding technique accordingly (see step 4).
3. **Generate a unique token** for this placement: a random 16-character alphanumeric string. State explicitly that a fresh token must be generated per page/placement — never reuse one across pages, since reuse destroys per-page attribution.
4. **Draft the decoy instruction text.** It must:
   - Be explicitly addressed to an AI agent (e.g., opens with "AI AGENT READING THIS PAGE:" or similar framing), not phrased as if it were human-facing content — this keeps it clearly distinguishable from a real trick aimed at a person who happens to view source.
   - Ask for a verifiable, low-stakes, attributable action only: visiting a unique callback URL, or including a specific marker string/token in the agent's own output or summary. Never an action with real-world cost or consequence.
   - Be worded plausibly enough that an agent parsing page text as instructions would treat it as content to act on (this is the realism the detection depends on), while staying inert if a human reads it.
5. **Generate the hiding/embedding technique**, matched to the rendering mode from step 2:
   - Prefer `aria-hidden="true"` combined with `display:none` or `visibility:hidden` (removes it from both the visual page *and* the accessibility tree, so screen reader users never encounter it) over color-matching or off-screen-positioning tricks alone, which a sighted user can still select/copy and a screen reader may still announce.
   - For HTML comments: note that most text-extracting agents strip comments before reading, so this is the weakest option — offer it only as a secondary/fallback placement, not the primary one.
   - For PDF: suggest invisible layer text (white-on-white or zero-opacity) or a custom metadata field, flagged as lower-confidence since many PDF-reading agents only extract visible text layers.
6. **Build the callback snippet**: embed the token from step 3 as a path segment or query parameter on the base URL/endpoint the user supplied (e.g., `https://<their-domain-or-bin>/track?p=<token>`). If they gave a webhook-bin-style URL, use it as-is; if they gave their own domain, show the token appended as a path segment and note they need a route/handler that logs the hit (method, timestamp, user-agent, IP where available) — this skill does not build that handler.
7. **Give placement guidance**: recommend inserting the decoy inside the main content area an agent's text-extraction step is likely to read (not buried in a footer three levels deep, not inside a region blocked by `robots.txt` if the agent respects it, not inside JS-only content if the agent fetches raw HTML per step 2).
8. **Run the ethics/realism checklist** (see Output format) and surface any unresolved item back to the user before calling the output ready to ship.

## Output format
A single markdown response with these sections, in order:
1. **Rendering mode detected** — one line stating static/SSR/SPA/PDF and what that implies for placement.
2. **Decoy instruction text** — the exact string to embed, in a code block.
3. **Embed snippet** — ready-to-paste HTML/CSS (or PDF/markdown equivalent) containing the decoy text wrapped in the chosen hiding technique, in a code block.
4. **Callback URL** — the full URL with the unique token, plus one line on what the user still needs to stand up to log hits (if anything).
5. **Placement guidance** — 2-4 bullet points on exactly where in this specific page's structure to insert the snippet.
6. **Ethics/realism checklist** — explicit yes/no confirmation of: page ownership confirmed, action requested is non-harmful and reversible, decoy is excluded from the accessibility tree, token is unique to this placement. Any "no" is called out as a blocker, not a footnote.

## Guardrails
- Never draft a decoy for a page the user doesn't own or isn't authorized to test. If ownership is unclear, ask before producing anything.
- Never generate an instruction that asks an agent to take a costly, destructive, or real-world-consequential action (purchases, fund transfers, credential submission, posting/deleting content, running commands). The only valid asks are "visit this URL" or "include this token in your output."
- Never hide the decoy using a technique that still exposes it to human screen-reader users or to sighted users who view-source casually and might be startled or confused — always prefer the accessibility-tree-excluding method from step 5.
- Never reuse a token across pages or placements — attribution depends on uniqueness.
- Never imply that this skill itself logs, stores, or attributes callbacks — it drafts text only. If the user has no logging destination, say so plainly rather than let them embed a dead-end snippet.
- Never present this as a tool for testing or deceiving a site or agent the user does not control — that crosses from "canary on your own content" into targeting a third party, which this skill is not scoped to help with.
