---
name: guardrail-detector-outage-fail-closed-tester
description: Reviews the exception/timeout/error-handling code around a guardrail detector call (classifier API, judge-LLM call, rules engine) against a declared fail-closed/fail-open policy per category, and flags any path that would silently let unchecked content through if the detector service errors, times out, or returns a non-200. Use when adding a new guardrail integration, auditing an existing one, or after any detector outage/incident to confirm the code actually does what the policy says.
---

# Fail-Closed Check: Guardrail Detector Outage Code Reviewer

## When to use this
Trigger this when someone is adding a new guardrail/safety-detector call to an LLM pipeline (classifier API, judge-LLM call, regex/rules engine, moderation endpoint), auditing an existing integration before a security review, or investigating after a detector outage/incident to find out whether — and where — unchecked content slipped through while the detector was down. The tell is: "does this guardrail actually block things when the detector service itself is broken, or does it just let everything through?"

This is a one-shot code-review judgment on the code as given. It does not run the code, does not monitor anything live, and does not install a runtime circuit breaker — it tells you where the bug is and drafts the fix.

## Inputs
**Data source**: Manual — the user pastes the call-site source code (or a diff) for each guardrail detector integration, showing how the code currently handles a detector-service exception, timeout, or non-200/malformed response. There is no mature connector today that reads "guardrail detector health" directly from an APM/OTel backend, so this stays a paste-in review.

Required for each detector reviewed:
1. **The call-site code** — the actual function/method that invokes the detector (HTTP call, SDK call, subprocess, judge-LLM prompt call) including everything between "make the call" and "return the allow/block decision to the caller."
2. **The declared policy** — for each detector/category, whether it is supposed to be fail-closed (block on any detector failure) or fail-open (log and continue on detector failure), e.g. "jailbreak detector: fail-closed; brand-tone checker: fail-open."

If the policy for a given detector isn't stated, say so explicitly in the output — never assume fail-closed or fail-open on the user's behalf. If fewer than ~15 lines of actual error-handling code are visible (e.g. only the happy-path call is pasted, with error handling living in an unshown wrapper or decorator), say the input is insufficient to judge that detector and ask for the wrapper, rather than guessing what it does.

## Procedure
1. **Inventory detectors and declared policy.** List every detector call site provided, paired with its declared fail-closed/fail-open category. Mark any detector with no stated policy as `POLICY UNSTATED`.
2. **Trace every error path in the call-site code**, for each detector:
   - Timeouts (explicit timeout params, or absence of one — no timeout set is itself a finding).
   - Exceptions: both specific (`ConnectionError`, `TimeoutError`, a client library's own exception types) and generic/bare (`except:` or `except Exception:`).
   - Non-2xx / non-200 HTTP responses, or a judge-LLM call that itself errors or returns unparseable output.
   - Retry exhaustion — what happens after the last retry fails.
   - **Ambiguous-but-non-erroring responses** — the call succeeds (no exception, no error status) but the detector's output doesn't match any value the code explicitly checks for (e.g. a judge-LLM expected to answer "YES"/"NO" returns something else, or a classifier field is missing/null). If the code's conditional only branches on the "positive" case and silently falls through to "safe/allow" for anything else, treat this exactly like a fail-open mismatch for a fail-closed detector — it is the same silent-allow failure mode, just triggered by an unexpected successful response instead of a transport error.
3. **Classify the actual behavior on each error path** as one of: (a) unhandled — propagates/crashes the caller (needs a judgment call on what the caller then does with an exception — note it, don't assume), (b) caught and the function returns/treats it as "allow" (this is the fail-open behavior), (c) caught and the function returns/treats it as "block" (fail-closed behavior), (d) caught and silently swallowed with no explicit return — note the implicit default of whatever the enclosing code does with no return value.
4. **Compare actual behavior to declared policy per path.** A mismatch where a `POLICY: fail-closed` detector has any error path landing in (b) or an implicit-allow case of (d) is the critical bug class — this is exactly the bug class the NeMo Guardrails outage fix (merged 2026-11-10) patched: a detector-unreachable condition silently resolving to "allow." A detector declared `fail-open` that lands in (c) for every path is a lower-severity finding (an availability/false-block risk, not a safety risk) — report it but don't conflate severity.
5. **For every critical mismatch, draft a corrected patch**: minimal diff in the same language, explicit `except` clause(s) covering the paths actually found, each ending in a deterministic return matching the declared policy, plus one structured log line per fallback (detector name, category, which policy applied, and the triggering error) so a fail-open event becomes an alertable log record instead of an invisible pass-through.
6. **List what you couldn't judge** — any detector where policy was unstated, or where the pasted code's error handling is incomplete (e.g., delegates to an unshown base class) — as open items, not silent passes.

## Output format
```
## Fail-Closed Review

| Detector | Category | Declared policy | Error path(s) found | Actual behavior | Verdict |
|----------|----------|------------------|----------------------|------------------|---------|
| <name> | <e.g. jailbreak> | fail-closed / fail-open / POLICY UNSTATED | timeout / exception type / non-200 / retry-exhausted | allow / block / unhandled / implicit | PASS / FAIL-OPEN BUG / AVAILABILITY RISK / UNKNOWN |

## Critical Findings (FAIL-OPEN BUG)
### <Detector name>
**What happens today:** <quote or close paraphrase of the offending code, with line reference if given>
**Why it's a bug:** <exact failure path — e.g. "a bare `except:` catches the client library's TimeoutError and falls through to `return True` (allowed)">
**Patch:**
```<language>
<corrected code, minimal diff, explicit except clauses, deterministic return, structured log line on fallback>
```

## Lower-Severity / Availability Findings
- <fail-open detector that fails closed on every error path, etc.>

## Unable to Judge
- <detector name> — <why: no policy stated / error handling lives in unshown code / insufficient snippet>

## Caveats
- This is a one-shot review of the code as given, not a test run — before merging, run these paths against an actual fault-injection test (kill/timeout/500 the real detector) to confirm the patch behaves as reviewed; this skill does not execute code.
```

## Guardrails
- Never flag an error path that isn't visible in the pasted code — only report what the code actually shows; if error handling clearly lives in a decorator, base class, or middleware that wasn't pasted, list the detector under "Unable to Judge," don't guess its behavior.
- Never assume a default fail-closed or fail-open policy for a detector when the user didn't state one — mark it `POLICY UNSTATED` and ask, don't silently pick one.
- Never claim a drafted patch has been tested or verified — it is a reviewed, drafted fix; say explicitly it still needs to run against a real fault-injection test before merge.
- Never conflate severity: a fail-closed category silently resolving to allow-on-error is a safety bug (critical); a fail-open category always blocking on error is an availability/false-positive issue (lower severity) — report both but never blur the distinction.
- Do not produce or describe an always-on runtime circuit breaker, monitoring dashboard, or alerting pipeline as the deliverable — that is a separate, standing piece of infrastructure (the project this skill is paired with), not a one-shot code review's output.
