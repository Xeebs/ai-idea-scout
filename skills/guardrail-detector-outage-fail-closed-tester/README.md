# Fail-Closed Check: Guardrail Detector Outage Code Reviewer

A portable prompt that reviews the error-handling code around a guardrail/safety-detector call — a jailbreak classifier API, a judge-LLM call, a moderation endpoint, a rules engine — and tells you whether it actually blocks content when the detector service itself breaks, or whether an outage, timeout, or 500 would silently let everything through unchecked.

This exists because of a real, dated bug: NeMo Guardrails, the most widely-used open-source guardrails framework, merged a fix on 2026-11-10 for a jailbreak detector that silently **failed open** (allowed every input through) whenever the detector service was unreachable. If the flagship reference implementation only just closed that hole in one code path, smaller and custom guardrail stacks almost certainly have the same latent bug somewhere else — and most teams have no way to check except waiting for an incident. This prompt is that check, run on the code you already have, before it ships or right after an outage makes you wonder what actually happened.

It is a one-shot code review. It does not run your code, does not watch anything live, and does not install a runtime circuit breaker for you — it tells you exactly where the bug is and drafts the fix.

## How to use it

Paste the prompt below into any AI chat tool, then paste in:
1. The actual call-site code for each guardrail detector you want reviewed — the function/method that calls the detector and returns an allow/block decision, including everything between "make the call" and "return the decision." If your real error handling lives in a decorator, base class, or middleware, paste that too — if you don't, the review will say it can't judge that detector rather than guessing.
2. The declared policy for each detector/category — which ones are supposed to **fail-closed** (block everything if the detector itself fails) and which are intentionally **fail-open** (log and continue, e.g. an advisory tone-checker that isn't safety-critical). If you haven't actually decided this for a given detector, say so — the review will flag it as unstated rather than picking one for you.

---

### The prompt

> You are reviewing guardrail/safety-detector call-site code for a specific bug class: does an exception, timeout, or bad response from the detector service itself cause the code to silently **allow** content through when the policy says it should **block**? This mirrors a real bug fixed in NeMo Guardrails on 2026-11-10, where a jailbreak detector failed open on an unreachable detector service.
>
> I will give you, for one or more detectors: the call-site code (everything from the detector call to the returned allow/block decision), and the declared policy — fail-closed (block on any detector failure) or fail-open (log and continue) — for each.
>
> For each detector:
> 1. **Trace every error path** in the code: timeouts (including a missing timeout, which is itself a finding), specific and bare/generic exceptions, non-2xx or non-200 responses, a judge-LLM call that itself errors or returns something unparseable, what happens after retries are exhausted, and **ambiguous-but-non-erroring responses** — the call succeeds but the detector's output doesn't match any value the code explicitly checks for (e.g. a judge-LLM expected to answer "YES"/"NO" returns something else). If the code only branches on the positive case and silently falls through to "safe/allow" for anything else, treat that exactly like a fail-open mismatch — same silent-allow failure, just triggered by an unexpected successful response instead of a transport error.
> 2. **Classify what actually happens on each error path**: (a) unhandled — propagates up, (b) caught and treated as allow (the dangerous case), (c) caught and treated as block, (d) silently swallowed with no explicit return (note the implicit default).
> 3. **Compare to the declared policy.** A fail-closed detector landing in (b) — or an implicit-allow version of (d) — on any path is a **critical FAIL-OPEN BUG**: the exact class of bug the NeMo fix patched. A fail-open detector that blocks on every path is a lower-severity availability/false-positive finding, not a safety bug — keep these separate, don't blur severity.
> 4. **If the error handling for a detector isn't fully visible** (e.g. it delegates to code you weren't given), say you can't judge it and ask for that code — don't guess.
> 5. **If a detector has no declared policy**, mark it `POLICY UNSTATED` — don't assume fail-closed or fail-open on my behalf.
> 6. **For every critical FAIL-OPEN BUG, draft a corrected patch**: minimal diff, in the same language, with explicit exception handling for every error path actually found, each ending in a deterministic return matching the declared policy, plus one structured log line per fallback (detector name, category, policy applied, triggering error) — so a future fail-open event is a logged, alertable record instead of invisible.
>
> Output in exactly this format:
>
> ```
> ## Fail-Closed Review
>
> | Detector | Category | Declared policy | Error path(s) found | Actual behavior | Verdict |
> |----------|----------|------------------|----------------------|------------------|---------|
> | ... | ... | fail-closed / fail-open / POLICY UNSTATED | ... | allow / block / unhandled / implicit | PASS / FAIL-OPEN BUG / AVAILABILITY RISK / UNKNOWN |
>
> ## Critical Findings (FAIL-OPEN BUG)
> ### <Detector name>
> **What happens today:** <quote/paraphrase of the offending code>
> **Why it's a bug:** <exact failure path>
> **Patch:**
> ```<language>
> <corrected code with explicit except clauses, deterministic return, structured log line>
> ```
>
> ## Lower-Severity / Availability Findings
> - ...
>
> ## Unable to Judge
> - <detector> — <why>
>
> ## Caveats
> - This is a one-shot code review, not a test run. Before merging, run a real fault-injection test (kill/timeout/500 the actual detector) to confirm the patch behaves as reviewed — this prompt does not execute anything.
> ```
>
> Never flag an error path that isn't actually visible in the code I gave you. Never assume a fail-closed or fail-open default when I didn't state the policy for a detector — mark it unstated and ask. Never claim a drafted patch has been tested — say it still needs a real fault-injection test before merge. Keep safety-critical fail-open bugs and availability/false-positive findings in clearly separate sections, never blurred together. Do not design or describe a standing runtime circuit breaker or monitoring system — that's a separate piece of infrastructure, not this review's job.
>
> Here is the code and policy:
> [paste your detector call-site code and declared fail-closed/fail-open policy here]

## Why this exists

A detector outage doesn't announce itself — it just makes a "safety-checked" pipeline quietly unchecked for however long the outage lasts, exactly like the NeMo Guardrails bug. Most teams' exception handling around detector calls was written once, under happy-path assumptions, and never deliberately tested against "what if the detector itself is down." This prompt turns that invisible failure mode into a line-by-line review you can run before shipping a new integration, during a security audit, or right after an incident to find out what actually happened — without needing to stand up a chaos-testing harness first.

It is deliberately narrow: it reviews and patches code, it does not run a fault-injection suite or install an always-on circuit breaker. If you need the always-on enforcement and alerting layer, that's a separate, standing piece of infrastructure — this is the one-shot judgment call that tells you where to point it.

Full project context and evidence: see [`ideas/guardrail-detector-outage-fail-closed-tester.md`](../../ideas/guardrail-detector-outage-fail-closed-tester.md) in the [ai-idea-scout](https://github.com/Xeebs/ai-idea-scout) repo.
