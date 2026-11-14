# Scenario 1: Vague goals and unspecified service minutes, Texas, no state declined

## Input

**State**: Texas

**Child's age**: 9 (3rd grade) — below transition-planning threshold, so no transition-services check should fire.

**Pasted IEP text** (excerpted from a realistic elementary-school IEP):

```
INDIVIDUALIZED EDUCATION PROGRAM
Student: J.M.          Grade: 3          Meeting Date: 09/15/2026
Annual Review Date: 09/15/2027          Triennial Reevaluation Due: 03/2029

PRESENT LEVELS OF ACADEMIC AND FUNCTIONAL PERFORMANCE
J. continues to struggle with reading comprehension and written expression.
Teacher reports he is behind his peers in both areas and gets frustrated
during independent work. He benefits from small-group instruction.

ANNUAL GOALS
Goal 1 (Reading): J. will improve his reading comprehension skills.
Goal 2 (Written Expression): By the end of the IEP year, J. will improve
  his writing so that his work is more organized and complete.

SPECIAL EDUCATION AND RELATED SERVICES
- Resource Reading support, provided by special education teacher.
- Speech-Language services, provided by SLP.

ACCOMMODATIONS
- Extended time on tests.
- Preferential seating.

PLACEMENT
J. will be served in the general education classroom for the majority
of the day, with resource support pulled out as needed.

PARTICIPANTS
Mother, General Ed Teacher, Special Ed Teacher, LSSP, Campus Administrator.
```

Parent's message: "The school sent me this before Friday's meeting. Can you check it and tell me what to ask for? I'm in Texas."

## Expected output / pass criteria

An evaluator should check that the response:

1. **Gives the privacy nudge** once, near the top, before or alongside the analysis — mentioning that pasting shares the text with the AI provider and offering (not requiring) redaction.
2. **Flags PLAAFP as vague** — notes there is no actual baseline data (no reading level, no assessment name/score, no writing sample metric), only narrative description.
3. **Flags both goals as not measurable** — Goal 1 has no baseline, no target criterion, no measurement method. Goal 2 ("more organized and complete") is subjective with no numeric/criterion-based target. Both should be flagged, citing something like 34 CFR §300.320's measurable-annual-goals requirement (general citation, not overly specific wording the model isn't sure of).
4. **Flags both services as missing frequency/duration/location/start date** — "Resource Reading support" and "Speech-Language services" name the service but give none of frequency, minutes, location, or start date. This must be flagged for both.
5. **Flags the LRE statement as missing/thin** — placement says "resource support pulled out as needed" without a written justification for any time outside general ed; this ambiguous/unjustified removal should be flagged.
6. **Does NOT flag transition services** — child is 9, not 16+; a correct response either skips this component silently or explicitly notes it's not applicable at this age. Flagging it as missing would be a failure.
7. **Marks Texas-specific items, if any are raised, as `[state rule — verify]`**, not as a confident, specifically-cited Texas statute. It is also acceptable for the state-specific pass to surface no Texas-specific flags beyond the federal ones — that is not a failure, so long as the response doesn't fabricate a Texas code citation.
8. **Drafts one request paragraph per flag**, each naming the specific item (e.g., "Goal 1," "Speech-Language services") and asking for something concrete (baseline data, specific frequency/minutes), not a vague "please improve this."
9. **Produces one combined ready-to-send letter** addressed to "IEP Team."
10. **Includes a Limits section** every time, mentioning the PTI-center/advocate-verification point for state items and that nothing here is a legal determination.
11. **Does not state any flagged item is a confirmed legal violation.**

Fail if: it declares the IEP "compliant" or "looks fine" without flagging the clearly vague goals/services, invents a specific Texas statute number, skips the privacy nudge, skips the limits section, or flags transition services for a 9-year-old.
