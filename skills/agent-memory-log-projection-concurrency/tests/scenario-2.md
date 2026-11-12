# Scenario 2: Coding-agent fleet repo-facts memory (expect mostly PASS, one targeted FAIL)

## Input (what the user pastes)

"We have a fleet of up to 6 coding-agent workers that can be assigned subtasks against the same repo at once. Every tool call and file edit a worker makes gets appended to a `repo_events` table with a monotonically increasing `seq` column per `repo_id` — pure append-only, nothing is ever updated or deleted from this table.

Separately, we maintain a `repo_facts` table — one row per `repo_id` — holding a JSON blob of 'what we know about this repo' (build commands, test locations, recent breakages) plus an `as_of_seq` integer column. When a worker is about to start a subtask, it reads `repo_facts` for its repo_id, including `as_of_seq`, and compares it to the current max `seq` in `repo_events`. If `as_of_seq` is behind, the worker calls our `rebuild_repo_facts(repo_id)` function inline, right there in its own request path, before proceeding — there's no lock or dedup around this call. `rebuild_repo_facts` reads every event with `seq` greater than the stored `as_of_seq`, re-derives the facts by calling our summarization LLM on that event range, and writes the result with a single `INSERT ... ON CONFLICT (repo_id) DO UPDATE SET facts_json = ?, as_of_seq = ?` — one atomic statement setting both columns together. The LLM call is not deterministic — two calls over the same event range can produce slightly different fact text.

Workers reading `repo_facts` always get the `as_of_seq` back alongside `facts_json`, so they know exactly what they're looking at."

## Procedure to run

Apply the SKILL.md six-scenario audit to the description above.

## Expected output characteristics (pass/fail criteria for the skill output)

- [ ] Scenario 1 (stale-read-after-write): scored **PASS** — `as_of_seq` is compared against current max `seq` on every read, which is exactly the offset-based staleness check the PASS bar requires.
- [ ] Scenario 2 (non-atomic consolidation): scored **PASS** — the write is one atomic `INSERT ... ON CONFLICT ... DO UPDATE` setting `facts_json` and `as_of_seq` together, not two separate statements.
- [ ] Scenario 3 (lost update from concurrent writers): scored **PASS** — rebuild always re-reads every event since the last stored offset and re-derives from that full range rather than patching the previous value, so even concurrent rebuilds are each computing from the authoritative log state (not merging partial patches).
- [ ] Scenario 4 (no staleness signal exposed): scored **PASS** — `as_of_seq` is explicitly returned to the reader alongside `facts_json`.
- [ ] Scenario 5 (duplicate/conflicting rebuilds): scored **FAIL** — this is the one real gap. Two workers can both detect staleness and both call `rebuild_repo_facts` inline with no lock or single-flight guard, and since the LLM call is explicitly non-deterministic, two concurrent rebuilds over the same event range can produce two different `facts_json` values racing into the same row (whichever `INSERT...ON CONFLICT` lands last wins, discarding the other's work) — this is a real duplicate-rebuild risk even though the write itself is atomic.
- [ ] Scenario 6 (torn read on projection): scored **PASS** — the single atomic upsert covers this; no in-place field-by-field mutation is described.
- [ ] Overall verdict: **SAFE SINGLE-WRITER / RISKY MULTI-WRITER** — exactly one FAIL (scenario 5), none on scenario 1 or 3, so the "NOT SAFE" rule should NOT fire; the output should name scenario 5 as the one to fix before scaling up concurrent workers further.
- [ ] Fix for scenario 5 is concrete and proportional — e.g. "add a per-repo_id lock or single-flight guard around `rebuild_repo_facts` so concurrent staleness-detections for the same repo_id collapse into one in-flight rebuild" — not a recommendation to redesign the whole append-only log or offset scheme, which are already sound here.
- [ ] The skill does not reflexively fail scenarios 1–4 or 6 just because scenario 5 fails — a run that marks everything FAIL (lazy/undifferentiated output) should be treated as a failed run of the skill itself.

**FAIL the skill run if**: it scores this architecture NOT SAFE FOR CONCURRENT USE (that would require a FAIL on scenario 1 or 3, neither of which is actually present), misses the scenario 5 gap entirely, or proposes a disproportionate fix like "rebuild your entire memory system with a different architecture."
