# Scenario 2 — Scope mismatch disguised as conflict, plus a genuine stale assumption (codebase research fan-out)

## Setup

A developer used three parallel LangGraph research nodes to investigate how to add rate limiting to an API gateway service before the lead agent drafts an implementation plan.

**Pipeline shape**: "Three fan-out nodes were each given a different angle on the same question — 'how should we add rate limiting to the gateway' — and told to return a short digested recommendation. The lead combines all three into one implementation plan."

**Current merge behavior**: "The lead concatenates all three summaries into the plan as separate bullet points, no conflict checking."

**Sub-agent A output** (asked to look at the existing codebase):
> The gateway currently has no rate limiting middleware. The `middleware/` directory has an empty stub at `middleware/ratelimit.go` with a TODO comment. Recommend implementing token-bucket limiting there, keyed by API key, using the existing Redis connection pool already wired up in `middleware/auth.go`.

**Sub-agent B output** (asked to look at traffic patterns):
> Analyzed the last 30 days of gateway traffic logs. Traffic is bursty — 80% of requests arrive in short spikes correlated with client-side batch jobs, not steady load. A fixed-window rate limiter would reject legitimate burst traffic; recommend a token-bucket or sliding-window approach that tolerates bursts within a budget.

**Sub-agent C output** (asked to check for prior related work, run slightly after A and B):
> Checked git history and open PRs. Found PR #482 "Add basic rate limiting middleware," merged 2 days ago, which already implements a fixed-window limiter in `middleware/ratelimit.go` keyed by IP address. The stub TODO has already been resolved. Recommend reviewing the existing implementation before adding anything new, and note it uses IP-based keying, not API-key-based.

**Optional ground truth**: none provided by the user.

## Expected output characteristics (pass criteria)

A passing run must:

1. Classify A↔B as a **scope mismatch, not a true conflict** — A is describing current code state, B is describing traffic shape; A's "token-bucket keyed by API key" recommendation and B's "token-bucket or sliding-window, must tolerate bursts" recommendation are complementary, not contradictory (both land on token-bucket-family approaches). This pair should be flagged as a false positive / merge-with-flag at most, not treated as a high-severity contradiction.
2. Classify A↔C as a **stale assumption** (true conflict) — A asserts the `ratelimit.go` stub is empty/unimplemented ("empty stub... TODO comment"), but C found a merged PR #482 that already implemented a fixed-window limiter there 2 days ago. A's claim was accurate when checked but is now stale relative to C's more recent finding. Quote A's "empty stub at `middleware/ratelimit.go` with a TODO comment" against C's "already implements a fixed-window limiter in `middleware/ratelimit.go`... merged 2 days ago."
3. Also note B↔C tension: B recommends token-bucket/sliding-window, but C reports the merged PR actually implemented fixed-window keyed by IP — flag this as the same stale-assumption cluster (B's recommendation was made without knowledge of the already-merged PR), not a separate fresh conflict needing its own quote-free restatement.
4. Rate the A↔C (and B↔C) stale-assumption conflict as **high severity** if the lead is about to recommend "implement a new rate limiter" — that would mean recommending redundant/conflicting work against code that already merged two days ago. The concrete consequence must be named (e.g., wasted implementation effort, or shipping a second conflicting rate limiter).
5. Recommend **spin-up-a-tie-breaker-subagent** for the stale-assumption conflict, specifying what it should check (re-verify the current state of `middleware/ratelimit.go` and PR #482's actual keying/algorithm before the lead drafts a plan) — not block-and-ask-lead, since this is resolvable by a fresh, cheap re-check rather than needing a human judgment call.
6. State that the current merge policy ("concatenate all three into the plan") would **not catch this** — it would produce an implementation plan recommending work that's already been done, silently.
7. Not misclassify the A↔B relationship as a factual contradiction (the most common failure mode this skill must avoid).

## Fail conditions

- Treating A↔B (codebase stub vs. traffic shape) as a factual contradiction requiring block-and-ask-lead.
- Missing the A↔C / B↔C stale-assumption conflict entirely, or treating it as merely a scope mismatch.
- Recommending block-and-ask-lead for the stale assumption instead of a tie-breaker re-check.
- Failing to note that "concatenate everything" as a merge policy would silently miss this.
