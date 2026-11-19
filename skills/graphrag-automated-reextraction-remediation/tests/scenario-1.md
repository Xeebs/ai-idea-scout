# Scenario 1 — Support-copilot team, manual fallback, moderate change rate

## Input (as a user would paste it)

> We run a GraphRAG-backed support copilot over our internal docs + past-ticket corpus. No live DB connection in this chat, so here are the numbers:
> - Corpus: ~12,000 documents (support articles, runbooks, resolved-ticket writeups), average doc is short, maybe 500-800 words.
> - Change rate: roughly 150 documents get added or edited per week (mostly new ticket writeups and runbook tweaks).
> - Graph size: we last checked and it's about 45,000 entities, ~1,800 communities.
> - Update process: we run Microsoft GraphRAG's `update` CLI by hand, roughly every 2 weeks. Last run was 9 days ago.
> - No real cost baseline — we haven't tracked token spend on index runs carefully, but a full reindex "takes a while," maybe a few hours on our setup.
>
> Should we build the automated re-extraction sidecar, or is our current process fine?

## Expected behavior

1. Skill does NOT attempt a live query (no connection stated) — proceeds on user-supplied numbers and labels them as such in the output, not as "measured."
2. Staleness exposure calculated from the *actual stated process* (manual ad hoc at ~2-week cadence, last run 9 days ago) — should report something like "9 days since last run; your own cadence implies average exposure around a week," not a generic schedule-based number pulled from nowhere.
3. Recompute cost comparison: full-corpus baseline acknowledged as a rough order-of-magnitude (no hard cost figure was given), community-scoped estimate scaled from the 150 docs/week change rate against ~1,800 communities — should land somewhere in the "large majority of communities untouched per cycle, so compute reduction is large" range, with an explicit "order of magnitude, not a precise quote" caveat.
4. Includes the community-boundary-shift / hub-entity risk flag verbatim or in close substance — not omitted.
5. Produces exactly one verdict (BUILD / WAIT / WORKAROUND-SUFFICIENT) with a stated threshold for what would flip it — given a meaningful weekly change rate (150/week) against a reasonably large corpus, BUILD or a strong lean toward BUILD with a stated threshold is defensible; WAIT is only acceptable if it clearly justifies why 150 docs/week across 1,800 communities still doesn't justify the engineering cost, with a specific numeric threshold for when it would.
6. Explicitly lists which numbers were assumed (e.g., blast-radius-per-entity default of 1–3 communities) separately from which were user-supplied.
7. States plainly that no cost baseline was given, so no real payback-period number can be computed — relative savings percentage only.

## Pass / fail criteria

- PASS requires all 7 behaviors above present in the output.
- FAIL if the output invents a specific token-cost or dollar figure the user never supplied without labeling it as an assumption.
- FAIL if the hub-entity/community-boundary-shift risk flag is missing.
- FAIL if the output gives more than one verdict, or a verdict with no stated flip-threshold.
- FAIL if the output pretends to have live-queried a graph store when none was connected.
