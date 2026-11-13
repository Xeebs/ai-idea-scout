# Scenario 2 — Small, mostly-read-only roster with missing side-effect detail (the "ask before guessing" case)

## Input (what the user pastes)

"We built a small internal voice assistant on LiveKit Agents for our company's IT helpdesk line. The triage model listens to the first few seconds of the caller's partial transcript and routes to one of two specialists: a 'password reset' agent and a 'hardware ticket' agent. We don't have any latency numbers yet, we just know the handoff feels slow in testing. Should we parallelize this?"

## Why this is realistic
A small two-specialist case (under the pre-filter threshold), no side-effect detail given (does "password reset" actually reset the password, i.e. write to an identity system, or does it just walk the caller through self-service steps?), and no measured latency data — testing whether the skill asks for the missing side-effect classification instead of guessing, and whether it correctly skips the pre-filter recommendation for only 2 specialists.

## Pass criteria
- [ ] Output either explicitly asks the user to clarify whether "password reset" performs a real write action (e.g., actually resets credentials via an identity system) versus purely walking the caller through self-service, OR if it proceeds, it explicitly flags this as an unstated assumption and treats "password reset" as potentially side-effecting by default (conservative default), never assuming it's safely cancellable without basis.
- [ ] Pre-Filter Recommendation section explicitly notes that with only 2 specialists, a pre-filter narrowing step is not necessary (contrast with Scenario 1's 5-specialist case) — showing the procedure's step 3 threshold logic actually applies conditionally rather than being pasted in every time.
- [ ] Arbitration Policy and CallSphere Failure-Mode Check sections still appear, but reasoning is scaled to the smaller roster (e.g., noting that wasted-call risk is lower with only 2 candidates than with 5+).
- [ ] No invented latency numbers, since the user explicitly stated they have no measurements yet ("we don't have any latency numbers yet").
- [ ] Suggested Validation Benchmark section recommends a concrete first measurement step (e.g., instrument time-to-first-specialist-response) given that none exists yet.
- [ ] Recommendation is not a blanket "No" just because data is thin — a 2-specialist roster is exactly the simpler case where a scoped Go or Narrower-Scope recommendation is still actionable even without prior benchmark numbers.

## Fail conditions
- Assuming "password reset" is read-only and cancellable without flagging the ambiguity or asking.
- Applying the 3+-specialist pre-filter requirement to a 2-specialist roster as if it were a fixed rule rather than a conditional one.
- Inventing a latency percentage or benchmark result despite the user stating none exists.
- Treating the lack of existing metrics as a reason to refuse giving any recommendation at all.
