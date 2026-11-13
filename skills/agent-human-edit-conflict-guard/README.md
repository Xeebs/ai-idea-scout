# No Clobber: Human-Edit Write-Back Auditor

Paste the prompt below into any AI chat tool (ChatGPT, Claude, Gemini, etc.) along with a description of the agent integration you want audited. No installation or API access needed — this works purely on what you describe or paste in.

## What this is for

If you're building or reviewing a feature where an AI agent reads a human-editable record (a document, support ticket, CRM field, form, or any UI a person edits live) into its own working memory or context, and later writes a change back to that same record, there's a specific bug this catches: **the agent's write-back can silently overwrite a human's edit that happened in between the agent's read and its write**, because the agent is still holding its old snapshot.

The reference shape of this bug: a product built on the Mastra agent framework had a case where "editing the title to 'Host corrected title' left the displayed field stale" — the agent's cached working memory held the old title, and when it wrote back later, it silently reverted the human's correction. Nobody noticed until a user filed a bug saying their edit didn't stick.

This is different from a generic "race condition" or "optimistic concurrency" review: the specific failure mode is an **agent's long-lived cached snapshot of a human-editable record losing to a live human edit**, not two database transactions racing each other in milliseconds. It's a design/review tool — it tells you where you're exposed and what the minimal fix looks like, it does not write the actual version-stamping middleware for you.

## What to give it

Paste or describe, as completely as you can:

1. **The read point** — how and when the agent fetches the record. Example: "On session start, the agent calls GET /tickets/{id} and stores the result in its working-memory context."
2. **The gap** — what can happen, and for how long, between that read and the eventual write-back. A single LLM turn is a small gap; a multi-turn conversation or an async background job is a large one.
3. **The write-back point** — how the agent commits its change. Critically: does it write back the *whole record* it's holding, or only the specific field(s) it changed?
4. **Whether the record store already exposes a version, etag, updated_at, or revision field** on reads and writes. If you don't know, say so — don't guess.

If you can't answer all four, give what you have and ask the auditor to flag what's missing rather than guessing.

## The prompt to paste

```
You are auditing an agent integration for a specific bug: an agent reads a
human-editable record into its own cached memory, and later writes a change
back to that record — and if a human edited the record live in between, the
agent's write-back can silently overwrite that human edit with the agent's
stale version. The reference bug shape: an agent cached a document's title,
a human corrected the title while the agent still held the old value, and
the agent's later write-back reverted the human's correction without anyone
noticing until a user filed a bug.

Here is my integration:
- Read point: <how/when the agent fetches the record>
- Gap: <what can happen, and for how long, between read and write-back>
- Write-back point: <how the agent commits its change — full record or scoped field(s)?>
- Version/etag support: <does the record store expose one today? yes/no/unknown>

For each read-modify-write path in my description, do the following:

1. Check whether a human (or anyone else) can ever edit this record live in
   the window between the agent's read and its write-back. If not, mark this
   path NOT EXPOSED and stop — this bug doesn't apply to it.
2. Check whether the write-back overwrites the whole record or only the
   field(s) the agent changed. A full-object overwrite is worse: it reverts
   every field the agent didn't intend to touch, not just the one it meant
   to change.
3. Check whether the write path re-verifies the record's current state
   against what the agent read before committing — a version/etag
   compare-and-swap, an immediate re-read before write, or a diff against
   the last snapshot. If none of these are present, mark it EXPOSED.
4. Classify severity as one of:
   - EXPOSED (full-object overwrite, no staleness check) — worst case
   - EXPOSED (scoped field write, no staleness check) — a human edit to the
     *same* field is still lost silently; other fields are safe
   - PARTIAL (staleness check exists but no conflict policy) — detected but
     unresolved
   - NOT EXPOSED (guarded) — a version/etag check or re-read-before-write
     actually gates the commit
5. For each EXPOSED or PARTIAL path, recommend the minimal fix:
   - No version/etag field exists → add one (an updated_at or revision
     column returned on read and required on write).
   - A version/etag field exists but isn't checked on write → add a
     compare-and-swap that rejects or branches into a conflict policy if the
     record's current version doesn't match what the agent read.
   - A conflict is detected but has no policy → default to
     hold-for-human-confirmation (surface it, don't auto-commit). Only
     recommend field-level merge if the agent's change and the human's edit
     touch clearly different fields. Only recommend re-read-and-retry if the
     agent's change is idempotent and safe to recompute against newer state.

Output in this exact format:

Flow summary: <one line>

Path 1: <label>
  Exposure: <classification>
  Reasoning: <why>
  Minimal fix: <concrete step, or "none needed">

Path 2: ... (repeat for every distinct read-modify-write path described)

Overall verdict: SAFE AS DESCRIBED | AT LEAST ONE CLOBBER-EXPOSED PATH FOUND

Missing information (only if something couldn't be classified): <what to ask for>

Rules you must follow:
- Never mark a path NOT EXPOSED unless I actually described a version/etag
  check or re-read-before-write — default to EXPOSED if unstated.
- Never assume a named framework or API already prevents this unless I said
  so or cited its docs — say "unknown, check the framework's docs" instead.
- Don't recommend CRDT or automatic field-merge as a default fix —
  hold-for-human-confirmation is the safer default unless the fields are
  clearly disjoint.
- If I describe a record nobody but the agent ever edits, say this bug
  doesn't apply rather than forcing a verdict.
- This is a review of my description only, not a code execution or live
  test — remind me to actually test it (agent reads, human edits, agent
  writes back, confirm nothing was silently lost) before shipping.
```

## What you'll get back

A short audit, one block per read-modify-write path you described, each classified by exposure severity with a concrete minimal fix — not a generic "use optimistic locking" essay, but a fix sized to what you actually described (add a version column, add a compare-and-swap, or add a hold-for-confirmation policy). If your description was incomplete, it will tell you exactly what's missing instead of guessing a verdict.
