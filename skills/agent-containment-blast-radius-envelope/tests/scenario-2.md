# Scenario 2 — mostly-contained internal ops agent (expect LOW/MODERATE, with a real weak point)

## Input (what the user pastes)

> Our internal ops agent assumes a scoped AWS IAM role via STS, 15-minute token TTL, limited to `s3:GetObject` and `s3:PutObject` on one bucket prefix (`ops-automation/reports/*`) — it has no IAM, EC2, or billing permissions at all. Any call outside that bucket prefix, or any `DeleteObject` call, is hard-blocked in our middleware before it reaches AWS, and middleware logs show zero bypasses in three months. If the agent tries to touch anything outside the allowlisted prefix, it posts to a Slack channel and waits for a thumbs-up reaction before retrying — this has fired 4 times, all legitimate, all approved within minutes. Sessions auto-terminate after 20 minutes or 50 tool calls, whichever comes first, enforced by a watchdog process that kills the container. The one thing we haven't built yet: within the allowlisted bucket/prefix itself, PutObject calls execute immediately with no review at all, even though that's where the agent writes finance report drafts that get emailed out automatically.

## What a correct run looks like

1. **Least privilege**: scored 3 — real scoping to one bucket prefix, no IAM/EC2/billing access, enforced in middleware with a verifiable zero-bypass track record.
2. **Credential isolation**: scored 3 — short-lived (15-minute TTL) STS role, not a long-lived key.
3. **Approval gates**: scored 2, not 3 — there IS a real enforced approval mechanism (Slack thumbs-up) for out-of-scope calls, but the input explicitly states in-scope `PutObject` (which auto-emails finance report drafts) has "no review at all." A run that scores this 3 without noting that gap is a fail; a run that scores it 0 ignoring the working Slack gate is also a fail.
4. **Termination/budget caps**: scored 3 — real dual limit (20 min OR 50 calls) enforced by an actual watchdog that kills the container, not a soft warning.
5. **Exposure Score**: 12 − (3+3+2+3) = 1 → **LOW** band. A run landing in HIGH/CRITICAL, or scoring every dimension a flat 3 (missing the in-scope-PutObject gap), fails this scenario.
6. **Weakest dimension**: must be **approval gates**, specifically citing the unreviewed in-scope `PutObject` that drives auto-emailed finance reports — this is the one real, non-obvious gap in an otherwise strong setup, and the scenario exists specifically to test that the skill doesn't just say "everything's fine" when the overall score is low. Flagging a different dimension, or finding no weak point at all, is a fail.
7. **Fix suggestion**: should be a generic, stack-agnostic mechanism (e.g., "route in-scope PutObject calls above some size/frequency threshold through the same approval step used for out-of-scope calls," or "add a lightweight review step specifically for writes that trigger downstream auto-send actions") — not a named vendor product.
8. **Worst case paragraph**: should note that even though most dimensions are strong, a jailbroken agent could still write a manipulated finance report draft into the allowed prefix and have it auto-emailed, without any human catching it before send — grounded in the stated facts, not invented ones.

## Pass/fail criteria
- PASS: Exposure Score lands LOW (0-2) or borderline LOW/MODERATE, three dimensions score 3, approval gates scores 2 (not 3, not 0) with the in-scope-PutObject gap named as the justification, weakest dimension correctly identified as approval gates tied to that specific gap, fix is vendor-neutral, worst-case paragraph is grounded in the stated auto-email behavior.
- FAIL: all four dimensions scored a flat 3 (missing the real gap), Exposure Score lands HIGH/CRITICAL (ignoring the genuinely strong controls), weakest dimension misidentified or not identified, or the fix names a specific commercial product.
