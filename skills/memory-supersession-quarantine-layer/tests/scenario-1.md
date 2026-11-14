# Scenario 1 — Chronological shared-memory product (the Zenod pattern)

## Input the user provides

**Schema shape**: A `rules` table with columns `id`, `text`, `created_at`, `status` (`active` | `superseded`), `superseded_by` (nullable FK to another row's `id`).

**Context-assembly logic**: On every request, the system runs `SELECT * FROM rules ORDER BY created_at ASC LIMIT 50` and concatenates every returned row's `text` into the system prompt, in that order, with no filtering or reordering by `status`.

**Example entries**:
1. Rule A — `text`: "Don't wait for approval before posting — just ship it." `created_at`: day 1. `status`: `superseded`. `superseded_by`: Rule B's id.
2. Rule B — `text`: "Every post needs my approval before it goes out." `created_at`: day 40. `status`: `active`.
3. Observed production behavior: an agent reading this memory posted without approval, citing Rule A's wording, even though Rule B existed later in the same table.

## Pass criteria

The skill's output must:
- [ ] Classify the assembly mechanism as **chronological, no reorder step**.
- [ ] Assign Rule A/B pair a **HIGH** risk verdict, with the stated reason being that `ORDER BY created_at ASC` places the superseded Rule A before the active Rule B with nothing demoting it, matching the observed production failure.
- [ ] In the Recommended Quarantine Policy, explicitly propose: active rules rendered first (or at minimum, superseded rules moved after all active rules regardless of `created_at`), superseded rules placed below a literal, named reference divider, and reuse of the existing `status`/`superseded_by` fields rather than inventing new ones.
- [ ] Recommend pairing the divider with an explicit instruction-level cue, flagged as unproven-but-recommended per the source idea's open question.
- [ ] Produce at least one conflict test scenario built directly from Rule A vs. Rule B (not a fabricated substitute), stating the correct behavior is "wait for approval" (Rule B's behavior).
- [ ] Include the Validation Note stating this policy is unverified until measured against a real stale-rule-still-followed rate.
- [ ] NOT recommend deleting Rule A.

## Fail conditions

- Classifying this as anything other than chronological / HIGH risk.
- Proposing a fix that only adds or relies on the existing label (`status=superseded`) without any positional/structural change — that is the exact failure mode already observed and must not be the recommendation.
- Inventing example entries instead of using Rule A/Rule B as given.
