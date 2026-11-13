# Guard Rail Starter: A Dependency-Light, Offline Defense-in-Depth Bundle for Budget-Constrained LLM Apps

- **Status**: EXPLORING (promoted 2026-11-13 cycle 39: evidence density — 2 independent attempts at the same three-in-one bundle, OpenPrep-AI and Arcjet's `@arcjet/guard`)
- **Date**: 2026-11-13
- **Topic**: AI safety & guardrails in production
- **Source**: research/2026-11-13-ai-safety-guardrails-in-production.md · P6
- **Maturity verdict**: PARTIAL — WebSearch found Arcjet (`@arcjet/guard`, `@arcjet/next`) is the closest match, bundling token-bucket/fixed/sliding-window rate limiting with prompt-injection detection and per-user AI token budgets, but it's marked experimental (v0.1.0-experimental.0) and depends on Arcjet's hosted platform rather than being dependency-light and fully offline. Other candidates (`ai-cost-guard`, `promptsafe-shield`, `@ny-squared/guard`, `@shuangwhywhy/quota-guard`) each cover only one of the three protections. No mature three-in-one offline bundle found.
- **Format**: BOTH
- **Data Sources**: CONNECTED — the application's own LLM API calls (OpenAI/Anthropic/Gemini SDKs), intercepted via in-process middleware, plus the app's existing user/session identifier for per-user quota tracking, and each provider's own usage/billing API (e.g., OpenAI's usage API, Google Cloud Billing API for Gemini) for real spend tracking — these SDKs and billing APIs are mature today; no new third-party connector is needed since the package wraps the app's own existing calls.

## The Gap
GitHub PR `nishit546/OpenPrep-AI#2354`, "feat(security): AI Token Bucket Rate Limiting, Prompt Injection Guardrails & Daily Quota Guard (#2322)," built all three protections from scratch inside the app rather than reaching for an existing lightweight library, explicitly motivated by cost/abuse risk from a single LLM API dependency (Gemini). There is no single small, dependency-light package that bundles rate limiting plus injection detection plus quota guarding specifically for budget-constrained solo-developer LLM apps — the named vendor stacks (NeMo Guardrails, Guardrails AI, Bedrock Guardrails) are heavier and enterprise-oriented.

## The Project
A single, dependency-light, fully offline open-source package (think "helmet.js for LLM apps") bundling the three protections solo/small-team builders keep re-deriving: token-bucket/sliding-window rate limiting per user or IP, a lightweight prompt-injection heuristic-plus-classifier pre-filter, and a daily/monthly quota guard tied to actual provider spend — all running in-process with no hosted dependency, shipped as middleware for the major LLM SDKs (OpenAI, Anthropic, Gemini) and common web frameworks (Express, Fastify, FastAPI).

## Tangible Impact
**Population**: solo developers and small teams (the OpenPrep-AI pattern — a single-maintainer or 2-3 person team shipping a consumer LLM app on one API provider) who cannot justify the integration cost or hosted-platform dependency of NeMo Guardrails, Guardrails AI, or Bedrock Guardrails, and are currently hand-rolling all three protections from scratch, as the evidenced PR shows happening live.
**Mechanism**: a single install covering the three most common abuse/cost-overrun vectors (budget-draining retry storms, injection-driven unwanted outputs, and runaway per-user usage) without requiring a hosted platform account or an enterprise-weight framework, closing the gap between "nothing" and "Arcjet's hosted experimental SDK" or "NeMo Guardrails' full framework."
**Measure**: integration time (target: under 30 minutes from install to all three protections active, vs. the multi-day custom build evidenced in the OpenPrep-AI PR); cost-overrun incidents prevented per month on a simulated abusive-traffic load test; false-positive rate of the injection pre-filter on a corpus of legitimate app-specific queries.

## Why Now
LLM API cost/abuse risk is now a widely-shared concern for solo builders, evidenced directly by the OpenPrep-AI PR's own stated motivation, and Arcjet's experimental release proves the bundled approach is technically viable and wanted — it just hasn't shipped as a mature, offline, framework-agnostic version yet.

## Skill Angle
A "Defense-in-Depth Gap Check" skill — given a description or code snippet of a team's current rate-limiting/injection-filtering/quota-tracking setup (or "we have none"), the skill scores which of the three protections are missing or under-configured and drafts the minimal config needed to close each gap, as a pre-adoption audit before integrating the full package.

## MVP Sketch
2-3 weeks, 1-2 people. Build the rate limiter and quota guard first (token bucket plus a rolling usage counter), add a minimal injection heuristic pre-filter (regex plus a small set of known pattern signatures, upgradeable to an LLM-classifier pass later), ship as a single npm package with middleware for Express and a direct OpenAI/Gemini SDK wrapper, and validate integration time plus false-positive rate against the OpenPrep-AI PR's own three features as the acceptance bar.

## Risks & Open Questions
- Arcjet could graduate its experimental bundle to stable and offline-capable before this ships, directly competing for the same niche.
- A heuristic-only injection pre-filter (to stay dependency-light/offline) will have a meaningfully lower catch rate than NeMo Guardrails' full classifier stack — needs to be marketed honestly as "basic defense-in-depth," not an enterprise-grade replacement.
- Single-provider quota guarding needs per-provider cost-API integration to track real spend, not just request counts — these connectors vary in maturity by provider and need per-provider adapters.
- Evidence base is one PR plus one experimental competitor — real validation requires confirming more solo builders hit this exact gap, not just OpenPrep-AI.
