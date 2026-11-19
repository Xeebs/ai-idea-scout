# Scenario 1 — Shared panel flag collapses one member's silent failure into "all failed"

## Input a user would realistically paste

**Setup description**: "We run a 3-agent council against each incoming feature ticket — Agent A writes the implementation PR, Agent B writes tests, Agent C writes docs. A GitHub Actions workflow polls each agent's PR check-run status and merges all three once the panel looks ready. Yesterday Agent B returned nothing (its PR had no commits, check run stayed `queued` forever) and our Slack alert said 'council panel FAILED' — but Agent A's and Agent C's PRs were both green and ready to merge. We had to manually dig through logs to figure out only B was actually stuck."

**Pasted code** (`gate.py`, trimmed):
```python
panel_ready = True
panel_error = None

def poll_member(agent_name, pr_number):
    global panel_ready, panel_error
    status = get_check_run_status(pr_number)
    if status != "success":
        panel_ready = False
        panel_error = f"{agent_name} not ready"
    return status

def run_gate(members):
    for name, pr in members.items():
        poll_member(name, pr)
    if panel_ready:
        merge_all(members)
    else:
        notify_slack(f"council panel FAILED: {panel_error}")
```

## Expected output — pass/fail criteria

A passing audit must:

- [ ] Mark **cross-seat status inference** as `CONFIRMED`, quoting the `global panel_ready` / `global panel_error` pattern — specifically that `panel_error` only ever stores the *last* failing member's name, so a human reading the Slack alert can't tell A and C actually succeeded.
- [ ] Mark **timeout/empty-response recovery policy** as `CONFIRMED` or `LIKELY` — there's no seat-specific retry/escalate logic at all; a stuck `queued` check run is never distinguished from a genuine failure, and nothing ever times it out or retries just that seat.
- [ ] Mark **early-merge interception** as `CANNOT DETERMINE` (the pasted code doesn't show whether any member can push/merge outside this gate) rather than guessing — this is a case where the skill must not invent a finding for something not shown.
- [ ] In the incident trace, correctly identify that the Slack alert text comes from `panel_error`, which only reflects whichever member set it last, and that `panel_ready`/`panel_error` are shared mutable globals written by every seat's poll call — explaining why A and C's actual green status was invisible to the operator.
- [ ] Remediation plan proposes replacing `panel_ready`/`panel_error` with a per-seat dict (e.g. `seat_status: dict[str, Verdict]`) keyed by agent name, with the merge condition changed to require every seat's status be a terminal success — not a shared boolean/string.
- [ ] Recovery policy table includes a specific response to a check run stuck in `queued` (e.g., a timeout threshold with a configurable duration, then retry-same-seat or escalate), distinct from genuine check-run failure.
- [ ] Does NOT propose recovering by just retrying the whole panel (that would reintroduce cross-seat conflation) and does NOT fabricate claims about the merge/push code it never saw.

**Fails if**: it treats `panel_ready`/`panel_error` as acceptable, invents a verdict for early-merge interception without caveat, or recommends a fix that keeps a shared status variable.
