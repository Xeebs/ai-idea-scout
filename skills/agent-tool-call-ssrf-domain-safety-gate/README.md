# Fetch Guard Audit: Combined SSRF + Domain-Safety Policy Drafting

A self-contained prompt template. Paste the block below into any AI chat tool (Claude, ChatGPT, Copilot Chat, etc.), fill in the `<your task scope>` and `<your fetch call sites>` placeholders with your own agent's details, and send it.

## When to use this

Use this when you're building or reviewing an agentic pipeline — a research assistant, a RAG ingestion job, a support agent, a web/PDF retrieval step — where **the model itself picks which URL to fetch while it's running**, rather than a human pre-approving the source. You want a concrete network-egress safety policy (SSRF defense plus domain-safety filtering) before you hand-build it, or before you trust whatever partial guard you already have.

This is a design-review exercise, not a live security scan: it produces a written policy and config draft for you (or a developer) to implement and test, not a runtime check that actually executes anything.

Skip this if your tool only ever calls a fixed URL the developer hardcoded — there's no SSRF surface to review there.

## What to hand over before you start

- Your agent's declared task scope, in 1-3 sentences (what it's supposed to be retrieving and why).
- Every fetch-type tool call site: the actual code, tool definition, or function signature that issues the outbound HTTP(S) request. If you don't have this handy, list each tool's name and what it fetches in plain language — but the more concrete, the better the output.
- Any existing allow/deny list or partial guard you already have in place, if any (so the audit doesn't recommend rebuilding something you already have).

If you don't have call sites to paste yet, say so — the assistant should ask for them rather than drafting a policy from a vague description.

## The prompt template

```
I'm building/reviewing an agent whose tools can fetch URLs it chooses itself
mid-run (not a fixed, hardcoded endpoint). I need a combined SSRF-defense and
domain-safety policy audit — not just SSRF, but also whether the agent could
reach an off-topic or abusive public domain that an SSRF-only check wouldn't
catch.

Agent task scope: <your task scope, 1-3 sentences>

Fetch-type tool call sites:
<paste each tool's code/definition, or at minimum name + what it fetches>

Existing guards already in place (if any): <describe, or say "none">

Please:
1. List every call site and score its current SSRF gating as
   NONE / PARTIAL / COVERED. COVERED requires: private-IP-range blocking
   (RFC 1918, link-local, loopback) + cloud-metadata-endpoint blocking
   (e.g. 169.254.169.254) + re-validation on every redirect hop, not just
   the initial URL.
2. Score current domain-safety gating per call site as NONE / PARTIAL /
   COVERED. COVERED requires both an abuse/malware reputation check AND a
   topical-relevance check against my stated task scope.
3. For anything below COVERED on either axis, draft:
   - an SSRF check config (blocklist contents, redirect-re-validation
     requirement, a note on DNS-rebinding risk and why resolved-IP pinning
     — not just URL validation — closes it)
   - a domain-safety policy: name one specific real, documented reputation
     API I should wire in for the abuse/malware half (don't invent one —
     if unsure, tell me to name one my stack already has access to), plus
     a relevance rule derived from my task scope (keyword or embedding-
     similarity check against the target page's title/meta-description),
     with an explicit default action for when the classifier is uncertain
     (should default to quarantine for human review, never silent-allow).
4. Give me a policy table: call site | SSRF status | domain-safety status |
   recommended action | config stub.
5. Give me an audit-log field list the runtime enforcement should record
   per fetch attempt.
6. List residual risks honestly — don't present this as a tested guarantee.
7. Give me a before-you-ship test checklist: a private-IP-literal fetch
   attempt, a redirect-to-private-IP attempt, a known-abuse-domain fetch
   attempt, and a legitimate-but-off-topic-domain fetch attempt, each
   expected to be blocked or quarantined.

Don't just cover SSRF and skip domain-safety even if that's most of what
I asked about — the combined check is the point: an SSRF-only guard still
lets the agent happily fetch a legitimate-looking but off-topic or abusive
domain, and a domain-reputation-only check doesn't stop the agent reaching
an internal service via a redirect chain.
```

## What you'll get back

A structured policy audit, in this order:

1. **Task scope restatement** (1-2 sentences) — the basis for every relevance judgment that follows.
2. **Policy table** — one row per fetch call site: SSRF gating status, domain-safety gating status, recommended action (allow/deny/quarantine), config stub.
3. **SSRF check config** per call site that needs work — blocklists plus the redirect-re-validation requirement.
4. **Domain-safety policy** per call site that needs work — named reputation API to wire in, plus the drafted relevance rule and its uncertain-case default.
5. **Audit-log field list** for the runtime implementation.
6. **Residual risks** (at least 3, stated plainly — e.g. DNS-rebinding exposure if resolved-IP pinning isn't implemented, unproven relevance-classifier false-positive rate, redirect-re-validation latency cost).
7. **Before-you-ship test checklist** — the four fetch attempts listed above, each should be blocked or quarantined by the drafted policy.

## What this will not do

- It will not execute any fetch or actually check a live reputation API — it drafts the policy and config, you or your developer wires it in and tests it.
- It will not invent a threat-intel API name if none is genuinely documented and live — it will tell you to name one instead of fabricating a plausible-sounding service.
- It will not score your existing setup as COVERED just because you have *an* SSRF check — COVERED requires private-range blocking, metadata-endpoint blocking, and redirect re-validation together, and separately requires both halves of domain-safety together.
- It will not produce a usable policy from a vague "the agent fetches some stuff" description — it needs your actual call sites.
