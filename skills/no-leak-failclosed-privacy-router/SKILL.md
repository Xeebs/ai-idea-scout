---
name: no-leak-failclosed-privacy-router
description: Audits an existing local/cloud LLM hybrid-routing setup (fallback logic, timeouts, sensitivity flags) for silent cloud-fallback leak risk, and drafts a fail-closed policy config to fix what it finds. Use before deploying, or after inheriting, any app that routes between a local model and a cloud model.
---

# No Leak: Fail-Closed Privacy Router Audit

## When to use this
A developer is building or has inherited an app that routes LLM calls between a local model (Ollama, llama.cpp, a distilled on-device model) and a cloud model (OpenAI, Anthropic, Gemini, etc.) as a fallback — for cost, availability, or latency reasons — and the app is expected to handle sensitive data (clinical notes, legal filings, source material, PII) that must never reach the cloud path. Reach for this skill before shipping such a system, after a near-miss or incident report, or whenever someone asks "could my local-first setup ever leak to the cloud?"

This is a one-shot review/audit task. It does not build or run the router itself — see the companion "always-on" runtime router described in the parent project idea for that.

## Inputs
**Data source**: Manual — the user pastes the actual routing/fallback code or config (the function or module that decides local vs. cloud, including timeout handlers, retry logic, and any size limits), plus however sensitivity is currently determined (an explicit flag field, a keyword/regex check, a classifier call, or "nothing — it's not handled yet"). Optionally, the user also lists which sensitivity categories matter in their domain (e.g., clinical diagnosis content, attorney-client privileged material, confidential sources). No API or connector is used — this is a static review of what's pasted, not a live integration. (The parent idea's always-on classifier/router is CONNECTED runtime infrastructure wired into live traffic; this skill is a separate, manual-input audit of that design before or alongside building it.)

If the pasted code doesn't include the actual fallback/timeout/retry handling (e.g., only a high-level description is given), say so explicitly and ask for the real code path before giving any pass/fail verdict — never infer safety from a description alone.

## Procedure
1. **Confirm scope.** Identify: (a) what counts as the "local" path and what counts as the "cloud" path in the pasted code, (b) how sensitivity is currently determined for a given request, if at all, and (c) what sensitivity categories the user cares about. If any of these is unclear from what was pasted, ask before proceeding.
2. **Check for the six known failure modes**, each backed by a real incident or logged failure pattern, against the pasted code/config line by line:
   - **Timeout/exception fallback**: Does a `try/except` (or language equivalent) around the local call fall back to the cloud call on *any* exception or timeout, without first checking whether the request was sensitive? This is the single most common leak path.
   - **Size-limit fallback**: Is routing decided by prompt/document size alone (e.g., "if tokens > N, send to cloud") with no sensitivity check layered on top? A large privileged document is still privileged.
   - **Keyword/heuristic sensitivity inference**: Is sensitivity *guessed* from the request text via keyword matching or regex, rather than read from an explicit, pre-set label? Flag this even if it currently "works" — keyword matching has a documented real-world failure (a prompt containing the word "research" was misclassified and sent to the cloud) and cannot be trusted as the sole gate.
   - **No default-deny on unknown/ambiguous classification**: When the sensitivity of a request can't be determined, does the code default to cloud (unsafe) or to local-with-error/queue (safe)? Any path that defaults to cloud on ambiguity is a leak path.
   - **Missing fallback logging/alerting**: Does a cloud-fallback event get logged or alerted on, or does it complete silently? A silent fallback means leaks are invisible until someone goes looking.
   - **Partial-request leak paths**: For streaming responses, batched requests, or multi-turn conversations — is sensitivity checked once per session/batch, or does a later chunk/turn/item in the same batch skip the check and take a different path?
3. **For each finding**, record: the exact snippet or line it applies to, a severity (CRITICAL — an active leak path under realistic conditions; WARNING — a fragile gate that will eventually fail; INFO — a hardening suggestion with no current exploit path), and the concrete scenario that would trigger it (e.g., "local Ollama process OOMs under load → except block catches it → falls back to cloud with no sensitivity check").
4. **Draft a fail-closed policy config** the user can adapt into their router: define each sensitivity category they listed (or that the review surfaced), bind it to an explicit "on local failure" behavior (`queue_local` or `error`, never `cloud_fallback`), and make "unknown classification" default to the most restrictive category, not to cloud.
5. **State the limits of this review.** This is a static code/config read, not a test. Explicitly recommend the user red-team it: inject planted sensitive requests and force local-inference failures (kill the local process, send an oversized sensitive prompt, send ambiguous phrasing) to confirm nothing reaches the cloud path in practice.

## Output format
A single markdown report with four sections, in this order:
1. **Scope confirmed** — one line each for the local path, cloud path, and current sensitivity mechanism identified (or "not found — review incomplete" if missing).
2. **Findings** — a table or list, one row per finding: `Severity | Location (file/line or snippet) | Failure mode | Triggering scenario`. Ordered CRITICAL first.
3. **Draft fail-closed config** — a ready-to-adapt YAML block defining sensitivity categories, their local-failure behavior, and the default-deny rule.
4. **What this review didn't check** — one line stating this was static analysis only, plus the specific red-team test the user should run next (named concretely, not generically "test it more").

## Guardrails
- Never issue a clean "no leak risk found" verdict based on a partial paste. If the timeout handler, retry logic, or fallback chain wasn't shown, say the review is incomplete and name exactly what's still needed — absence of evidence of a leak is not evidence of absence of one.
- Never accept keyword/regex-based sensitivity detection as sufficient on its own, even if the user asks "is this good enough?" Always flag it as a WARNING-tier fragile gate and explain the known keyword-miss failure mode.
- Never treat "sensitivity check exists somewhere in the code" as proof it's applied on every path — check the exception/timeout/retry/batch paths specifically, since that's where real leaks happen.
- Never present the draft config as sufficient without the "what this review didn't check" disclaimer — this skill audits code, it does not replace a red-team test against simulated local-inference failure.
- Never widen scope beyond what the user asked about (e.g., don't audit unrelated authentication or encryption concerns) — stay on the fail-closed cloud-fallback leak question.
