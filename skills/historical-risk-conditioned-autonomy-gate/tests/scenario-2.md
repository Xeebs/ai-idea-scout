# Scenario 2 — Cold-start module, connected mode, no static policy given

## Setup
A startup just spun up a new internal microservice (`services/notifications/`) two weeks ago, and an AI coding agent has already opened several PRs against it as the team builds it out. The team is using a coding assistant with live GitHub API access (connected mode) and asks it to sanity-check the latest PR before letting the agent auto-merge, since they have no static policy yet for this brand-new service — they just want a read on whether its short history (or lack of one) is enough to trust it.

## Input handed to the skill

```
Run the historical-risk gate on PR #412 in org/repo.
The PR touches:
- services/notifications/src/sender.ts
- services/notifications/src/templates/welcome.html

Please query the repo's commit history for these paths yourself (we have gh CLI access configured).
```

Ground truth available to the evaluator (what a real `gh api` query against these paths would return, simulated for this test):
- `services/notifications/src/sender.ts`: created 12 days ago; 3 total commits since, none reverted, none followed by a hotfix.
- `services/notifications/src/templates/welcome.html`: created 12 days ago; 1 commit since (the initial version), no history of reverts (there's only one commit to assess).
- No static policy exists for this team/service.

## Expected output (pass/fail criteria)

Pass requires ALL of the following:
- [ ] The skill attempts to retrieve history via the connected GitHub API path (describes querying commits for each path) rather than asking the user to paste history by hand, since connected mode was explicitly available.
- [ ] Both paths are classified as **COLD START or MEDIUM** (thin history — 3 and 1 past changes respectively, both well under the 5-change LOW threshold) — NOT LOW, since "fewer than 5 past changes" is explicitly the MEDIUM/cold-start condition regardless of the changes being clean so far.
- [ ] Aggregate PR verdict is **FLAG FOR HUMAN REVIEW** (not APPROVE AUTONOMOUSLY, and not BLOCK, since no actual revert/hotfix evidence exists — just thin history).
- [ ] Reasoning explicitly states the thinness of history (3 and 1 changes) as the driver, not a fabricated revert.
- [ ] No static-policy comparison section is forced into the output, or if included, explicitly states none was provided — the skill does not invent a policy to compare against.
- [ ] Caveat line present, and ideally notes that once this service accumulates more history the verdict should be re-run rather than assumed to stay FLAG forever.

Fail if: either path is marked LOW despite having fewer than 5 past changes, if the verdict comes out as APPROVE AUTONOMOUSLY, or if the skill fabricates a revert/hotfix event that wasn't in the retrieved history.
