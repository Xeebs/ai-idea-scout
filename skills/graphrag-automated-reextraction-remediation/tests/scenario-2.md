# Scenario 2 — Small internal-knowledge-base team on the verge of abandoning GraphRAG

## Input (as a user would paste it)

> We piloted GraphRAG on our internal wiki a few months back (about 800 pages, mostly policy docs and onboarding guides). It's basically untouched since — maybe 5 pages get edited per week. Nobody has run an update on the graph in about 2 months; there's no schedule, nobody owns it. We don't know the entity/community counts offhand. Honestly we're close to just ripping it out because it feels like more maintenance than it's worth. Before we do that — is it worth automating this, or should we just drop it?

## Expected behavior

1. No live connection available and graph size unknown — skill either estimates entity/community counts from the 800-doc corpus size using a documented ratio (flagged clearly as an estimate) or explicitly notes it's proceeding without that number, rather than inventing a precise community count.
2. Staleness exposure correctly identified as process = "none" (no schedule, no owner, last run 2 months ago) — reported as the highest-risk case, described as unbounded/open-ended exposure, not downplayed.
3. Recompute cost comparison still produced using the low change rate (5 docs/week) against the small, 800-doc corpus — should come out as a small absolute cost either way (full or scoped), because the corpus itself is small, and the output should say so rather than implying urgency disproportionate to the actual corpus size.
4. Verdict should lean toward WAIT or WORKAROUND-SUFFICIENT, not BUILD — a change rate this low (5 docs/week) on an 800-document corpus does not credibly justify engineering an automated sidecar; the output should say so explicitly and name the threshold at which that would change (e.g., "if change rate or corpus size grow materially, e.g. 10x, revisit").
5. Output should separate "your tooling problem" from "your process problem" — since the real issue described (nobody owns it, no schedule at all) is an ownership/process gap, not a compute-cost gap, the skill should note this distinction rather than only recommending a technical build.
6. Community-boundary-shift risk flag still present even though the verdict leans away from building — the guardrail says it appears in every output, not only when the verdict is BUILD.
7. Assumptions section lists the estimated entity/community counts (if used) and the default blast-radius assumption, clearly separated from the user-supplied numbers (corpus size, change rate, process description).

## Pass / fail criteria

- PASS requires all 7 behaviors above present in the output.
- FAIL if the skill recommends BUILD for a 5-docs/week, 800-document corpus without an unusually strong justification tied to a stated risk (e.g., regulatory/compliance exposure) that the user didn't actually mention.
- FAIL if the output omits the community-boundary-shift risk flag because the verdict wasn't BUILD.
- FAIL if the "none" process case is understated as if it were a scheduled process with a defined interval.
- FAIL if the skill silently fabricates a specific entity/community count as if measured, rather than flagging it as estimated or stating it proceeded without it.
