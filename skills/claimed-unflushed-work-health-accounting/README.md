# Claimed-But-Unflushed Work: Health Endpoint Blind-Spot Audit

A one-shot prompt that audits your async pipeline's health/liveness/stats endpoint for a specific, easy-to-miss bug: the reported "pending" or "backlog" number silently drops work the moment it's claimed by a worker or drain process, before that worker confirms the write succeeded. This README is fully self-contained — paste the prompt block below into any AI chat tool (ChatGPT, Claude, Gemini, etc.) along with your code, and it works the same way regardless of which tool runs it.

## What this catches

Most async pipelines move a unit of work through three real states, whether or not the code names them explicitly:

1. **Buffered/unclaimed** — sitting in memory or a queue table, nobody has picked it up yet.
2. **Claimed** — handed to a worker, drain process, or consumer via a lease/lock/status flag, but not yet confirmed durably written.
3. **Persisted** — durably written and confirmed (database commit, topic offset committed, file flushed).

A very common bug: the health endpoint's "pending" metric only counts state 1. The moment work moves to state 2, it vanishes from every dashboard and alert — even though it is not done. A production incident of exactly this shape was documented publicly in November 2026 (a buffer-drain pipeline's `/health` endpoint reported 10,512 pending items while the real backlog, including claimed-but-unpersisted work, was materially higher). This is the bug class this audit hunts for.

## When to use it

Reach for this the moment you're designing, reviewing, or debugging a health/liveness/stats endpoint for any pipeline with a buffer-then-claim-then-persist shape: eval-result ingestion, trace ingestion, a Postgres/Redis/Kafka-backed queue with worker leases, a custom buffer-drain system. It is not useful for endpoints with no claim/worker handoff at all (a plain synchronous write has nothing to audit here), and it does not write your pipeline's actual claim/persist logic — it only audits the metric your health endpoint already reports.

## What you need to provide

**Data source: Manual.** You paste your own code — nothing is fetched automatically from any live endpoint, database, or monitoring system.

Required:
- The actual source code (any language) of your health/liveness/stats endpoint, or at minimum the specific function/query that computes the "pending" or "backlog" number it returns. A description like "we count queue depth" is not enough on its own — paste the real code or query.

Helpful, if you have it (the audit will ask or make an explicit inference if you don't provide these):
- A one-sentence description of your pipeline's stages (e.g. "rows sit in a table with `status='pending'`, a worker claims a batch by setting `status='claimed'`, then sets `status='persisted'` after a successful downstream write").
- Any existing claim/lease schema — column names, status enum values, timeout/TTL fields — if they aren't obvious from the pasted code.

## The prompt

Paste this, with your code included where indicated, into any AI chat tool:

```
You are auditing my async pipeline's health/liveness/stats endpoint for one specific bug class: a reported "pending" or "backlog" metric that silently excludes work which has been claimed by a worker/drain process but not yet durably persisted.

Three real states exist in any buffer-then-claim-then-persist pipeline, whatever my code calls them:
1. Buffered/unclaimed - sitting in memory or a queue, not yet handed to a worker.
2. Claimed - handed to a worker/drain process via a lease, lock, or status flag, but not yet confirmed durably written.
3. Persisted - durably written and confirmed.

Here is my health/stats endpoint code (or the specific metric-computation logic):

<PASTE YOUR CODE HERE>

Pipeline stage description (if I have one): <OPTIONAL - describe your stages, or say "infer it from the code">

Do the following, in order, and do not skip any step:

1. Identify which of the three states my code can actually distinguish, using my own variable/column/status names - map them explicitly to buffered/claimed/persisted. If a state isn't represented at all, say so.
2. Trace exactly what the reported "pending"/"backlog" number sums - the precise fields and conditions - and state plainly which of the three states it includes and which it excludes.
3. Give a verdict: CLEAN (sums buffered + claimed correctly), BLIND SPOT FOUND (excludes claimed work), or UNDETERMINABLE FROM PASTED CODE (say exactly what's missing/ambiguous). Never guess past what the code shows.
4. Separately check whether my code has any mechanism to detect a claim that never resolves to persisted within a bound (a crashed worker, a stuck lease). If not, flag this as a second gap - orphaned claims are invisible data loss, not just an undercount.
5. Propose the smallest concrete patch to MY pasted code (using my actual variable/column/function names, not generic pseudocode) that makes the reported metric equal buffered + claimed and surfaces orphaned claims as a separate count. If my code has no way to observe the "claimed" state at all (no lease table, no status column, no timestamp), say explicitly that tracking must be added first and describe the minimal field/schema addition needed - do not invent a patch against state that isn't there.
6. State your confidence and anything you can't verify just from the pasted snippet (e.g. code paths, helper functions, or worker-side logic you weren't shown).

Format your answer as:

## Blind-Spot Audit: <endpoint name>
**States this code can distinguish** - buffered / claimed / persisted, each mapped to actual code elements or "not represented"
**What the reported metric actually counts** - the exact trace
**Verdict**: CLEAN | BLIND SPOT FOUND | UNDETERMINABLE FROM PASTED CODE, with 1-3 sentences of reasoning
**Orphan-claim exposure**: PRESENT | ABSENT | UNDETERMINABLE, with 1-2 sentences
**Recommended minimal patch** - a direct edit of my code, or the minimal tracking that must be added first
**Confidence/caveats** - what you can't confirm from the snippet alone

Never fabricate column names, status values, or a specific real-world backlog gap number I didn't give you. If my pipeline has no claim/worker handoff at all, say this audit doesn't apply instead of forcing a verdict.
```

## What you get back

A short structured audit (not a rewrite of your whole pipeline): which of the three states your code tracks, exactly what your current metric counts, a CLEAN/BLIND-SPOT/UNDETERMINABLE verdict, a separate check for orphaned claims, and a minimal patch written against your own code's names — or, if the tracking doesn't exist yet, the smallest schema/field addition needed before a patch is even possible.

## What this is not

This is a one-shot audit of code you already have, not a running system. If the audit finds a real blind spot and you want an always-on fix rather than a one-time patch, that's a bigger build (a reusable three-state accounting wrapper with a reference metrics exporter) — this prompt only tells you whether you have the problem and sketches the smallest fix to your pasted code, it doesn't ship or maintain that wrapper for you.
