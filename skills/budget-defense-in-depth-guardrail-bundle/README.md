# Guardrail Gap Check — Rate-Limit / Injection / Quota Audit for Budget-Constrained LLM Apps

Paste this whole prompt, plus the material it asks for, into any AI chat tool (Claude, ChatGPT, Gemini, etc.) to get a fast, honest audit of exactly three protections for an LLM-powered app: per-user rate limiting, prompt-injection filtering, and spend/quota guarding. This is for solo developers and small teams who can't justify an enterprise guardrail framework and want to know, before they hand-roll anything or buy a package, which of these three they already have, which are weak, and what the smallest fix for each gap looks like.

This is **not** a general security review. It does not cover PII handling, supply-chain risk, output sanitization, or the full OWASP LLM Top 10 — only these three cost/abuse-facing protections.

## What to hand over

**Data source: Manual.** In a generic chat tool there's no connector or file access, so you need to paste:
1. The code that calls your LLM SDK (OpenAI/Anthropic/Gemini/other) — the actual function or middleware that sends a user's input to the model.
2. Any existing rate-limiting, injection-filtering, or quota/spend-tracking code you already have, even if partial or you're not sure it works.
3. *(Optional, improves the quota-guard verdict)* Recent usage or billing numbers — tokens or dollars per day/month, if you have them. If you don't, say so; the audit will flag quota risk based on request counts alone instead of inventing a number.
4. Which LLM provider(s) you're on, and roughly how many real users/requests you expect per day (a ballpark is fine — this sizes the rate-limit suggestion).

If you're using this inside Claude Code with access to your actual repository instead of a chat tool, Claude can read the relevant files directly (the LLM call sites, middleware, config) and skip steps 1–2 above — just say "audit my repo for the guardrail gap check" and let it search.

## What happens next

The assistant will:

1. **Confirm scope** — name the provider(s) you're using and note whether it's working from pasted material or direct repo access.
2. **Check each of the three protections for real evidence**, not just intent:
   - **Rate limiting**: is there a per-user or per-IP throttle that actually *rejects* excess requests (token bucket, sliding/fixed window), or does it only log?
   - **Prompt-injection filtering**: is user input (or any retrieved/tool content) checked against known injection patterns or a classifier before it reaches the model?
   - **Quota/spend guard**: is there a daily/monthly cap on token count or dollar spend, per user and/or globally, that actually stops further calls on breach?
3. **Score each one**: `COVERED` (real enforcing code shown), `PARTIAL` (exists but weak — logs only, one endpoint only, counts requests but not real spend), `MISSING` (nothing found), or `UNKNOWN` (you say you have it but didn't show code — this never gets scored as covered on your word alone; show the file or it stays `UNKNOWN`).
4. **For every gap** (anything not `COVERED`), it drafts a minimal, ready-to-adapt, **fail-closed** snippet to close it — meaning the snippet rejects/raises on breach, it never just logs the problem and lets the call through:
   - Rate limiting → a token-bucket or sliding-window snippet in your actual framework, sized to your stated traffic (or an explicitly-labeled assumption if you didn't give a number).
   - Prompt injection → a short named list of known injection phrasings (e.g. "ignore previous instructions", "reveal your system prompt") as a pre-filter, plus a note on escalating to an LLM-classifier pass later — labeled clearly as basic/heuristic defense, not enterprise-grade.
   - Quota guard → a per-user and global cap wrapper that checks cumulative spend before each call and hard-stops on breach.
5. **Gives you an overall score** (`X/3 covered`) and a **priority order** for fixing what's left — cost-overrun risk (rate limit + quota) is ranked first by default, unless your app's specifics (e.g. heavy untrusted document input, no money-bearing actions) point the other way, in which case it says why.
6. **Flags regulated content.** If your app touches health, legal, financial, or similarly high-stakes content, it will explicitly say a heuristic-only injection filter isn't enough there and point you toward a dedicated classifier or managed framework (NeMo Guardrails, Guardrails AI, Bedrock Guardrails) for that surface specifically.

## Output you'll get

```
## Guardrail Gap Check — <provider(s)>, <repo-read | chat-paste> mode

| Protection | Status | Evidence | Risk if unaddressed |
|---|---|---|---|
| Rate limiting | ... | ... | ... |
| Prompt-injection filtering | ... | ... | ... |
| Quota/spend guard | ... | ... | ... |

**Overall: X/3 covered.**

## Fixes, in priority order
### 1. <Protection> — <status>
<why it's ranked here>
<code block: minimal fail-closed fix>
Assumptions made: ...

## Caveats
- <data gaps, e.g. no billing export provided>
- <regulated-content flag if relevant>
- Scope reminder: only these three protections, not a full security review.
```

## Ground rules this audit follows

- It will never mark something `COVERED` just because you say you have it — it needs to see the actual code, or it stays `UNKNOWN`.
- It will never invent numbers — no fabricated catch rates, dollar savings, or traffic figures. Anything it can't verify from what you gave it, it labels as an assumption out loud.
- Every fix it drafts fails closed: on breach, the code rejects or raises, it never just logs and continues (a quota guard or rate limiter that only logs isn't actually a guard).
- It will not claim these fixes are equivalent to an enterprise guardrail framework for regulated or safety-critical content — it says so explicitly when that applies to your app.
- If you only give it enough to check one or two of the three protections, it will say which ones it couldn't assess and why, rather than guessing a status to fill out the table.
