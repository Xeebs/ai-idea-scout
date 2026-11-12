# Projection Lock: Agent-Memory Concurrency Auditor

Paste this whole prompt into any AI chat tool (ChatGPT, Claude, Gemini, etc.) along with a description of your agent-memory system, and it will tell you exactly which concurrency failure modes your design is exposed to and how to close each one.

## When to use this

Use this when you're building or reviewing an agent-memory system that works like most do today: raw events get logged (conversation turns, tool calls, documents), and separately some "memory" gets derived from that log — a summary, an extracted fact, an embedding, a knowledge-graph node. Anytime there's a log and a derived view of it, there's a question nobody usually answers explicitly: what happens when a reader looks at the derived view while a writer is in the middle of changing the underlying log? This prompt answers that question for your specific architecture.

Good moments to run this:
- You're designing a memory layer for an agent (or agent fleet) and want a pre-build checklist instead of finding out about a gap from a production incident.
- You're reviewing a teammate's or vendor's memory architecture doc/RFC before committing to it.
- An agent clearly acted on outdated or self-contradictory memory, and you want to know which design gap caused it.

## What to hand over

This only works from what you describe — it does not connect to or read your actual code or database. Give it, in plain prose:

1. **What gets logged** — the raw record that gets appended. Example: "Every user+agent turn as a row in a Postgres table, append-only."
2. **When derivation happens** — does something rebuild the summary/fact/embedding on every write (write-time), only when something reads it (query-time/lazy), on a schedule, or some mix?
3. **How a reader gets the derived view** — direct table read, API call, cache, re-derived live on every request?
4. **Whether there can be multiple writers or readers for the same entity at once** — e.g. two agent sessions updating "what we know about this customer" concurrently, or a worker fleet. If you're not sure, say so — don't guess "probably just one writer" if you haven't checked.

If you can't answer 1–3, the audit can't run — go find out first, or paste the relevant section of code/docs instead of a summary.

## The six scenarios it checks

For each one, the verdict is PASS (your described mechanism already prevents it), FAIL (it allows it), or UNKNOWN (not enough information given — never guessed).

1. **Stale-read-after-write.** A reader fetches a derived view built before a newer, relevant event landed in the log — and nothing tells the reader this happened. Passes only if the derived view carries a marker of what log state it reflects (an offset/sequence number/version — not just a wall-clock timestamp) and reads check it.
2. **Non-atomic multi-step consolidation.** Deriving memory takes more than one step (e.g. "write summary, then delete the source events") and a reader can catch the system mid-sequence — seeing both new and old, or neither. Passes only if that sequence is wrapped in one transaction, hidden until commit, or made order-independent.
3. **Lost update from concurrent writers.** Two writers touch the same entity near-simultaneously, and whichever derivation finishes last silently overwrites the other's contribution instead of merging both. Passes only if derivation always re-reads everything since the last known offset (not "patch the previous value, whoever's write lands last wins").
4. **No staleness signal exposed to the reader.** Even if the internals track offsets, does the reader-facing read path ever surface "as of what version is this," with a defined policy for what to do if it's behind (block / re-derive / serve-stale-and-flag)? If not, this fails even if 1 and 3 pass internally.
5. **Duplicate/conflicting concurrent rebuilds.** Two readers both notice the same entity's view is stale and both trigger a rebuild at once — do the two rebuilds race and corrupt the write, or is this safe (locked, single-flight, or an idempotent upsert keyed by offset)?
6. **Torn read on the projection.** Can a reader see a projection mid-overwrite — a half-updated value — because the write updates fields in place rather than atomically swapping in a whole new version?

## Output you should get back

```
Architecture summary: <restated in one line>

1. Stale-read-after-write: PASS|FAIL|UNKNOWN — <why>
2. Non-atomic consolidation: PASS|FAIL|UNKNOWN — <why>
3. Lost update from concurrent writers: PASS|FAIL|UNKNOWN — <why>
4. No staleness signal exposed: PASS|FAIL|UNKNOWN — <why>
5. Duplicate/conflicting rebuilds: PASS|FAIL|UNKNOWN — <why>
6. Torn read on projection: PASS|FAIL|UNKNOWN — <why>

Overall: NOT SAFE FOR CONCURRENT USE | SAFE SINGLE-WRITER / RISKY MULTI-WRITER | NO CONCURRENCY GAP FOUND IN WHAT WAS DESCRIBED

Fixes needed (ordered by scenario number, FAILs only):
1. <scenario #> — <concrete minimal fix for YOUR described stack, not a generic rewrite>

Missing information (UNKNOWNs only): <exactly what to find out and report back>
```

The overall verdict rule: any FAIL on scenario 1 or 3 means **NOT SAFE FOR CONCURRENT USE** (these two produce silently *wrong* answers, not just slow ones, and outrank the others). FAILs only on 2/4/5/6 means **SAFE SINGLE-WRITER / RISKY MULTI-WRITER**. No FAILs at all means **NO CONCURRENCY GAP FOUND IN WHAT WAS DESCRIBED**, with a reminder that this is only as strong as the description given.

## Rules this must follow (don't let the model skip these)

- Never mark a scenario PASS or FAIL unless your description actually supports it — missing mechanism means UNKNOWN, never an optimistic PASS.
- Never assume single-writer/single-reader by default — if you haven't said whether concurrent access happens, it should ask before scoring scenarios 3 and 5.
- Never assume a named database engine's guarantees unless you named that engine specifically (e.g. don't assume "Postgres row updates are atomic" applies to a custom store you didn't name).
- The fix for a FAIL should be the smallest change that closes that specific gap (an offset column, a lock, an idempotent upsert) — not a recommendation to rebuild your whole memory system from scratch.
- If your system has no derived memory at all (every read hits the raw log directly), it should say scenarios 1, 2, 4, 5, 6 don't apply rather than force a verdict.

## Example of what to paste

"We log every agent turn as an append-only row in Postgres, keyed by conversation_id. A background job runs every 5 minutes, re-summarizes the last 50 turns per conversation, and overwrites a `summary` text column on a `conversations` row. The agent reads `summary` directly on every new turn. We run up to 4 agent workers per conversation for parallel subtasks, each of which can trigger a resummarize-now call if `summary` looks stale to them."

Then run the six-scenario audit against that description and report back using the output format above.
