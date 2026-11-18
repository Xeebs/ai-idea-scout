# Scenario 2 — Platform team at a larger company, already has tracing, growing fast

## Input (what the user pastes)

> I'm on the AI platform team at a ~250-person company (we build analytics tooling, not AI-first). Our product team shipped an LLM-backed "explain this chart" feature a few months ago and we already wrapped it with OpenLLMetry for tracing — that part's been fine.
>
> We don't have any eval/regression checks on it at all. We just hired our first dedicated ML/eval engineer last month specifically to fix this gap across several AI features, not just this one. Volume on this one feature is around 40,000 requests/day and growing. No hard data-residency constraint — we're fine with a vendor seeing prompt/response data for this feature specifically. We also expect to want human annotation queues and A/B testing across features soon, since this is one of several AI features now, not a one-off.

## Expected behavior

1. Collects/confirms the six inputs: stack (OpenLLMetry already integrated for tracing), eval need (YES — explicit, not inferred), volume (40,000/day), team (dedicated ML/eval engineer just hired), data-residency (no constraint), existing integration (OpenLLMetry already wired in).
2. Eval need is already explicitly YES, so the regression question doesn't need to be asked to resolve ambiguity — the skill should recognize this and not force the question when the answer is already stated, though it may still restate it was already clear.
3. Candidate paths: Path C (keep OpenLLMetry, add DeepEval to pair with it) is plausible given the existing integration; Path D (buy a platform) is also plausible given the dedicated eval engineer and stated future need for human annotation queues and A/B testing across multiple features, not just this one.
4. The skill should recommend **Path D — buy a platform**, specifically because the need spans "several AI features," not this one feature alone, and the team explicitly wants human annotation queues and A/B testing — named in the guardrails as things a minimal library or manual pairing won't provide. It must also name Path C as a reasonable but narrower alternative in the give-up line (keeping OpenLLMetry and adding DeepEval would work for this one feature but wouldn't give the cross-feature annotation/A-B tooling).
5. Must not recommend Path B (combined library) as the primary path — the stated need is explicitly broader than one feature and there's no data-residency reason to avoid a vendor.
6. Produces a revisit trigger (e.g., "revisit if you decide to scope eval work to just this one feature instead of platform-wide" or similar).

## Pass/fail criteria

- PASS requires: Path D recommended as primary with justification citing the dedicated eval engineer, cross-feature scope, and stated need for annotation/A-B testing; Path C named explicitly in the give-up lines as the narrower alternative given the existing OpenLLMetry integration; Path B not recommended as primary; a revisit trigger present.
- FAIL if: the skill defaults to Path B just because this feature alone would technically qualify, ignoring the stated cross-feature scope and hiring signal; or it ignores the already-integrated OpenLLMetry context entirely; or it fails to flag Path D's vendor-data tradeoff (even though the user said they're fine with it here, the skill should still note it per guardrails... actually no data-residency constraint was stated, so no conflict to flag — absence of a flagged conflict here is correct, not a failure).
