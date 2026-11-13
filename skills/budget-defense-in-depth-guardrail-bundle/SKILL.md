---
name: budget-defense-in-depth-guardrail-bundle
description: Audits an LLM-powered app's actual rate-limiting, prompt-injection filtering, and spend/quota-guard code (read from the repo or pasted) to score which of those three protections are missing or weak, and drafts minimal, fail-closed config to close each gap. Use before adopting a dedicated guardrail package, before a budget-constrained LLM feature ships, or after a cost-overrun/abuse scare, when the question is specifically these three protections — not a full OWASP LLM Top 10 review.
---

# Guardrail Gap Check: Rate-Limit / Injection / Quota Audit for Budget-Constrained LLM Apps

## When to use this
A solo developer or small team is shipping (or already running) an LLM feature on a single API provider and wants a fast, honest answer to "which of the three most common abuse/cost vectors — retry-storm rate abuse, prompt injection, runaway per-user spend — are we actually protected against today, and what's the smallest fix for each gap?" Trigger moments:
- Pre-launch review of an LLM feature before it goes to real users.
- A provider bill came in higher than expected, or a 429-storm/abuse complaint just happened.
- Deciding whether to hand-roll these three protections or adopt a dedicated bundle/library — this audit is the "do we even need the full package, or just one piece" check that should happen first.

This is **not** a general LLM security review (OWASP LLM Top 10, PII handling, supply chain, etc.) — it only scores these three specific protections. Say so explicitly if the user asks for a broader audit; point them elsewhere for that.

## Inputs
**Data source**: Connected — when run inside Claude Code with repository access, this skill reads the app's own LLM API call sites, middleware, and config files directly (via Read/Grep: the code that calls the OpenAI/Anthropic/Gemini SDK, any existing rate-limiter or quota-tracking modules) and, if the user has a provider usage/billing CLI or exported report available locally (e.g. OpenAI usage API output, Anthropic console export, GCP Billing export for Gemini), reads that too for real spend numbers — these SDKs and billing APIs are mature today, no new connector is needed. **Fallback (portable/chat-tool use, no filesystem access)**: Manual — the user pastes (1) the code that calls the LLM SDK, (2) any existing rate-limiter/injection-filter/quota code, even partial, and (3) recent usage or billing figures if they have them (optional but improves the quota-guard verdict).

If neither repo access nor a paste is available, say the audit cannot proceed and name exactly what's missing — never produce a scorecard from zero evidence.

## Procedure
1. **Confirm scope.** Identify the LLM provider(s) in use and whether this is running with repo access (Claude Code) or chat-paste mode. State which mode is active in the output.
2. **Gather evidence per protection** — read the repo (Grep/Read) or scan what was pasted for each:
   - **Rate limiting**: a per-user or per-IP throttle actually enforced before/around the LLM call (token bucket, sliding/fixed window, `express-rate-limit`, `slowapi`, a hand-rolled counter with a reject path). A counter that only *logs* without rejecting does not count.
   - **Prompt-injection filtering**: any check applied to user input (or retrieved/tool content) before it reaches the model — a denylist/regex pre-filter, a classifier call, structured-input enforcement, or explicit system-prompt hardening against instruction override.
   - **Quota/spend guard**: a daily or monthly cap tied to actual token count or dollar spend, per user and/or global, with code that stops further calls on breach (not just a dashboard metric).
3. **Score each of the three**, independently:
   - `COVERED` — real enforcing code found; quote the file/line or pasted snippet as evidence.
   - `PARTIAL` — something exists but is weak: applies to only one code path/endpoint, logs but doesn't reject, has an easily-bypassed limit (e.g. per-IP only on an app with shared NAT users), or the quota guard tracks requests but not actual token/dollar spend.
   - `MISSING` — nothing found after checking.
   - `UNKNOWN` — the user asserts a protection exists but no supporting code/config was shown. Never upgrade `UNKNOWN` to `COVERED` on a verbal claim alone — ask for the file instead, or report `UNKNOWN` with that caveat if they can't provide it.
4. **For every `MISSING`, `PARTIAL`, or `UNKNOWN` result**, draft a minimal, concrete, fail-closed config to close it:
   - Rate limiting → a token-bucket or sliding-window snippet in the app's actual language/framework (Express/Fastify middleware, FastAPI dependency, or a bare wrapper function if framework is unclear), sized to a stated or explicitly-assumed RPM baseline — state the assumption out loud if the user didn't give real traffic numbers.
   - Prompt injection → a minimal heuristic pre-filter: a short, named pattern list (e.g. "ignore previous instructions", "reveal your system prompt", role-override phrasing) plus a one-line note on escalating to an LLM-classifier pass later. Label this explicitly as basic/heuristic-only, not an enterprise-grade replacement.
   - Quota guard → a per-user and global daily/monthly cap wrapper that checks cumulative token/dollar spend before each call and hard-stops (fails closed, raises/rejects) on breach — never a snippet that logs the breach and lets the call through anyway.
5. **Compute an overall score** — `X/3 protections covered` — and a **priority fix order**: rank gaps by cost-overrun risk first (since budget-draining retry storms and runaway quota are typically the most financially acute for a solo/small-team budget), then injection, unless the evidence gathered in step 2 shows a specific reason to reorder (e.g. the app already handles no money-bearing actions but does handle untrusted document input — then injection ranks first). State the reason for the ranking.
6. **Flag regulated/safety-critical content.** If the app's description involves health, legal, financial, or other high-stakes content, add an explicit note that a heuristic-only injection filter (step 4) is insufficient for that surface and recommend a dedicated classifier layer or managed guardrail framework (e.g. NeMo Guardrails, Guardrails AI, Bedrock Guardrails) for that specific surface.
7. **Write the report** in the format below.

## Output format
```
## Guardrail Gap Check — <provider(s)>, <repo-read | chat-paste> mode

| Protection | Status | Evidence | Risk if unaddressed |
|---|---|---|---|
| Rate limiting | COVERED/PARTIAL/MISSING/UNKNOWN | <file/line or paste quote, or "none found"> | <concrete risk> |
| Prompt-injection filtering | ... | ... | ... |
| Quota/spend guard | ... | ... | ... |

**Overall: <X>/3 covered.**

## Fixes, in priority order
### 1. <Protection name> — <status>
<one-line rationale for why this is ranked here>
```<language>
<minimal fail-closed config/code>
```
Assumptions made: <stated traffic/budget baseline, or "none — real figures provided">

### 2. ...
### 3. ...
(Only include protections that scored MISSING/PARTIAL/UNKNOWN. If all three are COVERED, say so and skip the fixes section.)

## Caveats
- <data gaps: e.g. "no usage/billing export provided — quota-guard risk assessed on request counts only, not real spend">
- <regulated-content flag if triggered in step 6>
- This audit covers only rate limiting, prompt-injection filtering, and quota/spend guarding — not a full LLM security review (PII handling, supply chain, output-handling, etc.).
```

## Guardrails
- Never mark a protection `COVERED` without quoting the actual enforcing code (file/line from the repo, or the pasted snippet) — a comment, a TODO, or a verbal claim with nothing to show is `UNKNOWN`, not `COVERED`.
- Never invent catch rates, dollar-savings figures, incident counts, or traffic numbers — state real numbers only when the user or the repo's own code/config provides them; otherwise label a figure as an explicit assumption.
- Every drafted quota-guard or rate-limit snippet must fail closed (reject/raise on breach) — never produce a snippet that logs a breach and lets the call through anyway, since that contradicts the entire point of the audit.
- Never claim this audit, or the minimal fixes it drafts, is equivalent to or a replacement for an enterprise guardrail framework (NeMo Guardrails, Guardrails AI, Bedrock Guardrails) on regulated or safety-critical content — say so explicitly when that content type is present.
- When running with repo access, actually read the files — don't ask the user to re-describe what Grep/Read can find directly. Only fall back to requesting a paste when no repo context exists or the relevant code genuinely isn't in the repo (e.g. config lives in a hosted dashboard).
- If evidence is too thin to score all three (e.g. only one file was shared and it doesn't touch the other two protections), say which protections could not be assessed and why — never fill in a guessed status to complete the table.
