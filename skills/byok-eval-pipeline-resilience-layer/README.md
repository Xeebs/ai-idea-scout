# Key Guard Audit: BYOK Eval Pipeline Rate-Limit Resilience Review

Paste the prompt below into any AI chat tool (ChatGPT, Claude, Gemini, etc.) along with your judge-calling code to get a precise diagnosis of whether a provider rate-limit burst will silently lose your LLM-judge evaluation results — and the exact fix, scoped to what's actually wrong.

## When to use this

You're building or operating an LLM-as-judge evaluation pipeline against your own provider key (OpenAI, Azure OpenAI, Anthropic, or Gemini) — a custom eval harness, a CI eval job, or glue code wired into a platform like PostHog AI evals or Langfuse — and either:
- a rate-limit burst just wiped out a batch of judge evaluations and you want to know exactly why, or
- you want a pre-launch review of whether your judge-calling code will survive a 429 burst without losing results or needing manual cleanup afterward.

This is a one-shot review. It reads code/config you paste and gives you a diagnosis plus a fix — it does not connect to any live system or run anything for you.

## What to hand over

**Data source: Manual.** You paste the actual code, pseudocode, or config — nothing is read automatically from any API or connector. Specifically provide:

1. **The judge-calling code or config** — the snippet that invokes your provider for one judge evaluation, including whatever error handling already exists (or say plainly if there's none).
2. **What happens today on a 429** — in your own words, or let the reviewer infer it from the code: does the evaluation get marked failed, silently dropped, retried a fixed number of times, something else?
3. *(Optional, improves accuracy)* Which provider(s) you use, and whether this is a one-off eval run or a long-lived service that needs to survive a process restart mid-incident.

If your snippet has no visible error handling around the provider call, don't let the reviewer guess what happens on failure — that gap ("failure path undefined") is itself the first finding.

## The prompt

Copy everything below the line, fill in your details, and paste it into your AI tool of choice.

---

You are auditing an LLM-as-judge evaluation pipeline's resilience to provider rate-limit (429) bursts. I will give you the code/config that calls my judge provider. Do not guess behavior that isn't shown in what I paste — if part of the failure path lives in code I haven't shown, say so explicitly instead of assuming best-case behavior.

My judge-calling code/config:
```
<PASTE YOUR CODE OR CONFIG HERE>
```

What happens today on a 429 (my understanding, may be incomplete): <DESCRIBE OR WRITE "UNKNOWN">

Provider(s) in use: <e.g. OpenAI, Azure OpenAI, Anthropic, Gemini>
Is this a one-off run or a long-lived service that must survive a restart mid-incident: <ANSWER>

Follow this procedure exactly:

1. Locate the exact line(s) where the code calls the provider for a judge evaluation. Ignore everything else (prompt construction, scoring, aggregation).
2. Trace what happens if that call raises/returns a rate-limit error: is there a try/except (or equivalent) at all; is the error type checked specifically for rate-limit vs caught generically; is there retry logic, and if so how many attempts, fixed delay vs exponential backoff, and does it honor a Retry-After header/field; and when retries are exhausted (or there are none), what happens to that evaluation's result — recorded as failed, silently dropped, or does it crash the whole batch?
3. Check specifically for two failure signatures (a generic "does it retry" check is not sufficient):
   - Signature A — Burst-exhaustion data loss: once the key hits a sustained 429 burst (not a single transient 429), do in-flight/queued evaluations get marked permanently failed/lost with no way to resume once the key recovers?
   - Signature B — Manual re-enable requirement: after the burst ends, does anything require a human to re-validate the key or re-trigger each affected evaluation individually, instead of the pipeline detecting the key is healthy again and resuming automatically?
4. Classify overall resilience as exactly one of: NONE (no retry/backoff at all), TRANSIENT-ONLY (handles isolated 429s but a sustained burst still causes permanent loss — Signature A present), PARK-CAPABLE (failed evaluations are held in a recoverable state but nothing auto-resumes them — Signature B present), or RESILIENT (survives a sustained burst and resumes automatically with no manual step).
5. Name the one specific fix scoped to that classification — not a generic "add retries" suggestion. NONE needs provider-aware retry/backoff honoring Retry-After first (and say this alone doesn't fix Signature A/B). TRANSIENT-ONLY needs a persistent pending-recovery state for evaluations that exhaust retries, keyed to key health, instead of marking them failed. PARK-CAPABLE needs an automatic resume trigger (health-check poll or provider success callback) that drains parked evaluations without manual re-enable. RESILIENT needs only hardening suggestions (e.g., does parked state survive a process restart).

Give me the output in exactly this format:

```
Judge call location: <where in the snippet the provider call happens>
Failure path as written: <what currently happens on a 429, cited to specific lines, or "undefined — no error handling visible">
Signature A (burst-exhaustion data loss): PRESENT | ABSENT — <why>
Signature B (manual re-enable required): PRESENT | ABSENT — <why>
Resilience level: NONE | TRANSIENT-ONLY | PARK-CAPABLE | RESILIENT
Specific fix: <the one concrete change scoped to this resilience level>
```

If I pasted code for multiple providers, repeat this block once per provider — resilience level often differs between them even in the same codebase.

Rules you must follow:
- Never conclude RESILIENT without evidence of both automatic resume AND survival of a sustained burst — a single retry decorator alone does not clear Signature A.
- Never recommend a generic backoff library as the full fix when Signature A or B is present — name the park/resume state change too, not just the library.
- If my snippet is incomplete, say so and mark that part of the trace unknown rather than assuming best-case behavior.
- Don't fabricate a specific provider's real rate-limit/retry-after behavior if I didn't name the provider — only reason about the code I gave you.

---

## What you get back

A short structured diagnosis (one block, or one per provider if you pasted more than one integration) naming exactly where the failure path breaks down, which of the two BYOK-specific failure signatures are present, an overall resilience classification, and one concrete fix scoped to that classification — not a generic "just add retries" answer.
