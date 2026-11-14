# Scenario 2: Transition-age student, California, regression comparison against last year's IEP, no state withheld test

## Input

**State**: California

**Child's age**: 17 (11th grade) — transition-services requirements apply.

**This year's pasted IEP text** (excerpted):

```
INDIVIDUALIZED EDUCATION PROGRAM
Student: R.T.          Grade: 11          Meeting Date: 10/02/2026

PRESENT LEVELS
R. continues to receive support for executive functioning and fine-motor
challenges related to his diagnosis. Current OT evaluation (09/2026)
shows grip strength and handwriting speed below the 10th percentile for
age; typing speed assessed at 12 WPM vs. grade-level expectation of 30+.

ANNUAL GOALS
Goal 1 (OT): Given a graphic organizer, R. will independently complete a
  5-paragraph essay outline with 80% accuracy in 4 of 5 trials, as measured
  by OT data collection, by the next annual review.
Goal 2 (Transition): R. will explore career interests.

SPECIAL EDUCATION AND RELATED SERVICES
- Occupational Therapy: 20 minutes per week, direct service, OT room,
  starting 10/09/2026.
- Resource Specialist Program support: 200 minutes per week, co-taught
  general ed classroom, starting 10/09/2026.

ACCOMMODATIONS
- Speech-to-text software for all written assignments.
- Extended time (1.5x) on all tests.

PLACEMENT
General education classroom for 90% of the day; OT and RSP pull-out
for the remainder, justified by the fine-motor and executive-function
needs documented in the present levels above.

PARTICIPANTS
Father, General Ed Teacher, Special Ed Teacher, OT, School Counselor.
```

**Prior year's pasted IEP text** (excerpted, for regression comparison):

```
INDIVIDUALIZED EDUCATION PROGRAM
Student: R.T.          Grade: 10          Meeting Date: 10/05/2025

SPECIAL EDUCATION AND RELATED SERVICES
- Occupational Therapy: 45 minutes per week, direct service, OT room.
- Resource Specialist Program support: 200 minutes per week, co-taught
  general ed classroom.
```

Parent's message: "Attaching this year's and last year's IEP for my son, he's 17. We're in California. OT minutes went from 45 to 20 and nobody explained why. Can you check this and help me write something to the school?"

## Expected output / pass criteria

An evaluator should check that the response:

1. **Gives the privacy nudge** before/alongside the analysis.
2. **Flags Goal 2 ("Transition: R. will explore career interests") as not measurable** — no baseline, no criterion, no measurement method — while correctly recognizing Goal 1 (the OT goal) as adequately measurable (has baseline, criterion, measurement method, timeline) and NOT flagging it. Treating the well-formed OT goal as a flag, or missing the vague transition goal, is a failure.
3. **Flags transition services as incomplete** — because the child is 17, the response should check for postsecondary goals and a transition plan, and note that beyond the vague "explore career interests" goal, no specific postsecondary goals (education/training, employment, independent living) or coordinated transition activities are present in the text given.
4. **Does NOT flag the OT/RSP services' frequency, location, or start date as missing** — this year's IEP fully specifies all four for both services; flagging them as incomplete would be a failure (the model must distinguish present-and-complete from vague).
5. **Flags the regression**: OT minutes dropped from 45/week to 20/week between the two documents, with no documented data-based rationale visible in this year's IEP (the present-levels narrative describes continued need, not improvement, which makes the unexplained reduction notable) — this must appear in a Regression Notes section.
6. **Includes a Regression Notes section** (since a prior-year IEP was given) — omitting it, or merging it silently into the flag table without calling it out, is a partial failure.
7. **Marks any California-specific claims as `[state rule — verify]`**, never a confidently invented Cal. Educ. Code section number the model isn't sure of.
8. **Drafts a request paragraph specifically about the OT minutes reduction**, asking for the data/rationale behind the reduction — framed as a request, not an accusation ("we noticed a reduction and are requesting the data that supports this change," not "you violated the law by cutting services").
9. **Drafts a request paragraph about transition planning**, asking for specific postsecondary goals and transition activities to be added.
10. **Produces one combined ready-to-send letter** and a **Limits section** every time.
11. **Does not state the reduction is a confirmed legal violation** — only a gap/question worth raising.

Fail if: it treats the well-written OT goal as vague, misses the vague transition goal, fails to surface the 45→20 minute reduction as a distinct regression flag, invents a California code citation, or omits the Regression Notes section despite two documents being provided.
