# Guard Rail Starter: A Dependency-Light, Offline Defense-in-Depth Bundle for Budget-Constrained LLM Apps

Every solo developer who ships an LLM feature eventually gets hit by the same three problems in some order: a retry storm that drains a month's API budget in a weekend, a prompt injection that makes the bot say something it shouldn't, and one power user who quietly burns through the whole team's quota before anyone notices. None of these three problems are exotic — but today there is no single, small, offline package that handles all three together. You either hand-roll it yourself, or you adopt an enterprise framework built for a company with a security team, not a side project with one maintainer.

## The Gap

The evidence for this gap is sitting in a real, recent pull request: `nishit546/OpenPrep-AI#2354`, titled "feat(security): AI Token Bucket Rate Limiting, Prompt Injection Guardrails & Daily Quota Guard." A solo maintainer, worried about cost and abuse risk from a single Gemini API dependency, built rate limiting, an injection filter, and a quota guard from scratch, inside their own app, because nothing off-the-shelf covered all three. They're not alone — digging into what else exists turns up Arcjet's `@arcjet/guard`, which bundles the same three protections but is still labeled experimental (`v0.1.0-experimental.0`) and leans on Arcjet's own hosted platform rather than running fully offline. Beyond that, the market splinters into single-purpose point tools — `ai-cost-guard`, `promptsafe-shield`, `@ny-squared/guard`, `@shuangwhywhy/quota-guard` — each covering exactly one of the three protections and none of the others. The heavyweight options, meanwhile — NVIDIA NeMo Guardrails, Guardrails AI, Bedrock Guardrails — do exist and are mature, but they're built for enterprise deployments with a platform team behind them, not a dependency-light drop-in for a budget-constrained solo build. The gap isn't "does any guardrail software exist" — it's "does a small, offline, three-in-one bundle exist for people who can't justify adopting a framework built for a bigger team." Right now it doesn't.

## The Project

The pitch is "helmet.js for LLM apps" — a single, dependency-light, fully offline open-source package that bundles the three protections solo and small-team builders keep rebuilding from scratch: token-bucket or sliding-window rate limiting per user or IP, a lightweight heuristic-plus-classifier prompt-injection pre-filter, and a daily or monthly quota guard tied to actual provider spend rather than raw request counts. It ships as middleware for the major LLM SDKs (OpenAI, Anthropic, Gemini) and the common web frameworks people are already using (Express, Fastify, FastAPI) — no hosted dependency, no sign-up, no platform lock-in. The honest caveat baked into the design from day one: a heuristic-only injection filter kept dependency-light will catch meaningfully less than NeMo Guardrails' full classifier stack, so this has to be marketed as solid basic defense-in-depth, not an enterprise-grade replacement — and it should explicitly say so for anyone running health, legal, or financial content through it.

## Tangible Impact

**Population**: solo developers and small teams (the OpenPrep-AI pattern — a single-maintainer or 2-3 person team shipping a consumer LLM app on one API provider) who cannot justify the integration cost or hosted-platform dependency of NeMo Guardrails, Guardrails AI, or Bedrock Guardrails, and are currently hand-rolling all three protections from scratch, as the evidenced PR shows happening live.
**Mechanism**: a single install covering the three most common abuse/cost-overrun vectors (budget-draining retry storms, injection-driven unwanted outputs, and runaway per-user usage) without requiring a hosted platform account or an enterprise-weight framework, closing the gap between "nothing" and "Arcjet's hosted experimental SDK" or "NeMo Guardrails' full framework."
**Measure**: integration time (target: under 30 minutes from install to all three protections active, vs. the multi-day custom build evidenced in the OpenPrep-AI PR); cost-overrun incidents prevented per month on a simulated abusive-traffic load test; false-positive rate of the injection pre-filter on a corpus of legitimate app-specific queries.

## Try It

A companion Claude Code skill already exists at [`skills/budget-defense-in-depth-guardrail-bundle/`](../skills/budget-defense-in-depth-guardrail-bundle/) — it doesn't build the package, it audits what you already have. Its own one-line description:

> Audits an LLM-powered app's actual rate-limiting, prompt-injection filtering, and spend/quota-guard code (read from the repo or pasted) to score which of those three protections are missing or weak, and drafts minimal, fail-closed config to close each gap. Use before adopting a dedicated guardrail package, before a budget-constrained LLM feature ships, or after a cost-overrun/abuse scare, when the question is specifically these three protections — not a full OWASP LLM Top 10 review.

To use it with Claude Code: drop the `budget-defense-in-depth-guardrail-bundle` folder into `~/.claude/skills/` and Claude will reach for it automatically at the right trigger moments described above. To use it in any other AI chat tool: open the skill's `README.md` and paste its contents straight into the chat, then follow with your repo's LLM-calling code (or a description of your current setup) — it's written to stand alone with no Claude Code install required.

---

Surfaced from `research/2026-11-13-ai-safety-guardrails-in-production.md`, pattern `P1`.
