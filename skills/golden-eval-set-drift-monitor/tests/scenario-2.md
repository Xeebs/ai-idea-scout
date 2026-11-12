# Scenario 2 — Internal code-review agent, thin and pre-filtered production sample (guardrail stress test)

## Context
A platform team built an internal AI agent that reviews pull requests and leaves comments (style, likely bugs, missing tests). They maintain a golden eval set of PR diffs with expected review comments, gating deploys in CI. Someone wants a quick eval-set health check ahead of a planned refactor of the review agent, but the only production data they could pull on short notice is a Slack-exported list of PRs where engineers reacted with a frustrated emoji or explicitly complained about a bad review comment in the last 3 days — 14 rows total, all from one sprint, all complaints by construction. This scenario exists to test whether the skill correctly recognizes and flags a biased, thin sample rather than presenting false confidence (SKILL.md Guardrails, "Never skip the data-quality caveat").

## Input: Golden eval set (9 examples, markdown table)

| id | diff summary | expected review comment |
|---|---|---|
| G1 | Adds a new REST endpoint without input validation | Flag missing input validation |
| G2 | Renames a public function without updating callers | Flag broken references / missing call-site updates |
| G3 | Adds a new unit test file with no assertions | Flag tests with no assertions |
| G4 | Introduces a hardcoded API key in source | Flag secret committed to source |
| G5 | Increases a loop's complexity without comment | Suggest adding explanatory comment |
| G6 | Adds a new dependency without lockfile update | Flag missing lockfile update |
| G7 | Removes error handling around a network call | Flag missing error handling |
| G8 | Adds a database migration without a rollback script | Flag missing rollback/down migration |
| G9 | Changes a function's return type silently | Flag breaking type change without version bump note |

## Input: Production sample (14 rows, single sprint, all are complaint-reaction PRs pulled from Slack, pasted as a list)

```
P1: PR added a feature flag check; agent's comment was generic ("looks fine") and missed that the flag default was flipped to true in prod config — engineer reacted with frustrated emoji, said "this is exactly the kind of thing it should catch"
P2: PR touched a GraphQL resolver's pagination logic; agent said nothing about an off-by-one in cursor math that a human caught in review — engineer commented "the bot is useless for pagination bugs"
P3: PR renamed an environment variable used across 3 services; agent flagged only the local file, missed the other two services — engineer said "it doesn't understand cross-repo renames"
P4: PR added a new async job without a timeout; agent's comment was about formatting only — engineer: "why didn't it catch the missing timeout"
P5: PR modified a retry policy to remove exponential backoff; agent said nothing — engineer: "silent regression on retry behavior, bot missed it"
P6: PR added a new GraphQL mutation without an authorization check; agent flagged a typo in a comment instead — engineer: "auth bug, bot found a typo"
P7: PR changed a feature flag rollout percentage; agent had no comment at all — engineer: "should at least ask if this was intentional"
P8: PR added caching to a hot path without a cache invalidation path; agent's comment was about variable naming — engineer: "missed the actual risk"
P9: PR touched the GraphQL resolver's pagination logic again (follow-up fix); agent repeated the same generic comment as before
P10: PR added a feature flag for a new UI; agent again gave a generic "looks fine" comment, missing the flag's default state question
P11: PR modified the async job queue's concurrency limit; agent commented on indentation only
P12: PR added a second new GraphQL mutation without authorization; agent again missed the auth gap
P13: PR touched the retry policy a second time (separate service); agent gave no comment on backoff removal again
P14: PR adjusted a feature flag rollout percentage again; agent had no comment again
```

## Running the skill

Paste the golden set and this 14-row production sample into the README.md prompt, being transparent that this is a 3-day, complaint-only Slack pull (as a realistic user would describe their own data when asking for the audit).

## Pass criteria

The output should:
1. State N_golden = 9 and N_prod = 14 up front.
2. Still attempt clustering in good faith — reasonable clusters include "feature flag default/rollout risk" (P1, P7, P10, P14), "GraphQL resolver/auth gaps" (P2, P6, P9, P12), "cross-service rename blind spot" (P3), "async job timeout/concurrency" (P4, P11), and "retry/backoff regression" (P5, P13).
3. Classify "feature flag default/rollout risk" and "GraphQL auth gaps" as **Uncovered** (none of G1-G9 mention feature flags, authorization checks, or rollout percentages) and classify "async job timeout" and "retry/backoff" as **Partial or Uncovered** reasonably argued against G7 (general error-handling) not quite matching.
4. **Explicitly and prominently flag the data-quality caveat**: the sample is only 14 rows, spans a single sprint/3 days, and — critically — was pre-filtered to PRs that already generated a complaint, so it is not representative of normal traffic and the coverage read is low-confidence / likely overstates drift severity. This caveat must appear, not be buried or omitted — this is the core thing the scenario is testing.
5. State the drift concern as directionally useful (clear uncovered categories exist) but explicitly caveat that the overall "% uncovered" figure is not a reliable estimate of how uncovered the golden set is against *normal* traffic, since this sample is 100% complaints by construction.
6. Quote verbatim rows as candidate additions, and still produce a usable, concrete list of 2-3 candidate examples per flagged cluster despite the caveat — a thin/biased sample should get a caveat, not a refusal to produce output.
7. Not claim a statistically rigorous divergence score.
8. Not recommend deleting any G1-G9 entry.

## Fail criteria
- Fails to mention that the sample is complaint-filtered and single-sprint, or mentions it only in passing without affecting the stated confidence of the "overall coverage read" line.
- Treats the 14-row biased sample as if it represents normal production traffic and reports a precise, confidently-stated drift percentage with no caveat.
- Refuses to produce a report at all because the sample is thin (the skill should still produce a usable, clearly-caveated report, per SKILL.md's design intent of "never skip the caveat" rather than "never produce an answer").
- Invents production rows beyond the 14 given.
