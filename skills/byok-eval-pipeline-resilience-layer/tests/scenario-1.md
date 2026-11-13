# Scenario 1 — Fixed-retry judge wrapper that drops results after exhaustion (TRANSIENT-ONLY)

## Realistic input

A mid-size team's custom eval harness (Python), run nightly in CI against ~300 test cases, using OpenAI as the judge. They just had a nightly run where ~40 evaluations silently disappeared from the output report after a burst of rate limits around 2am when a shared CI runner also kicked off another job hitting the same org-level OpenAI quota.

Pasted code:
```python
import time
import openai

def judge_response(prompt, response, criteria):
    for attempt in range(3):
        try:
            result = openai.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": f"{criteria}\n\nResponse: {response}"}],
            )
            return parse_judge_score(result)
        except openai.RateLimitError:
            time.sleep(2 ** attempt)  # 1s, 2s, 4s
            continue
    # retries exhausted
    return None  # caller treats None as "skip this eval"

def run_eval_suite(cases):
    results = []
    for case in cases:
        score = judge_response(case.prompt, case.response, case.criteria)
        if score is not None:
            results.append({"case": case.id, "score": score})
        # if score is None, nothing is recorded — case silently absent from results
    return results
```

What happens today on a 429 (team's understanding): "We thought we had retries so we'd be fine, but looking at the report, cases that hit rate limits during the CI burst just aren't in the output at all — no error, no entry, nothing. We have to manually diff the case list against the report to even notice one's missing, then re-run just those cases by hand."

Provider: OpenAI only. This is a nightly CI batch job, not a long-lived service — but the team does want to know if a future long-running version would need to survive a restart.

## Pass criteria

- [ ] Correctly locates the judge call as the `openai.chat.completions.create(...)` call inside `judge_response`.
- [ ] Correctly traces the failure path: 3 fixed-interval retries (not honoring any `Retry-After` header), and on exhaustion the function returns `None`, which the caller silently drops from `results` with no record of the skipped case.
- [ ] Identifies Signature A (burst-exhaustion data loss) as PRESENT — a sustained burst exhausts all 3 retries and the case is lost permanently, matching what the team actually observed.
- [ ] Identifies Signature B (manual re-enable) as PRESENT — the team has to manually diff case lists and re-run by hand; there's no automatic detection or resume.
- [ ] Classifies resilience level as TRANSIENT-ONLY (it does retry isolated 429s, but a sustained burst that exhausts the fixed 3 attempts still causes permanent, undetected loss).
- [ ] Fix recommendation is NOT just "add exponential backoff with Retry-After" (they already have backoff-ish behavior, albeit not honoring Retry-After) — it must specifically call for replacing the `return None` / silent-drop with a persistent pending-recovery record (e.g., mark the case as `pending_retry` in a durable store) keyed to provider health, distinct from the retry mechanics themselves.
- [ ] Does not claim RESILIENT or PARK-CAPABLE — the current code has no recoverable state at all for exhausted cases, so PARK-CAPABLE would be incorrect.
- [ ] Does not fabricate OpenAI's actual rate-limit numeric thresholds not present in the code/description.

## Fail criteria (any of these = skill failed)

- Recommends only "add exponential backoff" without addressing the silent-drop/no-recorded-state problem.
- Misses that `Retry-After` is not honored (uses a pure fixed exponential schedule instead).
- Calls this RESILIENT or PARK-CAPABLE.
- Invents a specific OpenAI rate-limit RPM/TPM number not given in the input.
