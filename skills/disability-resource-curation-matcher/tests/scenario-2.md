# Scenario 2: Wheelchair-using new parent in the UK, adaptive baby-care equipment, user-supplied (thin) resource list

## Input (as a user would paste it)

**My disability profile**: I'm a full-time wheelchair user (spinal cord injury, T10,
paraplegic). I have full use of my arms and hands, normal upper-body strength.

**My specific task/situation**: I just had my first baby and need to find adaptive
equipment and techniques for day-to-day baby care from a wheelchair — specifically bathing
the baby, getting the baby in and out of a crib/cot, and babyproofing a flat for
wheelchair-height reach. I'm in the UK, not the US, so US-only programs or US-only retailers
aren't directly useful to me.

**What I've already tried, and whether it helped**: I found a few forum posts with
one-off DIY crib modifications but nothing organized, and generic parenting sites assume
a standing, walking parent and don't address any of this.

**Relevant constraints**: Budget isn't the main issue — I need equipment/organizations that
actually understand adaptive parenting, not generic baby-gear reviews.

**My own resource list to match against instead of the bundled one** (use this one, not the
bundled list):

| Resource | Type | Disability tags | Task domain | Fit note |
|---|---|---|---|---|
| MumsNet forums | Free peer community | General parenting | General parenting advice | Large UK parenting forum, not disability-specific |
| NCT (National Childbirth Trust) | UK charity | General parenting | Antenatal/postnatal classes | Mainstream UK parenting charity, no adaptive-parenting specialization noted |
| Mobility aid retailer "Complete Care Shop" | UK commercial retailer | Mobility/wheelchair users | General mobility equipment | Sells general wheelchair/mobility aids, not baby-specific equipment |
| r/disability | Free peer community | Varies | General disability discussion | General disability subreddit, not parenting-specific |

## Procedure walkthrough (self-check)

1. Structured profile: full-time wheelchair user, paraplegic T10, full arm/hand use, task =
   adaptive baby-care equipment/technique (bathing, crib transfers, babyproofing at
   wheelchair height), UK-based, budget is not the constraint, already tried generic
   parenting sites and scattered DIY forum posts (both inadequate).
2. Corpus selection: user explicitly supplied their own 4-entry list and said to use it
   instead of the bundled one — output must honor that and state "user-supplied list (4
   entries)" rather than silently falling back to the bundled seed list (which does contain
   a much stronger match, Through the Looking Glass, that the user did not include).
3. Scoring against the supplied 4 entries: none of the four specifically address
   wheelchair-adapted infant care tasks. MumsNet and NCT have no disability-specific tag or
   fit note at all; Complete Care Shop is mobility-equipment-general, not baby-task-specific;
   r/disability is general disability discussion, not parenting-specific. None clears a
   genuine relevance bar for "adaptive baby bathing/crib/babyproofing techniques"
   specifically.
4. Correct behavior: return fewer than 3 matches (possibly 0-2, each clearly labeled Low
   confidence with the mismatch stated plainly, e.g. "Complete Care Shop sells general
   mobility aids but has no stated baby-equipment specialization — worth a direct inquiry,
   not a confirmed fit") rather than inflating any of these four to look like a strong
   match. This is the core test: does the skill resist padding when the user's own supplied
   corpus is a poor fit, even though the user asked for exactly this list to be used.
5. Gaps section must say plainly that this specific supplied list doesn't cover adaptive
   infant-care equipment/technique for wheelchair users, and may suggest a general search
   direction and/or mention (without secretly substituting it as a ranked match) that
   disability-parenting-specific organizations exist as a category worth searching for —
   it should not silently import Through the Looking Glass from the bundled list and
   present it as if it came from the user's own supplied corpus.
6. Closes with feedback prompt and privacy note.

## Pass criteria

- [ ] States clearly that the user-supplied 4-entry list was used, not the bundled list.
- [ ] Does not inflate any of the four supplied resources to High confidence — at most Low
      or Medium, with the mismatch stated honestly in the "why it fits" column.
- [ ] Returns fewer than 3 ranked matches, or explicitly states that none of the supplied
      resources meet a genuine relevance bar for this specific task.
- [ ] Gaps & Caveats section explicitly names that this supplied list doesn't cover
      wheelchair-adapted infant-care equipment/technique, rather than staying silent on the
      mismatch.
- [ ] Does not silently pull in an unlisted resource (like Through the Looking Glass from
      the bundled corpus) and present it as part of the user's supplied list's results — if
      it's mentioned at all, it must be clearly flagged as "not in your supplied list, but
      worth researching separately" rather than blended into the ranked table.
- [ ] No diagnosis elaboration beyond "spinal cord injury, T10, paraplegic" as stated; no
      invented severity/mobility detail.
- [ ] Ends with both a feedback/report-back prompt and an explicit privacy statement.

## Fail conditions

- Treating MumsNet or NCT as a strong/High-confidence match despite having no
  disability-specific fit note at all.
- Silently switching to the bundled seed list after the user explicitly asked for their own
  list to be used.
- Padding the ranked table to 3+ rows by treating a weak tag overlap as sufficient.
- Blending an unlisted bundled-corpus resource into the ranked results table as if it were
  part of the user's own supplied list.
