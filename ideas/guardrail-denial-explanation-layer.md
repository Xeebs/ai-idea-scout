# Why Blocked: A Cross-Backend Denial Explanation Layer for Guardrail-Blocked Actions

- **Status**: PROPOSED
- **Date**: 2026-11-13
- **Topic**: AI safety & guardrails in production
- **Source**: research/2026-11-13-ai-safety-guardrails-in-production.md · P4
- **Maturity verdict**: PARTIAL — WebSearch found plenty of backend "attach a reason to the denial" infrastructure (`reasongate`, small Rust crates like `embacle`/`prompty`/`heartbit-core`/`bitrouter-guardrails`, and vendor governance blogs arguing reasons should name the controlling rule) but no reusable, generic end-user-facing UI component for explaining a block to the person who tried it — the data plumbing exists narrowly, the user-facing layer does not.
- **Format**: BOTH
- **Data Sources**: CONNECTED — the guardrail or policy engine's own denial event (rule ID, triggered category, confidence score), reached via whichever backend emits it (NeMo Guardrails violation events, Guardrails AI validator failures, reasongate's rule-based denials, or a custom app's own block event) — no single mature cross-vendor connector exists yet, so the project ships adapters normalizing a handful of common backends into one schema.

## The Gap
GitHub PR `alehar9320/agentic-odi#924`, "feat(studio): explain a blocked action where the person tried it (#510)," built `BlockedReasonNote.tsx`/`blockedReason.ts` from scratch for one internal studio product — there is no generic, reusable "guardrail denial explainer" component in evidence anywhere in this run. Most other guardrail discussion in this run's digest (Spring AI Privacy Guardrails, CanaryGuard, OpenPrep-AI) is about detection and blocking, not about explaining the block back to the end user who triggered it.

## The Project
A drop-in explanation layer: a backend adapter normalizes denial events from any guardrail backend into one schema (rule ID, category, confidence, a plain-language template), and a frontend component library (React first, matching the one proven internal pattern) renders a specific, actionable explanation instead of a silent block — e.g., "This request was blocked because it asked the assistant to share a customer's SSN (PII disclosure policy). Try rephrasing without identifying details." A template library maps common guardrail categories to clear, non-technical language, since raw rule IDs and confidence scores aren't usable by end users on their own.

## Tangible Impact
**Population**: end users of internal enterprise AI agent platforms and AI-assisted SaaS tools who hit a guardrail block mid-task — the sales reps, support agents, and analysts using internal copilots/studio tools like the one evidenced in this digest, and customers of AI products that enforce content or action policies, narrowed specifically to "a person who tried an action, had it silently blocked, and had no way to know why."
**Mechanism**: replacing a silent block with a specific explanation cuts the trial-and-error loop users currently run (rephrase blindly, retry, give up, or file a support ticket) and reduces the perception that the tool is broken or arbitrarily restrictive, without weakening the guardrail itself.
**Measure**: support-ticket volume tagged "why was this blocked" before/after rollout; successful-retry rate within a few attempts after a block (does the user reach a correct, allowed action on their own); user-reported trust/clarity score on blocked interactions.

## Why Now
Multiple vendors already attach a reason field to denials at the backend (reasongate, the small Rust crates found in this digest) — the data plumbing is commodity now; only the normalization-across-backends and the end-user-facing component are missing, a much smaller build than it would have been even a year ago.

## Skill Angle
A "Denial Message Drafting" skill — given a guardrail's raw denial payload (rule ID/category/confidence) and the product's tone-of-voice guidelines, the skill drafts the plain-language explanation and suggested next step shown to the end user. This lets a team improve their denial copy without building the full adapter/component library first.

## MVP Sketch
2-3 weeks, 1-2 people. Pick two open-source guardrail backends (NeMo Guardrails and Guardrails AI) plus the custom-event case, write adapters normalizing each into one denial schema, ship a React component rendering it, and A/B test against a silent-block control on one real internal tool's guardrail-triggering flows, measuring successful-retry rate.

## Risks & Open Questions
- Explaining exactly why something was blocked can itself leak information useful for crafting a bypass — needs a deliberately vague-but-helpful template tier for security-sensitive categories.
- Only one real-world implementation (`alehar9320/agentic-odi`) was found — validating that other teams want this beyond one studio product is the key open question.
- Guardrail vendors (NeMo Guardrails, Guardrails AI) could ship this as a first-party feature, which would commoditize the adapter layer quickly.
