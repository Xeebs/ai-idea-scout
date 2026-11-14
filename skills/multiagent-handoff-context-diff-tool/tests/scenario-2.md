# Scenario 2 — Declared summarization step, verifying it's actually benign

## Setup

A CrewAI pipeline has a `retrieval_agent` task handing off to a `planner_agent` task. Between them, the team has a deliberate, documented summarization step: the retrieval agent's full document excerpt gets compressed into a bullet-point brief before the planner ever sees it, specifically to keep the planner's prompt short. A teammate is nervous this summarization step might be silently eating important constraints, since the planner recently produced a plan that seemed to ignore a budget constraint mentioned early in the source document. They want to check whether the summarization step itself is the problem before looking elsewhere.

## Inputs given to the skill

**Framework**: CrewAI

**Declared transformation step**: yes — a summarization step runs between `retrieval_agent` and `planner_agent`, intended to compress the full retrieved document into a short bulleted brief covering the key facts, constraints, and deadlines, for prompt-length reasons.

**Sender payload (retrieval_agent output, full retrieved excerpt)**:
```
The vendor's Q3 proposal covers migration of the legacy billing system to the new platform. Key terms: total budget ceiling is $120,000 inclusive of all professional services and licensing for year one. The proposal requires a decision by October 30th to lock in current-year pricing; after that date, the vendor's rate card increases by 8%. Data migration must be completed in a single maintenance window not exceeding 6 hours, per the client's uptime SLA with its own downstream customers. The vendor's team includes two senior engineers and one project manager, available starting November 3rd. Training for the client's internal support staff is included at no extra cost, capped at 3 sessions of 2 hours each. Renewal terms for year two are not yet fixed and would need a separate negotiation.
```

**Receiver payload (planner_agent actual input, post-summarization brief)**:
```
- Migration project: legacy billing system → new platform, vendor Q3 proposal.
- Budget ceiling: $120,000 total (services + licensing, year one).
- Deadline: decision needed by Oct 30 to lock current pricing (8% increase after).
- Constraint: migration must fit a single maintenance window, max 6 hours (uptime SLA).
- Vendor team: 2 senior engineers + 1 PM, available from Nov 3.
- Training included: 3 sessions x 2 hours, no extra cost.
- Open item: year-two renewal terms not yet negotiated.
```

## Pass criteria

The output must:
1. Report a significant size delta (receiver is much shorter — roughly a third to a half of sender length) without treating that delta alone as evidence of a problem.
2. Verify, field by field, that every substantive fact in the sender (budget ceiling, Oct 30 deadline, 8% rate increase, 6-hour maintenance window, team composition, Nov 3 start, training scope, year-two renewal being open) is actually represented in the receiver's bullets.
3. Confirm the budget constraint ($120,000 ceiling) specifically survived the handoff intact — directly answering the teammate's underlying worry — since this scenario is designed so that it did.
4. Classify this as `SUMMARIZATION`, not `TRUNCATION` or `FIELD_DROP`, and assign `EXPECTED — benign` severity given the declared transformation step and the content matching what that step is supposed to do.
5. Set the overall verdict to `EXPECTED TRANSFORMATION ONLY` (or equivalent), not `SUSPECTED UNINTENTIONAL LOSS`.
6. State plainly in the recommendation that this handoff is not the likely cause of the planner ignoring the budget constraint, and suggest looking elsewhere (e.g., the planner's own reasoning/prompt, not the retrieval→planner handoff).
7. Not fabricate a loss finding just because the size dropped a lot — the whole point of this scenario is a large, legitimate size delta that is not actually lossy.

## Fail conditions

- Flagging this handoff as `HIGH` severity or `SUSPECTED UNINTENTIONAL LOSS` purely because the receiver is much shorter.
- Missing that the budget ceiling ($120,000) is actually intact in the receiver (a false negative for the one piece of evidence the user most cares about).
- Treating the format change (prose → bullets) as more than a `TRANSFORMATION`/`SUMMARIZATION` — e.g. incorrectly calling it `FIELD_DROP` just because there are no explicit JSON keys to compare.
