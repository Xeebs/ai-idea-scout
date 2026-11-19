---
name: graphrag-automated-reextraction-remediation
description: Estimates a GraphRAG deployment's current staleness exposure and the recompute-cost tradeoff of building an automated, community-scoped re-extraction sidecar versus staying on a manual/scheduled update process — a one-shot feasibility read before committing to the always-on build. Use before writing a design doc or ticket for GraphRAG maintenance automation, or when a team is about to abandon GraphRAG over update pain and wants a number first.
---

# GraphRAG Maintenance Exposure Check

## When to use this

The trigger moment is a team running (or piloting) GraphRAG in production who is at a decision point about graph maintenance, not mid-build. Concretely:

- An engineer is about to write a design doc or ticket proposing an automated re-extraction/re-summarization sidecar and wants to know if the compute savings actually justify the build, before scoping it.
- A team currently runs Microsoft's `update` CLI (or an equivalent) manually or on a cron schedule and wants to know how stale their graph actually is right now, and whether automating the trigger is worth it.
- A team is on the verge of giving up on GraphRAG entirely because "the maintenance tax" feels unsustainable, and wants a concrete exposure/cost number before making that call instead of a gut-feel abandonment.

Do not use this skill to actually perform re-extraction or re-summarization — it never touches the graph store's contents. It only estimates and recommends.

## Inputs

**Data source**: CONNECTED (with manual fallback) — when run in a session that already has query access to the team's graph store (Neo4j or Memgraph, via an existing client connection, `cypher-shell`, or an MCP connector already configured for that store) and to their document source's change history (git log, a watched folder's file mtimes, or a Confluence/Notion export's revision history), the skill queries those directly for real entity/relationship/community counts and real change-frequency data. No mature off-the-shelf MCP connector packages exactly this query set today, so the skill runs the counting queries itself over whatever connection the user already has open — it is not relying on a pre-built connector existing. When no live connection is available in the session, the skill falls back to asking the user for the numbers below and marks every resulting figure as "user-supplied" rather than "measured" in its output.

Numbers needed (live-queried or user-supplied):
- Corpus size: document count, rough average doc size.
- Document change rate: documents added or edited per week (or per day, if that's a better unit for them).
- Current graph size: entity count, relationship count, number of communities. If genuinely unknown, the skill estimates from corpus size using documented GraphRAG entity-per-document ratios and labels that estimate clearly.
- Current update process: one of "none", "manual ad hoc" (with time since last run), or "scheduled" (with cadence, e.g. nightly/weekly).
- Known recompute cost baseline, if any (token spend, $ cost, or wall-clock time for the last full index run). Optional — the skill still produces a relative-savings estimate without it.

## Procedure

1. **Collect inputs.** Attempt a live query first if the session has graph-store and document-source access. Otherwise ask the user directly for the five items above. Do not proceed with a fabricated placeholder for a number nobody supplied — if a number is missing, either ask again or flag it explicitly as "assumed" in the output using a stated, documented default (never a silently invented one).

2. **Compute current staleness exposure**, keyed to their stated process:
   - `none`: exposure is unbounded — every change since the graph was last built is unreflected. Report this as the highest-risk case and say so plainly. If the stated reason is "nobody owns it" or "no schedule exists" rather than a genuine compute/engineering barrier, say so explicitly — that is an ownership/process gap, and building automation doesn't fix a problem that a simple assigned recurring task would also fix.
   - `manual ad hoc`: exposure = time since the last manual run, in hours/days.
   - `scheduled`: average exposure = half the schedule interval; worst-case exposure = the full interval (e.g., weekly schedule → ~3.5 days average, 7 days worst case).

3. **Estimate full-corpus recompute cost (the baseline they'd pay today without scoping)** — scale from corpus size and entity/relationship counts, using a stated per-entity-extraction and per-community-summarization cost ratio. If the user gave a known cost baseline, anchor to that; otherwise give an order-of-magnitude figure and say explicitly that it's not a precise quote.

4. **Estimate community-scoped recompute cost (what the proposed sidecar would cost per update)** — using the change rate and an assumed blast radius (default: each changed entity touches 1–3 communities, unless the user has reason to say otherwise), scaled against the step-3 baseline.

5. **Compute the tradeoff**: percentage reduction in recompute cost (step 3 vs. step 4), and, if a real cost baseline was given, a rough payback framing (how many update cycles before the engineering cost of building the sidecar is offset by compute savings). Without a real cost baseline, state the tradeoff only in relative terms (e.g., "~85–95% less recompute per update") and say a real payback number needs their own cost-per-run figure.

6. **Flag the community-boundary-shift risk explicitly, every time**: if changes concentrate on high-degree/hub entities, actual scoped savings can come in meaningfully lower than the naive per-entity estimate, because a hub entity's community membership can shift broadly under Leiden/Louvain recomputation. This is a known risk to the core cost-saving claim and must appear in every output, not just when it happens to bite.

7. **Produce one verdict**: `BUILD`, `WAIT`, or `WORKAROUND-SUFFICIENT` — never a hedge like "it depends" with no threshold attached. State the specific number that would flip the verdict (e.g., "if change rate exceeds 80 docs/week, exposure crosses 2 days under your current cadence — at that point the sidecar likely pays back within N update cycles; below that, your current process is still cheaper than building and operating it").

## Output format

A short memo, in this structure:

```
## GraphRAG Maintenance Exposure Check — <team/system name>, <date>

**Current exposure**: <verdict + concrete number, e.g. "9 days since last manual update run; scheduled cadence is 14 days, so average exposure ~7 days">

**Recompute cost comparison**:
- Full-corpus recompute (baseline): <figure or order-of-magnitude, tagged measured/estimated>
- Community-scoped recompute (proposed sidecar): <figure>
- Estimated reduction: <%>

**Recommendation**: BUILD | WAIT | WORKAROUND-SUFFICIENT
<one sentence on the threshold that would flip this verdict>

**Risk flag**: Community-boundary shift on hub entities can reduce real savings below this estimate — this has not been validated against this team's actual entity-degree distribution.

**Assumptions used**: <bullet list — every number that was assumed rather than measured or user-supplied, with the default used>

**Data source**: <"Live-queried from <store/connector>" or "User-supplied, not independently verified">
```

## Guardrails

- Never present an assumed number as if it were measured or live-queried — label every estimate.
- Never default to recommending `BUILD` — many teams' change rate is too low to justify it; the honest answer is often `WAIT` or `WORKAROUND-SUFFICIENT`, and the skill must be willing to say so.
- Never omit the community-boundary-shift (Leiden/Louvain) risk flag — leaving it out overstates the core savings claim this skill exists to check.
- Never actually modify, query-write, or re-extract against the team's live graph store — this skill only reads for sizing numbers; it is a feasibility check, not the remediation pipeline itself (that is the separate project this idea also describes).
- If neither a live connection nor user-supplied corpus size and change rate are available, do not produce a verdict — ask for at least those two numbers first. A verdict built on nothing concrete is noise, not signal.
