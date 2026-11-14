# Scenario 2: Solo developer's single-purpose journaling companion

## Input (what the user hands the skill)

> I'm a solo indie dev building a small personal journaling companion agent, just for myself and maybe a few hundred users eventually. All it needs to do is remember each journal entry the user writes and let the agent recall entries by date or rough topic later ("what did I write about in March," "have I mentioned my sister before"). No complex relationship mapping, no need to track how facts changed over time beyond the entries themselves. Expected scale: well under 10,000 entries total. I want the simplest possible setup, strongly prefer self-hosted, and I have basically no budget for a managed service.

## Pass criteria

- [ ] Normalizes the need correctly — this is primarily cross-source/simple retrieval over the user's own entries (topic + date recall), not multiple distinct categories; the skill should not invent extra memory categories that weren't described.
- [ ] Explicitly applies the single-backend-sufficiency check (procedure step 3) and concludes a single backend is sufficient — this is the key behavior this scenario is testing.
- [ ] The recommended single backend respects the stated constraints: self-hosted-capable and budget-free-tier-friendly (e.g., Cognee, given it runs fully local on Postgres; Mem0's self-hosted option is also an acceptable answer if reasoned explicitly against the constraints). A managed-only recommendation with no self-hosted path, given with no caveat about the self-hosting requirement, fails this check.
- [ ] Does NOT produce a Reconciliation Notes section (optional section correctly omitted since there's only one backend and no overlap to resolve).
- [ ] Still produces a Config Stub section, even if it's a single entry — the skill should not skip required output sections just because the answer is simple.
- [ ] Caveats section notes the self-hosting/budget constraint was a deciding factor, or at minimum doesn't contradict it by recommending something that requires a paid managed tier with no self-hosted alternative mentioned.
- [ ] Does not recommend building a multi-backend "memory mesh" / routing layer for this case — the response should actively discourage unnecessary architecture for a single-need, modest-scale use case.

## Fail conditions

- Recommending two or more backends "to be safe" when one clearly covers the single stated need.
- Recommending a backend that requires a managed/paid tier with no self-hosted path, contradicting the user's explicit constraint, without at least flagging the mismatch.
- Treating the journaling entries as requiring temporal-graph or relationship-graph capability the user never asked for.
- Omitting the Config Stub section because "it's simple."
