# No Leak: Fail-Closed Privacy Router Audit

A self-contained prompt template for auditing a local/cloud LLM routing setup for silent cloud-fallback leak risk. Paste the block below into any AI chat tool (Claude, ChatGPT, etc.), fill in your code, and send it.

## When to use this

You're building or maintaining an app that routes LLM calls between a local model (Ollama, llama.cpp, a small on-device model) and a cloud model (OpenAI, Anthropic, Gemini, or similar) as a fallback — usually for cost, availability, or latency. The app handles data that must never reach the cloud path: clinical notes, legal filings, confidential sources, or other PII. You want to know: under realistic failure conditions (timeouts, oversized prompts, ambiguous content), could a sensitive request ever silently end up at the cloud model?

This is a one-time review of your routing design, not a tool you install. It produces a findings report and a draft fail-closed config you can adapt into your own router.

## What to hand over

Paste:
1. The actual code or config that decides local vs. cloud routing — including the timeout/exception handler, any retry logic, and any size limits. A description alone isn't enough; the reviewer needs the real logic.
2. However sensitivity is currently determined for a request — an explicit flag field, a keyword/regex check, a classifier call, or "nothing yet."
3. Optionally, the sensitivity categories that matter in your domain (e.g., clinical diagnosis content, attorney-client privileged material, protected sources, generic PII).

No API keys, no live data, no connector setup — this works purely from what you paste.

## The prompt template

```
You are auditing my local/cloud LLM routing setup for silent cloud-fallback
leak risk — cases where a sensitive request could end up reaching the cloud
model even though it was supposed to stay local-only.

Here is my routing/fallback code or config:
<PASTE CODE OR CONFIG HERE>

Here is how sensitivity is currently determined for a request (or state "not
handled yet"):
<DESCRIBE OR PASTE>

Sensitivity categories that matter for my domain (optional):
<LIST CATEGORIES, e.g. clinical notes, legal privilege, source protection, PII>

Please:
1. Confirm you can identify the local path, the cloud path, and the current
   sensitivity mechanism in what I pasted. If anything critical is missing
   (especially the timeout/exception/retry handling), say so and ask for it
   before giving any verdict.
2. Check specifically for these six known failure modes and flag every one
   that applies, with the exact line/snippet and a concrete triggering
   scenario:
   - A timeout or exception handler that falls back to cloud on ANY failure,
     without checking sensitivity first.
   - Routing decided by prompt/document size alone, with no sensitivity
     check layered on top.
   - Sensitivity being guessed from the text (keywords/regex) instead of
     read from an explicit label — flag this even if it "seems to work."
   - Any path where an unknown/ambiguous classification defaults to cloud
     instead of defaulting to local-with-error/queue.
   - Cloud fallback events that aren't logged or alerted on anywhere.
   - Streaming, batched, or multi-turn requests where sensitivity is only
     checked once and a later chunk/turn/item could take a different path.
3. Rate each finding CRITICAL (active leak path), WARNING (fragile gate that
   will eventually fail), or INFO (hardening suggestion, no current exploit
   path), ordered CRITICAL first.
4. Draft a fail-closed policy config (YAML) that defines my sensitivity
   categories, sets "on local failure" to queue-locally-or-error (never
   cloud) for each sensitive category, and defaults unknown classifications
   to the most restrictive category rather than to cloud.
5. End with one line stating this was a static code review only, and name
   the specific red-team test I should run next (e.g., "kill the local
   process and send a planted sensitive prompt; confirm it queues/errors
   and never reaches the cloud endpoint").

Do not tell me the setup is safe based on a partial description. If you
don't have the actual fallback/timeout code, ask for it first.
```

## What you'll get back

A four-part report:
1. **Scope confirmed** — the local path, cloud path, and current sensitivity mechanism, as understood from what you pasted (or a note that the review is incomplete and what's missing).
2. **Findings** — one entry per issue found: severity, exact location, which of the six failure modes it is, and the scenario that would trigger a real leak.
3. **Draft fail-closed config** — a YAML block you can adapt, binding each sensitivity category to a local-failure behavior and setting a default-deny rule for unknown classifications.
4. **What this review didn't check** — a one-line disclaimer plus the specific red-team test to run next.

## Limits

This is a static read of the code or config you paste — it cannot see logic you didn't include, and it cannot replace actually testing your system under simulated local-inference failure (killing the local process, sending oversized sensitive prompts, sending ambiguously-phrased sensitive content). Treat the report as a pre-deployment checklist, not a certification.
