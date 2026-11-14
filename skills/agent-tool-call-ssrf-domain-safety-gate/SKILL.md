---
name: agent-tool-call-ssrf-domain-safety-gate
description: Audits an agent's fetch-type tool calls (web retrieval, PDF download, model-chosen-URL API calls) for SSRF exposure AND off-topic/abusive-domain exposure together, then drafts the allow/deny policy and SSRF check config for each call site. Use before wiring network-egress safety into an agent that fetches URLs it chooses itself mid-run.
---

# Fetch Guard Audit: Combined SSRF + Domain-Safety Policy Drafting

## When to use this
Use this when someone is building or reviewing an agentic pipeline (research assistant, RAG ingestion job, support agent, PDF/web retrieval step) where **the model itself picks which URL to fetch mid-run**, rather than a human pre-vetting the source — and they want a concrete network-egress safety policy before (or instead of) hand-building SSRF checks and domain filtering from scratch. The trigger moment is a security/design review conversation, not a runtime request: this skill drafts policy, it does not execute fetches or enforce anything live.

Do not reach for this for tools that only ever call a fixed, developer-specified endpoint (no model-chosen URL) — there's no SSRF surface to audit there.

## Inputs
**Data source**: Manual — the user pastes (a) the agent's declared task scope in 1-3 sentences (what it's supposed to be retrieving and why), and (b) the list or actual code of every fetch-type tool call site (tool definitions, function signatures, or the snippet that issues the outbound HTTP request). The skill's output then *recommends* wiring specific CONNECTED resources into the runtime implementation later — for example a named abuse/malware reputation API (Google Safe Browsing API or a comparable mature free-tier URL-reputation service) for the abuse-domain half — but this skill itself never calls that API; it only names it and drafts the config stub for a developer to wire in.

If the user hasn't pasted actual call sites yet, ask for them before drafting anything — a policy written against a vague description of "the agent fetches stuff" is not usable.

## Procedure
1. **Enumerate call sites.** From what's pasted, list every tool/function that can issue an outbound HTTP(S) request to a URL not hardcoded by the developer. If it's ambiguous whether a tool's target URL is model-chosen or fixed, ask.
2. **Score existing SSRF gating per call site** as one of `NONE` / `PARTIAL` / `COVERED`:
   - `COVERED` requires: resolved-IP check against private ranges (RFC 1918, link-local 169.254.0.0/16, loopback) AND cloud metadata endpoints (169.254.169.254, metadata.google.internal, etc.) AND re-validation on every redirect hop (not just the initial URL).
   - `PARTIAL` = some of the above but not all (e.g., checks the initial URL but doesn't re-check after a redirect — the most common real gap).
   - `NONE` = no SSRF check present at all.
3. **Score existing domain-safety gating per call site** as `NONE` / `PARTIAL` / `COVERED`:
   - `COVERED` requires both an abuse/malware reputation check AND a topical-relevance check against the stated task scope.
   - `PARTIAL` = only one of the two.
   - `NONE` = neither.
4. **Draft the SSRF check config** for every call site scored below `COVERED`: private-range blocklist, named cloud metadata IPs to block, a flag requiring redirect-hop re-validation (pin to the resolved IP actually connected to, not the URL string), and a one-line note on DNS-rebinding risk (a check that passes at validation time can still resolve differently at connection time — resolved-IP pinning, not just URL validation, is what closes this).
5. **Draft the domain-safety policy** for every call site below `COVERED`:
   - Abuse/malware half: name one specific mature reputation API appropriate to the user's stack (e.g., Google Safe Browsing API's `urlsafety.lookup`, or a comparable documented free-tier service) and state plainly that this should be wired in, not rebuilt from scratch.
   - Relevance half: turn the pasted task scope into 3-6 topic/keyword descriptors, then draft a simple relevance rule: either a domain-category allowlist consistent with those descriptors, or a check comparing the target page's title/meta-description against the task-scope descriptors (embedding similarity or keyword overlap — state which the user's stack can support). Always state the default action when the classifier is uncertain (recommend: quarantine for human review, never silent-allow).
6. **Produce the policy table** (see Output format) — one row per call site.
7. **Write the audit-log field list** the runtime enforcement should record per fetch attempt (timestamp, call site, target URL, resolved IP, SSRF verdict, domain-safety verdict, final action) so observability exists from day one rather than being bolted on after an incident.
8. **List residual risks explicitly** — do not present the draft as a tested guarantee. At minimum flag: DNS-rebinding exposure if resolved-IP pinning isn't implemented exactly as specified; relevance-classifier false-positive/false-negative rate is unproven until tested against real traffic; redirect re-validation adds latency to every fetch.

## Output format
Produce, in this order:
1. **Task scope restatement** — 1-2 sentences, used as the basis for every relevance judgment below.
2. **Policy table** — columns: `Call site` | `SSRF gating (NONE/PARTIAL/COVERED)` | `Domain-safety gating (NONE/PARTIAL/COVERED)` | `Recommended action` | `Config stub`.
3. **SSRF check config** — one block per call site scored below COVERED, listing the private-range blocklist, metadata-IP blocklist, and redirect-re-validation requirement.
4. **Domain-safety policy** — one block per call site below COVERED, naming the reputation API to wire in and the drafted relevance rule with its uncertain-case default action.
5. **Audit-log field list.**
6. **Residual risks** — bulleted, no fewer than 3.
7. **Before-you-ship test checklist** — at minimum: (a) attempt a fetch to a private-IP literal, (b) attempt a fetch that redirects to a private IP after an initially-public-looking URL, (c) attempt a fetch to a known-abuse-domain test fixture, (d) attempt a fetch to a legitimate but off-topic public domain, confirming each is blocked/quarantined per the drafted policy.

## Guardrails
- Never present the output as a completed, tested guard — it is a design draft. The policy table's "COVERED" status reflects what the user described having today, not what this skill verified by execution.
- Never score or recommend based on SSRF alone — if the user only asks about SSRF, still surface the domain-safety half unprompted; a pattern search confirms numerous public SSRF-only point-solutions already exist, so SSRF-only coverage is not this skill's job to just repeat.
- Never fabricate or guess which threat-intel/reputation API is "mature" — only name ones that are genuinely documented, live, public services, and say so plainly; if unsure, say "name a reputation API your stack already has a budget/contract for" instead of inventing one.
- Never draft a policy without the actual call sites pasted in — a policy against a vague description is unusable and worse than no policy, because it creates false confidence.
- Never recommend "block all redirects" as the SSRF fix without also specifying redirect-hop re-validation as the correct alternative when redirects are operationally required — many real agent fetch flows legitimately need to follow at least one redirect.
- Never score a control as present when the user is unsure it exists ("not totally sure if there's a redirect check anywhere") — default to the stricter, lower score and explicitly list it as an open question needing verification before the policy is finalized, rather than assuming the generous case.
