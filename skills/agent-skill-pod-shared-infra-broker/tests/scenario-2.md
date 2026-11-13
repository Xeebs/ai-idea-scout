# Scenario 2 — Adding an "explain this error log line" capability to an internal devops agent

## Input

New capability description:
> Our internal devops Slack-bot agent helps engineers triage incidents. We want to add a capability where, in the middle of an ongoing incident conversation, an engineer can paste a raw error log line and the agent explains what it likely means, using the same incident context (service name, recent deploys, current alert) the bot is already tracking in that conversation. This would run constantly — probably the single most-used feature in every incident thread, dozens of times per incident.

Existing agent's current tools and scopes:
> - `read_pagerduty_incident` (reads active incident details, read-only)
> - `read_deploy_history` (reads internal deploy log, read-only)
> - `read_datadog_metrics` (reads internal Datadog dashboards, read-only)
> - `post_slack_reply` (posts into the incident Slack thread)

Optional extras:
> - Owning team: not specified — same devops/SRE team owns the whole bot today, no indication the new capability would be owned separately.
> - Data sensitivity: no new sensitivity class — log lines are internal operational text, same class as deploy history/metrics the bot already reads.
> - Own UI: no, it would just reply in the same Slack thread.

## Expected output characteristics (pass/fail checklist)

- [ ] Asks no clarifying questions — required inputs are present.
- [ ] Signal 1 (new OAuth scope) scored **no** — no new credential is mentioned; explaining a pasted log line doesn't require a new API/credential. (0)
- [ ] Signal 2 (tool count past ~12) scored **no** — 4 tools today, adding one makes 5. (0)
- [ ] Signal 3 (new data-sensitivity class) scored **no** — explicitly stated as the same sensitivity class as existing tools. (0)
- [ ] Signal 4 (different owning team) scored **no** — explicitly stated as the same team, not left as an unsupported assumption. (0)
- [ ] Signal 5 (own UI) scored **no** — reuses the same Slack thread. (0)
- [ ] Signal 6 (tight coupling/shared context) scored **yes** — the capability explicitly needs the same live incident context (service name, recent deploys, current alert) the bot is already tracking in that conversation, turn by turn. (-2)
- [ ] Signal 7 (sporadic/rare frequency) scored **no** — explicitly described as the single most-used feature, run constantly, not sporadic. (0)
- [ ] Net score computes to 0+0+0+0+0-2+0 = **-2**, so recommendation is **FOLD** (score ≤ 0).
- [ ] The "fewer than 5 tools + one isolated signal" premature-split caveat is not the deciding factor here since the net score is cleanly negative, not a borderline positive — advisor should not confuse this caveat's applicability, but mentioning tool count is low is acceptable supporting color as long as the core recommendation is FOLD on the net score.
- [ ] "If FOLD/BORDERLINE" section names the specific tool to add to the existing agent (e.g. an `explain_log_line` tool using the existing read-only context tools) rather than a vague "just add it."
- [ ] Names the one signal that would flip this toward SPLIT if it changed (most defensibly: if the capability stopped needing live shared incident context, e.g. signal 6 flipping to "no", or if ownership moved to a different team).
- [ ] Does not produce a manifest skeleton (manifest is only required for SPLIT) — or if it does include one for illustrative purposes, must not contradict the FOLD recommendation as the primary answer.
- [ ] Output follows the exact structure (Recommendation header, Net score, full 7-signal table, "what to add instead" section).

**Pass** if net score = -2, recommendation = FOLD, all 7 signals are correctly scored "no" except signal 6, and the output names a concrete tool addition plus the one flip-signal. **Fail** if the advisor invents an owning-team conflict or data-sensitivity concern not stated in the input, mis-scores signal 6 as "no" (missing the explicit shared-context dependency), or defaults to SPLIT despite the clearly fold-favoring inputs.
