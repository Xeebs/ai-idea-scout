---
name: byok-eval-pipeline-resilience-layer
description: Audits the code/config a team uses to call its LLM-judge provider (OpenAI/Azure OpenAI/Anthropic/Gemini) in an eval pipeline, and pinpoints exactly where a 429/rate-limit burst causes silent evaluation data loss versus where it's actually recoverable. Use when someone is debugging "we lost eval results after a rate-limit spike" or designing/reviewing a BYOK eval pipeline's judge-calling path before it ships.
---

# Key Guard Audit: BYOK Eval Pipeline Rate-Limit Resilience Review

## When to use this
Someone is building or operating an LLM-as-judge evaluation pipeline against their own provider key (OpenAI, Azure OpenAI, Anthropic, or Gemini) — a custom eval harness, a CI eval job, or glue code wired into a platform like PostHog AI evals or Langfuse — and either (a) just had a rate-limit burst wipe out a batch of judge evaluations and wants to know exactly why, or (b) wants a pre-launch review of whether their judge-calling code will survive a 429 burst without losing results or requiring manual cleanup afterward.

This is a one-shot design/code review, not a running system. It produces a diagnosis and a specific fix, not a deployed queue.

## Inputs
**Data source**: Manual — the user pastes the actual code, pseudocode, or config that calls their judge provider inside the eval loop (the HTTP/SDK call, any existing try/except or retry wrapper, and how a failed call's result is recorded — e.g., marked failed, skipped, left null, or retried). This skill never connects to a live provider API or pipeline; it works entirely from what's pasted.

Required from the user:
1. **The judge-calling code or config** — the actual snippet that invokes the provider for one judge evaluation, including whatever error handling already exists (even if it's "none").
2. **What happens today on a 429** — in their own words or inferable from the code: does the evaluation get marked failed, silently dropped, retried a fixed number of times, or something else?
3. *(Optional but improves accuracy)* **Provider(s) in use** and whether this is a single eval run or a long-lived service that needs to survive a process restart mid-incident.

If the pasted snippet has no visible error handling around the provider call at all, don't guess what happens on failure — say explicitly that the failure path is undefined from the code shown and that's itself the first finding.

## Procedure
1. **Locate the judge call boundary.** Identify the exact line(s) where the code calls the provider SDK/API for a judge evaluation. Everything else (prompt construction, scoring, aggregation) is out of scope for this audit.
2. **Trace the failure path for a 429 specifically.** Follow what happens if that call raises/returns a rate-limit error:
   - Is there a `try/except` (or equivalent) around the call at all?
   - If caught, is the error type checked (429 / rate-limit specifically) or is it caught generically alongside unrelated errors?
   - Is there any retry? If so, how many attempts, fixed delay or exponential backoff, and does it read a `Retry-After` header/field if the provider sends one?
   - When retries are exhausted (or there are none), what happens to *that evaluation's result* — is it recorded as failed, left absent from output, logged and dropped, or does it crash the whole batch?
3. **Check for the two BYOK-specific failure signatures** this skill exists to catch (the generic "does it retry" question is necessary but not sufficient):
   - **Signature A — Burst-exhaustion data loss**: once the key hits a sustained 429 burst (not a single transient 429), do in-flight and queued evaluations get marked permanently failed/lost, with no mechanism to resume them once the key recovers? This is distinct from a single retried call succeeding.
   - **Signature B — Manual re-enable requirement**: after the burst ends, does anything in the code/config require a human to re-validate the key or re-trigger each affected evaluation individually, versus the pipeline automatically detecting the key is healthy again and resuming on its own?
4. **Classify the overall resilience level**:
   - **NONE** — no retry/backoff at all; any 429 fails the evaluation immediately.
   - **TRANSIENT-ONLY** — retries/backoff exist for isolated 429s, but a sustained burst that exhausts retries still causes permanent loss (Signature A present).
   - **PARK-CAPABLE** — failed evaluations are held in a recoverable state (queue, DB row, flag) rather than discarded, but nothing automatically resumes them (Signature B present).
   - **RESILIENT** — evaluations survive a sustained burst and resume automatically once the key is healthy again, with no required manual step.
5. **Name the specific fix**, scoped to the gap found — not a generic "add retries" suggestion:
   - NONE → add provider-aware retry with exponential backoff honoring `Retry-After` first; this alone does not fix Signature A or B, say so.
   - TRANSIENT-ONLY → add a persistent "pending-recovery" state for evaluations that exhaust retries, keyed to the provider key's health, instead of marking them failed.
   - PARK-CAPABLE → add an automatic resume trigger (health-check poll or provider success callback) that drains parked evaluations without a manual re-enable step per evaluation.
   - RESILIENT → note that the pipeline already handles this; suggest only hardening (e.g., does parked state survive a process restart, per the MVP's own open question about queue durability).

## Output format
```
Judge call location: <file/function or description of where in the snippet the provider call happens>
Failure path as written: <what currently happens on a 429, cited to the specific code/config lines or "undefined — no error handling visible">
Signature A (burst-exhaustion data loss): PRESENT | ABSENT — <why>
Signature B (manual re-enable required): PRESENT | ABSENT — <why>
Resilience level: NONE | TRANSIENT-ONLY | PARK-CAPABLE | RESILIENT
Specific fix: <the one concrete change scoped to this resilience level, not a generic "add retries">
```
If multiple provider integrations are pasted (e.g., separate OpenAI and Anthropic call sites), repeat the block per provider — resilience level often differs between them even in the same codebase.

## Guardrails
- Never conclude RESILIENT without evidence of both an automatic resume mechanism AND survival of a sustained burst, not just a working single-retry — "it has a retry decorator" is not enough to clear Signature A.
- Never recommend a generic backoff library as the full fix when Signature A or B is present — naming the library without the park/resume state change is a half-fix that will still lose data on a long enough burst.
- If the pasted snippet is incomplete (e.g., error handling lives in a file not shown), say so explicitly and mark that part of the trace as unknown rather than assuming best-case behavior.
- Do not simulate or fabricate what a provider's actual rate-limit/retry-after behavior is for a provider not named by the user — only reason about the code shown.
