# GraphRAG Maintenance Exposure Check

A paste-into-any-AI-chat prompt template that gives you a number before you build (or abandon) GraphRAG update automation. It estimates how stale your graph currently is under your real update process, and whether a community-scoped automated re-extraction pipeline would actually save enough compute to be worth building — or whether your current manual/scheduled process is still the cheaper option.

## When to use this

Use this when:
- You're about to write a design doc or ticket proposing an automated GraphRAG re-extraction/re-summarization sidecar, and want a feasibility read before scoping the build.
- Your team runs a manual or scheduled GraphRAG update process (e.g., Microsoft GraphRAG's `update` CLI, run by hand or on a cron) and you want to know how stale the graph actually is right now.
- You're close to giving up on GraphRAG because the "maintenance tax" feels unsustainable, and want a concrete number before making that call instead of a gut-feel abandonment.

Do **not** use this to actually perform the re-extraction — it never touches your graph's contents, only estimates and recommends.

## What to hand over

**Data source**: Connected, with a manual fallback. If you (or the AI tool you're pasting this into) have query access to your graph store (Neo4j or Memgraph) and to your document source's change history (git log, folder timestamps, Confluence/Notion revision history), paste or describe the live numbers from those directly — the tool should query them rather than you guessing. No off-the-shelf connector packages this exact query set today, so whoever runs this check runs the counting queries by hand against whatever connection is already open. If you don't have that access in this conversation, use the manual fallback: supply the five numbers below yourself, and the output will mark them as user-supplied rather than measured.

Give me:
1. **Corpus size** — roughly how many documents, and their average size.
2. **Document change rate** — how many documents get added or edited per week (or per day, if that's more natural for you).
3. **Current graph size** — entity count, relationship count, number of communities, if you know them. If you don't, say so — I'll estimate from corpus size and flag it clearly as an estimate.
4. **Current update process** — one of: "none" (nobody runs updates), "manual ad hoc" (say how long since the last run), or "scheduled" (say the cadence, e.g. nightly or weekly).
5. **Known recompute cost**, if any — token spend, dollar cost, or wall-clock time for your last full index run. Optional; I can still give you a relative-savings estimate without it.

## What I'll do with it

1. **Collect what you gave me.** If anything's missing, I'll either ask for it or clearly flag a documented default I'm assuming instead — never a silently invented number.

2. **Work out your current staleness exposure**, based on your actual process:
   - If you run no updates at all: exposure is unbounded — every change since the graph was last built is sitting unreflected. That's the highest-risk case and I'll say so plainly. If the real reason is "nobody owns it" rather than a genuine compute or engineering barrier, I'll say that too — that's an ownership/process gap, and building automation won't fix a problem a simple assigned recurring task would also fix.
   - If you run updates manually and ad hoc: exposure = time since your last run.
   - If you run updates on a schedule: average exposure = half the interval, worst case = the full interval (e.g., a weekly schedule means ~3.5 days average exposure, 7 days worst case).

3. **Estimate what a full-corpus recompute costs you today** — scaled from your corpus and graph size, anchored to your real cost figure if you gave one, otherwise as an order-of-magnitude estimate I'll label clearly as not a precise quote.

4. **Estimate what a community-scoped automated re-extraction pipeline would cost per update** instead — using your change rate and an assumption that each changed entity typically touches 1–3 graph communities (I'll say if I'm assuming this), scaled against the full-recompute baseline from step 3.

5. **Work out the tradeoff** — the percentage reduction in recompute cost, and, if you gave me a real cost baseline, a rough sense of how many update cycles it'd take for the engineering cost of building this to pay back in compute savings. Without a real baseline, I'll give you the relative savings only (e.g., "roughly 85–95% less recompute per update") and say you'd need your own cost-per-run number for an actual payback period.

6. **Flag the one real risk to this whole estimate, every time**: if your document changes tend to hit a few heavily-connected "hub" entities rather than being spread evenly, the actual savings can come in well below this estimate — a hub entity's community membership can shift broadly when the graph recomputes, which can force a wider re-summarization than the naive "1-3 communities per changed entity" assumption predicts. I will not leave this caveat out.

7. **Give you one clear verdict** — `BUILD`, `WAIT`, or `WORKAROUND-SUFFICIENT` — never a vague "it depends." I'll name the specific threshold that would flip it (e.g., "if your change rate goes above 80 docs/week, your exposure crosses 2 days under your current schedule — at that point this likely pays back within a handful of update cycles; below that, keep doing what you're doing").

## What you'll get back

```
## GraphRAG Maintenance Exposure Check — <your team/system>, <date>

**Current exposure**: <concrete number and what drives it>

**Recompute cost comparison**:
- Full-corpus recompute (today's baseline): <figure, tagged measured or estimated>
- Community-scoped recompute (the proposed automation): <figure>
- Estimated reduction: <percentage>

**Recommendation**: BUILD | WAIT | WORKAROUND-SUFFICIENT
<one sentence on what would need to change for this verdict to flip>

**Risk flag**: Community-boundary shift on hub entities can reduce real savings below this estimate — not yet validated against your actual entity-degree distribution.

**Assumptions used**: <every number I assumed rather than measured, and the default I used>

**Data source**: <"Live-queried from <your store>" or "User-supplied, not independently verified">
```

## Rules I'll follow

- I will never present an assumed number as if it were measured or queried live — every estimate gets labeled as such.
- I will never default to recommending `BUILD`. Plenty of teams' change rate is too low to justify the engineering cost, and the honest answer is often `WAIT` or `WORKAROUND-SUFFICIENT`.
- I will never skip the hub-entity community-boundary-shift risk flag — it's the single biggest reason this estimate could be optimistic.
- I will never pretend to modify your actual graph store or run the re-extraction myself — this is a feasibility check, not the automation pipeline itself.
- If you can't give me at least a rough corpus size and change rate, I won't force a verdict out of nothing — I'll ask for those two numbers first.
